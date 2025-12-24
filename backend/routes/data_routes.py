import os
import pandas as pd
import numpy as np
from flask import Blueprint, jsonify, request
from tsdownsample import M4Downsampler
from auth import login_required
from config import DATA_DIR, ANNOTATIONS_DIR

data_bp = Blueprint('data', __name__)

@data_bp.route('/api/set-path', methods=['POST'])
@login_required
def set_data_path(current_user):
    """Set custom data directory path for current user"""
    try:
        from auth import load_users, save_users
        
        data = request.get_json()
        path = data.get('path', '')
        
        if path and os.path.isdir(path):
            users = load_users()
            if current_user in users:
                users[current_user]['data_path'] = path
                save_users(users)
            return jsonify({'success': True, 'path': path})
        else:
            return jsonify({'success': False, 'error': 'Invalid directory path'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@data_bp.route('/api/current-path', methods=['GET'])
@login_required
def get_current_path(current_user):
    """Get current data directory path for current user"""
    try:
        from auth import load_users
        users = load_users()
        user_path = users.get(current_user, {}).get('data_path', DATA_DIR)
        return jsonify({'success': True, 'path': user_path})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@data_bp.route('/api/browse-dir', methods=['GET'])
def browse_directory():
    """Browse server directory structure"""
    try:
        path = request.args.get('path', '/home')
        if not os.path.exists(path):
            return jsonify({'success': False, 'error': 'Path does not exist'}), 404
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        
        path = os.path.abspath(path)
        parent_path = os.path.dirname(path)
        
        directories = []
        try:
            for item in sorted(os.listdir(path)):
                item_path = os.path.join(path, item)
                try:
                    if os.path.isdir(item_path):
                        has_data_files = any(f.endswith(('.csv', '.xls', '.xlsx')) for f in os.listdir(item_path))
                        directories.append({
                            'name': item,
                            'path': item_path,
                            'is_dir': True,
                            'has_data_files': has_data_files
                        })
                except PermissionError:
                    continue
        except PermissionError:
            return jsonify({'success': False, 'error': 'Permission denied'}), 403
        
        current_has_data = any(f.endswith(('.csv', '.xls', '.xlsx')) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)))
        
        return jsonify({
            'success': True,
            'current_path': path,
            'parent_path': parent_path if parent_path != path else None,
            'directories': directories,
            'has_data_files': current_has_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@data_bp.route('/api/files', methods=['GET'])
@login_required
def get_files(current_user):
    """Get all CSV and Excel files in current user's directory"""
    try:
        from auth import load_users
        import json
        
        users = load_users()
        user_path = users.get(current_user, {}).get('data_path', DATA_DIR)
        
        if not os.path.exists(user_path):
            return jsonify({'success': False, 'error': 'Path does not exist'}), 404
        
        files = []
        for f in os.listdir(user_path):
            full_path = os.path.join(user_path, f)
            if os.path.isfile(full_path) and f.endswith(('.csv', '.xls', '.xlsx')):
                user_ann_dir = os.path.join(ANNOTATIONS_DIR, current_user)
                annotation_file = None
                annotation_count = 0
                has_annotations = False
                
                # Check for annotations
                patterns = [
                    os.path.join(user_ann_dir, f"{f}.json"),
                    os.path.join(user_ann_dir, f"annotations_数据集{f.replace('.csv', '')}.json"),
                    os.path.join(user_ann_dir, f"annotations_{f.replace('.csv', '')}.json")
                ]
                
                for pattern in patterns:
                    if os.path.exists(pattern):
                        annotation_file = pattern
                        break
                
                if annotation_file:
                    try:
                        with open(annotation_file, 'r', encoding='utf-8') as af:
                            ann_data = json.load(af)
                            annotations = ann_data.get('annotations', [])
                            if annotations:
                                has_annotations = True
                            annotation_count = len([ann for ann in annotations if ann.get('segments')])
                    except:
                        pass
                
                files.append({
                    'name': f,
                    'has_annotations': has_annotations,
                    'annotation_count': annotation_count
                })
        
        return jsonify({'success': True, 'files': files, 'path': user_path})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@data_bp.route('/api/data/<filename>', methods=['GET'])
@login_required
def get_data(filename, current_user):
    """Read CSV or Excel file data with smart column detection and M4 downsampling"""
    try:
        from auth import load_users
        users = load_users()
        user_path = users.get(current_user, {}).get('data_path', DATA_DIR)
        filepath = os.path.join(user_path, filename)
        
        # Support custom downsampling limit from query params
        try:
            max_rows = int(request.args.get('limit', 10000))
        except (ValueError, TypeError):
            max_rows = 10000
            
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext == '.csv':
            df = pd.read_csv(filepath)
        elif file_ext in ['.xls', '.xlsx']:
            df = pd.read_excel(filepath, engine='openpyxl' if file_ext == '.xlsx' else None)
        else:
            return jsonify({'success': False, 'error': 'Unsupported file format'}), 400
        
        if df.empty:
            return jsonify({'success': False, 'error': 'File is empty'}), 400

        original_len = len(df)
        columns = df.columns.tolist()
        
        # ============ Smart Column Detection ============
        time_col, val_col, series_col, label_col = None, None, None, None
        
        # Sort columns to prioritize certain names
        priority_cols = ['time', 'date', 'value', 'val', 'series', 'label']
        sorted_cols = sorted(columns, key=lambda c: next((i for i, p in enumerate(priority_cols) if p in str(c).lower()), len(priority_cols)))

        for col in sorted_cols:
            if not str(col) or str(col).startswith('Unnamed'): continue
            
            col_lower = str(col).lower()
            # Time detection
            if time_col is None and any(p in col_lower for p in ['time', 'date', '时间', '日期']):
                time_col = col
            # Value detection
            if val_col is None and (pd.api.types.is_numeric_dtype(df[col]) or any(p in col_lower for p in ['val', 'value', '数值', '值'])):
                val_col = col
            # Series detection
            if series_col is None and any(p in col_lower for p in ['series', 'category', '序列', '类型']):
                series_col = col
            # Label detection
            if label_col is None and any(p in col_lower for p in ['label', 'annotation', '标签', '标注']):
                label_col = col
        
        # Robust fallback for value column
        if val_col is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                val_col = numeric_cols[0]
            elif len(columns) > 0:
                val_col = columns[-1]
        
        if val_col is None:
            return jsonify({'success': False, 'error': 'No suitable value column found'}), 400
            
        # Clean value data
        df[val_col] = pd.to_numeric(df[val_col], errors='coerce').fillna(0.0)
        
        # ============ M4 Downsampling ============
        downsampled = False
        if original_len > max_rows:
            try:
                # Ensure we have numeric index for downsampling
                y_values = df[val_col].values.astype(np.float64)
                x_values = np.arange(len(y_values), dtype=np.float64)
                
                indices = M4Downsampler().downsample(x_values, y_values, n_out=max_rows)
                # Ensure indices are within bounds and sorted
                indices = np.sort(indices)
                df = df.iloc[indices].copy()
                downsampled = True
            except Exception as e:
                print(f"Downsampling error: {e}")
                step = max(1, original_len // max_rows)
                df = df.iloc[::step].copy()
                downsampled = True
        
        # ============ Response Data Construction ============
        series_set = set()
        # Optimization: use to_dict for faster conversion if possible, 
        # but manual loop allows fine-grained control over naming
        res_data = []
        for idx, row in df.iterrows():
            s_val = str(row[series_col]) if series_col and pd.notna(row[series_col]) else (val_col or 'value')
            series_set.add(s_val)
            
            res_data.append({
                'idx': int(idx),
                'time': int(idx), # D3 uses this for X-axis
                'val': float(row[val_col]),
                'series': s_val,
                'label': str(row[label_col]) if label_col and pd.notna(row[label_col]) else ''
            })
        
        return jsonify({
            'success': True,
            'filename': filename,
            'columns': columns,
            'data': res_data,
            'seriesList': list(series_set),
            'labelList': [],
            'useIndexMode': True,
            'originalLength': original_len,
            'downsampled': downsampled,
            'count': len(res_data),
            'detectedColumns': {
                'time': str(time_col) if time_col else None,
                'value': str(val_col) if val_col else None,
                'series': str(series_col) if series_col else None,
                'label': str(label_col) if label_col else None
            }
        })
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
