from django import forms

# attrs = {'class': 'upload-file-field'}
class UploadFileForm(forms.Form):
    file = forms.FileField(label='File')
