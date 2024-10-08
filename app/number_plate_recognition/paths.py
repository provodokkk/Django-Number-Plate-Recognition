import shutil
import os


# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Model paths
COCO_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'yolov8n.pt')
LICENSE_PLATE_DETECTOR_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'license_plate_detector.pt')

# Results
RESULTS_CSV_FILE_PATH = os.path.join(BASE_DIR, 'results.csv')
INTERPOLATED_CSV_FILE_PATH = os.path.join(BASE_DIR, 'test_interpolated.csv')


def get_files_data(folder_path: str) -> list[dict[str, str]]:
    files = os.listdir(folder_path)
    return [{'name': file, 'path': os.path.join(folder_path, file)} for i, file in enumerate(files)]


# Uploads
UPLOADS_DIR = os.path.join(BASE_DIR, '..', 'media', 'buffer', 'uploads')
UPLOADS_DIR_CONST = os.path.join(BASE_DIR, '..', 'media', 'uploads')


def get_uploaded_file_info():
    files_data = get_files_data(UPLOADS_DIR)
    if files_data:
        return files_data[0]
    return None


# Outputs
OUTPUTS_DIR = os.path.join(BASE_DIR, '..', 'media', 'buffer', 'outputs')
OUTPUTS_DIR_CONST = os.path.join(BASE_DIR, '..', 'media', 'outputs')


def get_output_file_info():
    return get_files_data(OUTPUTS_DIR)[0]


# Processed frames
PROCESSED_FRAMES_DIR = os.path.join(BASE_DIR, '..', 'media', 'buffer', 'processed_frames')
PROCESSED_FRAMES_DIR_CONST = os.path.join(BASE_DIR, '..', 'media', 'processed_frames')


def get_all_processed_frame_files_info():
    return get_files_data(PROCESSED_FRAMES_DIR)


def clear_folder(folder_path: str) -> None:
    """Clears all files in the specified folder."""
    try:
        shutil.rmtree(folder_path)
        os.makedirs(folder_path)
    except Exception as e:
        print(f"An error occurred while clearing the folder: {e}")


def clear_buffer_directories():
    clear_folder(UPLOADS_DIR)
    clear_folder(OUTPUTS_DIR)
    clear_folder(PROCESSED_FRAMES_DIR)


def move_files(source_dir: str, destination_dir: str) -> None:
    """Move files from source directory to destination directory."""
    files = os.listdir(source_dir)

    for file in files:
        source_path = os.path.join(source_dir, file)
        dest_path = os.path.join(destination_dir, file)
        shutil.move(source_path, dest_path)


def move_all_files_to_constant_dirs():
    move_files(UPLOADS_DIR, UPLOADS_DIR_CONST)
    move_files(OUTPUTS_DIR, OUTPUTS_DIR_CONST)
    move_files(PROCESSED_FRAMES_DIR, PROCESSED_FRAMES_DIR_CONST)
