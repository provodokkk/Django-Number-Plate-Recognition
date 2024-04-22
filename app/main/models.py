from django.db import models


# class uploaded_files(models.Model):
#     plate_type = models.CharField(max_length=5)


class license_plates(models.Model):
    # file_id = models.IntegerField
    # uploaded_file = models.CharField(max_length=64, default=None, null=False)
    file = models.FileField(upload_to='uploads', default=None)
    plate_number = models.CharField(max_length=32, default='Unknown')
    accuracy = models.FloatField(default=0)
