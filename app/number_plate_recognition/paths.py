import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Model paths
COCO_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'yolov8n.pt')
LICENSE_PLATE_DETECTOR_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'license_plate_detector.pt')

# Results
RESULTS_CSV_FILE_PATH = os.path.join(BASE_DIR, 'results.csv')
INTERPOLATED_CSV_FILE_PATH = os.path.join(BASE_DIR, 'test_interpolated.csv')


# Uploads path
def process_uploads_folder(folder_path: str) -> dict:
    files = os.listdir(folder_path)
    return {'name': files[0],  # take only 1 file at a time
            'path': os.path.join(folder_path, files[0]), }


UPLOADS_DIR = os.path.join(BASE_DIR, '..', 'media', 'uploads')
uploaded_file = process_uploads_folder(UPLOADS_DIR)

# Output path
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
output_file = {'path': ''}




