import os
import json
import time
from datetime import datetime

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas as pd
from pathlib import Path

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
CORS(app)

# Configuration directories
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')
ANNOTATIONS_DIR = os.path.join(BASE_DIR, 'annotations')
LABELS_FILE = os.path.join(BASE_DIR, 'config', 'labels.json')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ANNOTATIONS_DIR, exist_ok=True)

# Current working data path
CURRENT_DATA_PATH = DATA_DIR


# ==================== Static Files ====================
@app.route('/')
def index():
    """Serve the frontend"""
    return send_from_directory(app.static_folder, 'index.html')


# ==================== Path Management ====================
@app.route('/api/set-path', methods=['POST'])
def set_data_path():
    """Set custom data directory path"""
    global CURRENT_DATA_PATH
    try:
        data = request.get_json()
        path = data.get('path', '')
        
        if path and os.path.isdir(path):
            CURRENT_DATA_PATH = path
            return jsonify({'success': True, 'path': CURRENT_DATA_PATH})
        else:
            return jsonify({'success': False, 'error': 'Invalid directory path'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/current-path', methods=['GET'])
def get_current_path():
    """Get current data directory path"""
    return jsonify({'success': True, 'path': CURRENT_DATA_PATH})


@app.route('/api/browse-dir', methods=['GET'])
def browse_directory():
    """Browse server directory structure"""
    try:
        path = request.args.get('path', os.path.expanduser('~'))
        
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
                        has_data_files = False
                        try:
                            for f in os.listdir(item_path):
                                if f.endswith(('.csv', '.xls', '.xlsx')):
                                    has_data_files = True
                                    break
                        except PermissionError:
                            pass
                        
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
        
        current_has_data = any(
            f.endswith(('.csv', '.xls', '.xlsx')) 
            for f in os.listdir(path) 
            if os.path.isfile(os.path.join(path, f))
        )
        
        return jsonify({
            'success': True,
            'current_path': path,
            'parent_path': parent_path if parent_path != path else None,
            'directories': directories,
            'has_data_files': current_has_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== File Management ====================
@app.route('/api/files', methods=['GET'])
def get_files():
    """Get all CSV and Excel files in current directory"""
    try:
        files = []
        for f in os.listdir(CURRENT_DATA_PATH):
            if f.endswith(('.csv', '.xls', '.xlsx')):
                annotation_file = os.path.join(ANNOTATIONS_DIR, f"{f}.json")
                has_annotations = False
                annotation_count = 0
                
                if os.path.exists(annotation_file):
                    try:
                        with open(annotation_file, 'r', encoding='utf-8') as af:
                            ann_data = json.load(af)
                            annotations = ann_data.get('annotations', [])
                            if annotations:
                                has_annotations = True
                                annotation_count = len(annotations)
                    except:
                        pass
                
                files.append({
                    'name': f,
                    'has_annotations': has_annotations,
                    'annotation_count': annotation_count
                })
        
        return jsonify({
            'success': True,
            'files': files,
            'path': CURRENT_DATA_PATH
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/data/<filename>', methods=['GET'])
def get_data(filename):
    """Read CSV or Excel file data with improved column detection and NaN handling"""
    try:
        filepath = os.path.join(CURRENT_DATA_PATH, filename)
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext == '.csv':
            df = pd.read_csv(filepath)
        elif file_ext in ['.xls', '.xlsx']:
            df = pd.read_excel(filepath, engine='openpyxl' if file_ext == '.xlsx' else None)
        else:
            return jsonify({'success': False, 'error': 'Unsupported file format'}), 400
        
        # Replace NaN with None for JSON compatibility
        df = df.where(pd.notna(df), None)
        
        columns = df.columns.tolist()
        
        # Auto-detect time column (check multiple common names)
        time_col = None
        time_candidates = ['time', 'timestamp', 'datetime', 'date', '时间', '日期']
        for col in columns:
            if col.lower() in time_candidates:
                time_col = col
                break
        
        # Auto-detect value column
        val_col = None
        val_candidates = ['value', 'val', 'values', '值', '数值']
        for col in columns:
            if col.lower() in val_candidates:
                val_col = col
                break
        
        # Auto-detect series column
        series_col = None
        series_candidates = ['series', 'channel', '序列', '通道', 'category']
        for col in columns:
            if col.lower() in series_candidates:
                series_col = col
                break
        
        # Auto-detect label column
        label_col = None
        label_candidates = ['label', 'labels', '标签']
        for col in columns:
            if col.lower() in label_candidates:
                label_col = col
                break
        
        # Fallback: if no time column found, we'll use index
        use_index_as_time = time_col is None
        
        # Fallback: if no value column, use first numeric column
        if val_col is None:
            for col in columns:
                if col != time_col and col != series_col and col != label_col:
                    if df[col].dtype in ['float64', 'int64', 'float32', 'int32']:
                        val_col = col
                        break
        
        # If still no value column, use second column or first if only one
        if val_col is None and len(columns) >= 2:
            val_col = columns[1] if columns[0] == time_col else columns[0]
        elif val_col is None and len(columns) == 1:
            val_col = columns[0]
            use_index_as_time = True
        
        # Build data array with proper NaN handling
        data = []
        series_set = set()
        
        # Helper function to convert time to ISO format
        def to_iso_time(time_val, idx):
            if time_val is None:
                return f"1970-01-01T00:00:{idx:02d}.000Z"
            time_str = str(time_val)
            # Try to parse various formats and convert to ISO
            try:
                from datetime import datetime
                # Try common formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y/%m/%d %H:%M:%S', 
                           '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%fZ']:
                    try:
                        dt = datetime.strptime(time_str, fmt)
                        return dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
                    except ValueError:
                        continue
                # Already ISO format or unrecognized - return as-is with T replacement
                if 'T' not in time_str and ' ' in time_str:
                    return time_str.replace(' ', 'T') + '.000Z'
                return time_str
            except Exception:
                return time_str
        
        for idx, row in df.iterrows():
            # Handle time: use index if no time column, convert to ISO format
            if use_index_as_time:
                time_value = f"1970-01-01T00:00:{idx % 60:02d}.000Z"
            else:
                time_value = to_iso_time(row[time_col], idx)
            
            # Handle value: convert to float, default to 0 if NaN/None
            try:
                val_value = float(row[val_col]) if row[val_col] is not None else 0.0
            except (ValueError, TypeError):
                val_value = 0.0
            
            # Handle series
            if series_col and row[series_col] is not None:
                series_value = str(row[series_col])
            else:
                series_value = 'value'
            series_set.add(series_value)
            
            # Handle label: ensure it's a string or empty
            if label_col and row[label_col] is not None:
                label_value = str(row[label_col])
            else:
                label_value = ''
            
            data.append({
                'time': time_value,
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
            'hasTimeColumn': not use_index_as_time,
            'detectedColumns': {
                'time': time_col,
                'value': val_col,
                'series': series_col,
                'label': label_col
            }
        })
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'trace': traceback.format_exc()}), 500


# ==================== Annotations ====================
@app.route('/api/annotations/<filename>', methods=['GET'])
def get_annotations(filename):
    """Get annotations for a file"""
    try:
        annotation_file = os.path.join(ANNOTATIONS_DIR, f"{filename}.json")
        
        if not os.path.exists(annotation_file):
            return jsonify({
                'success': True,
                'filename': filename,
                'annotations': []
            })
        
        with open(annotation_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'annotations': data.get('annotations', [])
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/annotations', methods=['POST'])
def save_annotations():
    """Save annotations for a file"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        annotations = data.get('annotations', [])
        
        if not filename:
            return jsonify({'success': False, 'error': 'Filename is required'}), 400
        
        annotation_file = os.path.join(ANNOTATIONS_DIR, f"{filename}.json")
        
        annotation_data = {
            'filename': filename,
            'annotations': annotations,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(annotation_file, 'w', encoding='utf-8') as f:
            json.dump(annotation_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': 'Annotations saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/annotations/<filename>', methods=['DELETE'])
def delete_annotation(filename):
    """Delete a specific annotation"""
    try:
        data = request.get_json()
        annotation_id = data.get('annotation_id')
        
        if not annotation_id:
            return jsonify({'success': False, 'error': 'Annotation ID is required'}), 400
        
        annotation_file = os.path.join(ANNOTATIONS_DIR, f"{filename}.json")
        
        if not os.path.exists(annotation_file):
            return jsonify({'success': False, 'error': 'Annotation file not found'}), 404
        
        with open(annotation_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        annotations = data.get('annotations', [])
        annotations = [a for a in annotations if a.get('id') != annotation_id]
        
        data['annotations'] = annotations
        data['last_updated'] = datetime.now().isoformat()
        
        with open(annotation_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': 'Annotation deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/download-annotations/<filename>', methods=['GET'])
def download_annotations(filename):
    """Download annotations in target JSON format"""
    try:
        annotation_file = os.path.join(ANNOTATIONS_DIR, f"{filename}.json")
        
        if not os.path.exists(annotation_file):
            return jsonify({
                'annotations': [],
                'export_time': datetime.now().isoformat(),
                'filename': filename
            })
        
        with open(annotation_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Format for export
        export_annotations = []
        for ann in data.get('annotations', []):
            export_ann = {
                'categories': ann.get('categories', {}),
                'local_change': ann.get('local_change', {})
            }
            export_annotations.append(export_ann)
        
        return jsonify({
            'annotations': export_annotations,
            'export_time': datetime.now().isoformat(),
            'filename': filename
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== Label Configuration ====================
@app.route('/api/labels', methods=['GET'])
def get_labels():
    """Get label configuration"""
    try:
        if os.path.exists(LABELS_FILE):
            with open(LABELS_FILE, 'r', encoding='utf-8') as f:
                labels = json.load(f)
            return jsonify({'success': True, 'labels': labels})
        else:
            return jsonify({
                'success': True,
                'labels': {
                    'overall_attribute': {},
                    'local_change': {},
                    'custom_labels': []
                }
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/labels', methods=['POST'])
def save_labels():
    """Save label configuration"""
    try:
        data = request.get_json()
        
        with open(LABELS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': 'Labels saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/labels/custom', methods=['POST'])
def add_custom_label():
    """Add a custom label"""
    try:
        data = request.get_json()
        label_text = data.get('label', '')
        label_color = data.get('color', '#3b82f6')
        
        if not label_text:
            return jsonify({'success': False, 'error': 'Label cannot be empty'}), 400
        
        if os.path.exists(LABELS_FILE):
            with open(LABELS_FILE, 'r', encoding='utf-8') as f:
                labels = json.load(f)
        else:
            labels = {'overall_attribute': {}, 'local_change': {}, 'custom_labels': []}
        
        new_label = {
            'id': f'custom_{int(time.time() * 1000)}',
            'text': label_text,
            'color': label_color
        }
        
        existing_texts = [l.get('text', l) if isinstance(l, dict) else l 
                         for l in labels.get('custom_labels', [])]
        
        if label_text not in existing_texts:
            labels.setdefault('custom_labels', []).append(new_label)
            
            with open(LABELS_FILE, 'w', encoding='utf-8') as f:
                json.dump(labels, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'custom_labels': labels['custom_labels']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Time Series Annotator v2 - Backend Starting...")
    print("API Server: http://localhost:5000")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Annotations Directory: {ANNOTATIONS_DIR}")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
