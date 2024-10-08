from ultralytics import YOLO
import cv2

from sort.sort import *
from util import get_car, read_license_plate, write_csv

from coco_classnames import Classnames
from paths import COCO_MODEL_PATH, LICENSE_PLATE_DETECTOR_MODEL_PATH, RESULTS_CSV_FILE_PATH, get_uploaded_file_info

uploaded_file = get_uploaded_file_info()

# load models
coco_model = YOLO(COCO_MODEL_PATH)
license_plate_detector = YOLO(LICENSE_PLATE_DETECTOR_MODEL_PATH)

mot_tracker = Sort()
vehicles = Classnames.get_vehicles()


def process_frame(frame):
    _results = {}
    # Detect vehicles
    detections = coco_model(frame)[0]
    detected_vehicles = []

    for detection in detections.boxes.data.tolist():
        *vehicle_data, class_id = detection

        if int(class_id) in vehicles:
            detected_vehicles.append(vehicle_data)

    # Track vehicles
    track_ids = mot_tracker.update(np.asarray(detected_vehicles))

    # Detect license plates
    license_plates = license_plate_detector(frame)[0]

    for license_plate in license_plates.boxes.data.tolist():
        x1, y1, x2, y2, license_plate_bbox_score, _ = license_plate
        license_plate_bbox_coords = x1, y1, x2, y2

        # Assign license plate to the car
        *car_bbox_coords, car_id = get_car(license_plate, track_ids)

        if car_id != -1:
            # Crop license plate
            license_plate_crop = frame[int(y1):int(y2), int(x1):int(x2), :]

            # License plate filtering
            license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
            _, license_plate_crop_threshold = cv2.threshold(license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV)

            # Read license plate number
            license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop_threshold)

            if license_plate_text is not None and not 0:
                _results[car_id] = {'car': {'bbox': car_bbox_coords},
                                    'license_plate': {'bbox': license_plate_bbox_coords,
                                                      'text': license_plate_text,
                                                      'bbox_score': license_plate_bbox_score,
                                                      'text_score': license_plate_text_score},
                                   }

    return _results


def process_file(file_name: str, results) -> None:
    frame_number = 0

    if file_name.lower().endswith('.jpg'):  # ('.png', '.jpg', '.jpeg')
        frame = cv2.imread(uploaded_file['path'])
        results[frame_number] = process_frame(frame)
    elif file_name.lower().endswith('.mp4'):  # ('.mp4', '.avi', '.mov')
        ret = True
        cap = cv2.VideoCapture(uploaded_file['path'])

        # read frames
        while ret:
            ret, frame = cap.read()

            if ret:
                results[frame_number] = process_frame(frame)
            frame_number += 1
    else:
        print(f"Unsupported file format: {file_name}")


def main():
    results = {}
    process_file(uploaded_file['name'], results)
    # write results
    write_csv(results, RESULTS_CSV_FILE_PATH)


if __name__ == '__main__':
    main()
