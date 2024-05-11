from django import forms

# attrs = {'class': 'upload-file-field'}
class UploadFileForm(forms.Form):
    uploaded_file = forms.FileField(label='uploaded_file')
