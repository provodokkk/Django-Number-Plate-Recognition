import os
import sys


def run_plate_recongition(input_file: str):
    """Runs the code for plate recognition and vizualization"""
    os.system(f'python plate_recognition.py {sys.argv[1]}')
    os.system('python add_missing_data.py')
    os.system('python visualize.py')

