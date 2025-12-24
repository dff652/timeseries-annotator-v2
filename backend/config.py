import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ANNOTATIONS_DIR = os.path.join(BASE_DIR, 'annotations')
LABELS_FILE = os.path.join(BASE_DIR, 'config', 'labels.json')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ANNOTATIONS_DIR, exist_ok=True)
