from django.http import HttpResponse
from django.shortcuts import render
from subprocess import run, PIPE
import sys

from main.forms import UploadFileForm
from main.models import license_plates

from ..number_plate_recognition.main import run_plate_recongition


def index(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            fp = license_plates(file=form.cleaned_data['file'])
            fp.save()
    else:
        form = UploadFileForm()

    return render(request, 'main/index.html', {'form': form})


def run_plate_recognition(request):
    user_input = request.FILES.get('InputFile')
    run_plate_recongition(user_input)
    return render(request, 'main/index.html')
