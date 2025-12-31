import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import os
import json
import time
from flask import Blueprint, jsonify, request
from config import LABELS_FILE

label_bp = Blueprint('label', __name__)

@label_bp.route('/api/labels', methods=['GET'])
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

@label_bp.route('/api/labels', methods=['POST'])
def save_labels():
    """Save label configuration"""
    try:
        data = request.get_json()
        with open(LABELS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return jsonify({'success': True, 'message': 'Labels saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@label_bp.route('/api/labels/custom', methods=['POST'])
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
