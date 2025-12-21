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
    """Read CSV or Excel file data"""
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
        
        # Convert to TRAINSET format: time, val, series, label
        # Try to detect columns
        columns = df.columns.tolist()
        
        # Build response data
        data = []
        time_col = None
        val_col = None
        
        # Auto-detect time column
        for col in columns:
            if col.lower() in ['time', 'timestamp', 'datetime', 'date']:
                time_col = col
                break
        
        # Auto-detect value column  
        for col in columns:
            if col.lower() in ['value', 'val', 'values']:
                val_col = col
                break
        
        # If not found, use first two columns
        if time_col is None and len(columns) >= 1:
            time_col = columns[0]
        if val_col is None and len(columns) >= 2:
            val_col = columns[1]
        
        # Build data array
        for idx, row in df.iterrows():
            data.append({
                'time': str(row[time_col]) if time_col else str(idx),
                'val': float(row[val_col]) if val_col and pd.notna(row[val_col]) else 0,
                'series': 'value',
                'label': ''
            })
        
        return jsonify({
            'success': True,
            'filename': filename,
            'columns': columns,
            'data': data,
            'seriesList': ['value'],
            'labelList': []
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


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
