from django.shortcuts import render
import os
import re

from main.forms import UploadFileForm
from main.models import File, Plate

from number_plate_recognition import main
from number_plate_recognition.paths import INTERPOLATED_CSV_FILE_PATH, get_output_file_info
from number_plate_recognition.paths import clear_buffer_directories, get_all_processed_frame_files_info
from number_plate_recognition.paths import move_all_files_to_constant_dirs
from number_plate_recognition.visualize import get_plates_with_highest_score


def index(request):
    if request.method == 'POST':
        clear_buffer_directories()

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            fp = File(uploaded_file=form.cleaned_data['uploaded_file'])
            fp.save()
    else:
        form = UploadFileForm()

    return render(request, 'main/index.html', {'form': form})


def get_processed_file(request):
    main.run_plate_recognition()
    file = File.objects.last()

    # update processed file path to the table
    processed_file = get_output_file_info()
    file.processed_file = os.path.join('buffer', 'outputs', processed_file['name'])
    file.save()

    processed_frames = get_all_processed_frame_files_info()
    plates_with_highest_score_data = get_plates_with_highest_score(INTERPOLATED_CSV_FILE_PATH)

    for plate, frame in zip(plates_with_highest_score_data, processed_frames):
        accuracy = round(float(plate['license_number_score']) * 100, 2)
        new_plate = Plate(file_id=file.id, frame_number=plate['frame_number'], plate_number=plate['license_number'],
                          accuracy=accuracy, processed_frame=f"buffer/processed_frames/{frame['name']}")
        new_plate.save()

    last_plate = Plate.objects.last()
    plates = Plate.objects.filter(file_id=last_plate.file_id)

    move_all_files_to_constant_dirs()
    update_paths_in_database(file)

    context = {
        'file': file,
        'file_type': determine_file_type(processed_file['name']),
        'plates': plates,
    }
    return render(request, 'main/results.html', context)


def remove_buffer_directory(path: str):
    parts = re.split(r'[\\/]', path)
    if parts[0] == 'buffer':
        parts.pop(0)
    return os.path.join(*parts)


def update_paths_in_database(file):
    file.uploaded_file = remove_buffer_directory(str(file.uploaded_file))
    file.processed_file = remove_buffer_directory(str(file.processed_file))
    file.save()

    file_id = file.id
    plates = Plate.objects.filter(file_id=file_id)
    for plate in plates:
        plate.processed_frame = remove_buffer_directory(str(plate.processed_frame))
        plate.save()


def determine_file_type(file_url):
    _, extension = os.path.splitext(file_url)
    if extension.lower() in ('.jpg', '.jpeg', '.png'):
        return 'image'
    elif extension.lower() in ('.mp4', '.mov', '.avi'):
        return 'video'
    else:
        return None
