from django.db import models
from number_plate_recognition.util import file_upload_path


class Files(models.Model):
    uploaded_file = models.FileField(upload_to=file_upload_path, default=None)
    processed_file = models.FileField(upload_to='buffer/outputs', default=None)


class Plates(models.Model):
    file = models.ForeignKey('Files', on_delete=models.CASCADE)
    frame_number = models.IntegerField(default=0)
    plate_number = models.CharField(max_length=32, default='Error')
    accuracy = models.FloatField(default=0)
    processed_frame = models.FileField(upload_to='buffer/outputs', default=None)
