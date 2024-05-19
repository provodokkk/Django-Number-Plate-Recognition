from django.shortcuts import render
from django.http import HttpResponse
from openpyxl import Workbook

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

    context = {
        'form': form,
        'files': File.objects.all()
    }

    return render(request, 'main/index.html', context)


def get_processed_file(request, file_id=None):
    if file_id is not None:
        file = File.objects.get(pk=file_id)
        file_type = determine_file_type(file.processed_file.name)
        plates = Plate.objects.filter(file_id=file.id)
    else:
        main.run_plate_recognition()
        file = File.objects.last()

        # update processed file path to the table
        processed_file = get_output_file_info()
        file.processed_file = os.path.join('buffer', 'outputs', processed_file['name'])
        file.save()

        file_type = determine_file_type(processed_file['name'])

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
        'file_type': file_type,
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


def download_excel(request, file_id):
    wb = Workbook()
    ws = wb.active
    ws.append(['Frame Number', 'Plate Number', 'Accuracy %'])

    processed_data = Plate.objects.filter(file_id=file_id)

    for data in processed_data:
        ws.append([data.frame_number, data.plate_number, data.accuracy])

    # Save workbook to HttpResponse
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=processed_data.xlsx'
    wb.save(response)

    return response
