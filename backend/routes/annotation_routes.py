import os
import json
import tempfile
import shutil
from datetime import datetime
from flask import Blueprint, jsonify, request
from auth import login_required
from config import ANNOTATIONS_DIR

annotation_bp = Blueprint('annotation', __name__)

@annotation_bp.route('/api/annotations/<filename>', methods=['GET'])
@login_required
def get_annotations(filename, current_user):
    """Get annotations for a file (user-specific)"""
    try:
        user_ann_dir = os.path.join(ANNOTATIONS_DIR, current_user)
        os.makedirs(user_ann_dir, exist_ok=True)
        
        annotation_file = None
        annotation_data = None
        
        # Try finding the file by exact name or by searching content
        pattern1 = os.path.join(user_ann_dir, f"{filename}.json")
        if os.path.exists(pattern1):
            annotation_file = pattern1
        
        if not annotation_file:
            # Fallback search
            for json_file in os.listdir(user_ann_dir):
                if not json_file.endswith('.json'): continue
                json_path = os.path.join(user_ann_dir, json_file)
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if data.get('filename') == filename:
                            annotation_file = json_path
                            annotation_data = data
                            break
                except: continue
        
        if not annotation_file:
            return jsonify({'success': True, 'filename': filename, 'annotations': []})
        
        if not annotation_data:
            with open(annotation_file, 'r', encoding='utf-8') as f:
                annotation_data = json.load(f)
        
        # Normalize fields for frontend (expert_output -> expertOutput)
        annotations = annotation_data.get('annotations', [])
        for ann in annotations:
            if 'expert_output' in ann and 'expertOutput' not in ann:
                ann['expertOutput'] = ann['expert_output']
        
        return jsonify({
            'success': True,
            'filename': filename,
            'annotations': annotations,
            'overall_attribute': annotation_data.get('overall_attribute', {})
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@annotation_bp.route('/api/annotations/<filename>', methods=['POST'])
@login_required
def save_annotations(filename, current_user):
    """Save annotations for a file using atomic write"""
    try:
        data = request.get_json()
        
        # Field normalization and structure validation
        if 'filename' in data:
            save_data = data
        else:
            save_data = {
                'filename': filename,
                'overall_attribute': data.get('overall_attributes', {}),
                'annotations': data.get('annotations', []),
                'export_time': datetime.now().isoformat()
            }
            
        # Ensure consistent naming inside annotations
        for ann in save_data.get('annotations', []):
            if 'expertOutput' in ann:
                ann['expert_output'] = ann['expertOutput'] # Save both for compatibility
        
        user_ann_dir = os.path.join(ANNOTATIONS_DIR, current_user)
        os.makedirs(user_ann_dir, exist_ok=True)
        annotation_file = os.path.join(user_ann_dir, f"{filename}.json")
        
        # Atomic write using a temporary file
        fd, temp_path = tempfile.mkstemp(dir=user_ann_dir, text=True)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as tmp:
                json.dump(save_data, tmp, ensure_ascii=False, indent=2)
            os.replace(temp_path, annotation_file)
        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise
        
        return jsonify({'success': True, 'message': f'Annotations saved for {filename}'})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@annotation_bp.route('/api/annotations/<filename>', methods=['DELETE'])
@login_required
def delete_annotation(filename, current_user):
    """Delete a specific annotation"""
    try:
        data = request.get_json()
        annotation_id = data.get('annotation_id')
        if not annotation_id:
            return jsonify({'success': False, 'error': 'Annotation ID is required'}), 400
        
        user_ann_dir = os.path.join(ANNOTATIONS_DIR, current_user)
        annotation_file = os.path.join(user_ann_dir, f"{filename}.json")
        
        if not os.path.exists(annotation_file):
            return jsonify({'success': False, 'error': 'Annotation file not found'}), 404
        
        with open(annotation_file, 'r', encoding='utf-8') as f:
            file_data = json.load(f)
        
        file_data['annotations'] = [a for a in file_data.get('annotations', []) if a.get('id') != annotation_id]
        file_data['last_updated'] = datetime.now().isoformat()
        
        with open(annotation_file, 'w', encoding='utf-8') as f:
            json.dump(file_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': 'Annotation deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@annotation_bp.route('/api/download-annotations/<filename>', methods=['GET'])
@login_required
def download_annotations(filename, current_user):
    """Download annotations in target JSON format"""
    try:
        user_ann_dir = os.path.join(ANNOTATIONS_DIR, current_user)
        annotation_file = os.path.join(user_ann_dir, f"{filename}.json")
        
        if not os.path.exists(annotation_file):
            return jsonify({'annotations': [], 'export_time': datetime.now().isoformat(), 'filename': filename})
        
        with open(annotation_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        export_annotations = []
        for ann in data.get('annotations', []):
            export_annotations.append({
                'categories': ann.get('categories', {}),
                'local_change': ann.get('local_change', {})
            })
        
        return jsonify({
            'annotations': export_annotations,
            'export_time': datetime.now().isoformat(),
            'filename': filename
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
