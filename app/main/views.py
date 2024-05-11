from django.shortcuts import render
import os

from main.forms import UploadFileForm
from main.models import File, Plate

from number_plate_recognition import main
from number_plate_recognition.paths import INTERPOLATED_CSV_FILE_PATH, get_output_file_info
from number_plate_recognition.paths import clear_all_directories, get_all_processed_frame_files_info
from number_plate_recognition.visualize import get_plates_with_highest_score


def index(request):
    if request.method == 'POST':
        clear_all_directories()

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
    file.processed_file = os.path.join('outputs', processed_file['name'])
    file.save()

    processed_frames = get_all_processed_frame_files_info()
    plates_with_highest_score_data = get_plates_with_highest_score(INTERPOLATED_CSV_FILE_PATH)

    for plate, frame in zip(plates_with_highest_score_data, processed_frames):
        accuracy = round(float(plate['license_number_score']) * 100, 2)
        new_plate = Plate(file_id=file.id, frame_number=plate['frame_number'], plate_number=plate['license_number'],
                          accuracy=accuracy, processed_frame=f"processed_frames/{frame['name']}")
        new_plate.save()

    last_plate = Plate.objects.last()
    plates = Plate.objects.filter(file_id=last_plate.file_id)

    context = {
        'file': file,
        'file_type': determine_file_type(processed_file['name']),
        'plates': plates,
    }
    return render(request, 'main/results.html', context)


def determine_file_type(file_url):
    _, extension = os.path.splitext(file_url)
    if extension.lower() in ('.jpg', '.jpeg', '.png'):
        return 'image'
    elif extension.lower() in ('.mp4', '.mov', '.avi'):
        return 'video'
    else:
        return None
