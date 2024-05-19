import os


def run_plate_recognition():
    """Runs the code for plate recognition and visualization"""
    os.system('python ./number_plate_recognition/plate_recognition.py')
    os.system('python ./number_plate_recognition/add_missing_data.py')
    os.system('python ./number_plate_recognition/visualize.py')
