from django.http import HttpResponse
from django.shortcuts import render
from subprocess import run, PIPE
import sys

from main.forms import UploadFileForm
from main.models import license_plates

sys.path.append('../')  # folder switching
from number_plate_recognition import main
from number_plate_recognition.util import clear_folder
from number_plate_recognition.paths import OUTPUT_DIR, UPLOADS_DIR


def index(request):
    if request.method == 'POST':
        clear_folder(UPLOADS_DIR)
        clear_folder(OUTPUT_DIR)

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            fp = license_plates(file=form.cleaned_data['file'])
            fp.save()
    else:
        form = UploadFileForm()

    return render(request, 'main/index.html', {'form': form})


def run_plate_recognition(request):
    # user_input = request.FILES.get('InputFile')
    main.run_plate_recognition()
    return render(request, 'main/index.html')
