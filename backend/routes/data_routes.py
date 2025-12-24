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
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext == '.csv':
            df = pd.read_csv(filepath)
        elif file_ext in ['.xls', '.xlsx']:
            df = pd.read_excel(filepath, engine='openpyxl' if file_ext == '.xlsx' else None)
        else:
            return jsonify({'success': False, 'error': 'Unsupported file format'}), 400
        
        original_len = len(df)
        columns = df.columns.tolist()
        
        time_col, val_col, series_col, label_col = None, None, None, None
        for col in columns:
            if col == '' or str(col).startswith('Unnamed'): continue
            if time_col is None:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    time_col = col
                elif df[col].dtype == 'object':
                    try:
                        pd.to_datetime(df[col].dropna().head(5), errors='raise')
                        time_col = col
                    except: pass
            if pd.api.types.is_numeric_dtype(df[col]):
                if val_col is None: val_col = col
            elif df[col].dtype == 'object' and col != time_col:
                if df[col].nunique() <= 10 and series_col is None: series_col = col
                elif label_col is None: label_col = col
        
        if val_col is None and len(columns) >= 2:
            for col in columns:
                if col != time_col and not str(col).startswith('Unnamed'):
                    val_col = col
                    break
        if val_col is None and len(columns) >= 1: val_col = columns[-1]
        
        if val_col is None:
            return jsonify({'success': False, 'error': 'No numeric value column found'}), 400
            
        df[val_col] = pd.to_numeric(df[val_col], errors='coerce').fillna(0.0)
        
        MAX_ROWS = 10000
        downsampled = False
        if original_len > MAX_ROWS:
            try:
                indices = M4Downsampler().downsample(np.arange(original_len, dtype=np.float64), df[val_col].values.astype(np.float64), n_out=MAX_ROWS)
                df = df.iloc[indices].reset_index(drop=True)
                downsampled = True
            except:
                df = df.iloc[::(original_len // MAX_ROWS)].reset_index(drop=True)
                downsampled = True
        
        data = []
        series_set = set()
        for idx, row in df.iterrows():
            val_value = float(row[val_col])
            series_value = str(row[series_col]) if series_col and pd.notna(row[series_col]) else (val_col or 'value')
            series_set.add(series_value)
            label_value = str(row[label_col]) if label_col and pd.notna(row[label_col]) else ''
            
            data.append({
                'idx': idx,
                'time': idx,
                'val': val_value,
                'series': series_value,
                'label': label_value
            })
        
        return jsonify({
            'success': True,
            'filename': filename,
            'columns': columns,
            'data': data,
            'seriesList': list(series_set),
            'labelList': [],
            'useIndexMode': True,
            'originalLength': original_len,
            'downsampled': downsampled,
            'detectedColumns': {'time': time_col, 'value': val_col, 'series': series_col, 'label': label_col}
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
