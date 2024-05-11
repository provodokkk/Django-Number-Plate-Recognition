import ast

import os
import sys
import csv
import cv2
import numpy as np
import pandas as pd
import math

from typing import List, Dict, Tuple, Any, Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from number_plate_recognition.paths import get_uploaded_file_info, INTERPOLATED_CSV_FILE_PATH
from number_plate_recognition.paths import OUTPUTS_DIR, PROCESSED_FRAMES_DIR


uploaded_file = get_uploaded_file_info()


class LicensePlateProcessor:
    """A class to process license plate data and overlay onto frames."""
    def __init__(self, results: pd.DataFrame, *, cap: Optional[cv2.VideoCapture] = None,
                 frame: Optional[np.ndarray] = None) -> None:
        """
        Initializes LicensePlateProcessor.

        Args:
            results: DataFrame containing license plate data.
            cap: VideoCapture object for reading frames.
            frame: Initial frame.

        Returns:
            None
        """

        self.__coeff = 0.107                    # Coefficient for resizing the license plate crop.
        self.__cap = cap                        # Object for reading frames.
        self.__frame: np.ndarray = frame        # Current frame.
        self.__results: pd.DataFrame = results  # Contains license plate data.

        self.license_plate: Dict[int, Dict[str, Any]] = {}  # Stores license plate data.
        self.license_crop: np.ndarray = None                # Cropped license plate image.
        self.license_plate_number: str = ''
        self.license_crop_shape: Dict[str, int] = None

        self.process_license_plate_data()

    def get_license_plate(self) -> Dict[int, Dict[str, Any]]:
        """Returns license plate data."""
        return self.license_plate

    def get_frame(self) -> np.ndarray:
        """Returns the current frame."""
        return self.__frame

    def set_frame(self, frame: np.ndarray) -> None:
        """Sets the current frame."""
        self.__frame = frame

    def process_license_plate_data(self) -> None:
        """
        Processes license plate data from results DataFrame.

        Returns:
            None
        """
        license_plate_data = self.extract_license_plate_data()

        for car_id, data in license_plate_data.items():
            if self.__cap:
                self.read_frame(data)

            # Capture the license plate crop
            try:
                self.license_crop = self.capture_license_plate_crop(data['license_bbox'])
            except Exception as e:
                print(f"Error capturing license plate crop for car ID {car_id}: {e}")
                continue

            # Store license plate crop and number
            self.license_plate[car_id] = {'license_crop': self.license_crop,
                                          'license_plate_number': data['license_plate_number']}

    def extract_license_plate_data(self) -> Dict[int, Dict[str, Any]]:
        """
        Extracts license plate data from results DataFrame.

        Returns:
            Dict[int, Dict[str, Any]]: Extracted license plate data.
        """
        license_plate_data = {}
        grouped_results = self.__results.groupby('car_id')

        for car_id, group in grouped_results:
            max_row = group.loc[group['license_number_score'].idxmax()]

            license_bbox_str = max_row['license_plate_bbox']
            license_plate = [float(coord) for coord in license_bbox_str.split()]

            license_plate_data[car_id] = {'max_score': max_row['license_number_score'],
                                          'license_plate_number': max_row['license_number'],
                                          'frame_number': max_row['frame_number'],
                                          'license_bbox': license_plate, }

        return license_plate_data

    def read_frame(self, data: Dict[str, Any]) -> None:
        """
        Reads frame from video capture object.

        Args:
            data: Data containing frame number.

        Returns:
            None
        """
        # Set video capture to the frame containing the license plate
        self.__cap.set(cv2.CAP_PROP_POS_FRAMES, data['frame_number'])

        # Read the frame
        ret, self.__frame = self.__cap.read()

    def capture_license_plate_crop(self, license_bbox: List[float]) -> np.ndarray:
        """
        Captures license plate crop from frame.

        Args:
            license_bbox: Bounding box coordinates of license plate.

        Returns:
            np.ndarray: Cropped license plate image.
        """
        x1, y1, x2, y2 = license_bbox

        # Extracting the region of interest from the frame
        license_crop = self.__frame[int(y1):int(y2), int(x1):int(x2), :]

        height, width, _ = self.__frame.shape

        # Resizing the license plate crop to a fixed height of 400 pixels while maintaining the aspect ratio
        license_height = int(height * self.__coeff)
        license_width = int((x2 - x1) * license_height / (y2 - y1))
        license_crop = cv2.resize(license_crop, (license_width, license_height))

        return license_crop

    def add_license_plate_overlay(self, license_plate_bbox: str) -> None:
        """
        Adds license plate overlay to the frame.

        Args:
            license_plate_bbox: Bounding box coordinates of the license plate.

        Returns:
            None
        """
        try:
            # Parse bounding box coordinates
            car_x1, car_y1, car_x2, car_y2 = self.parse_bbox(license_plate_bbox)

            # Get dimensions of the license crop
            H, W, _ = self.license_crop.shape

            # Store car shape data in a dictionary
            self.license_crop_shape = {'x1': car_x1, 'y1': car_y1,
                                       'x2': car_x2, 'y2': car_y2,
                                       'height': H, 'width': W, }

            # Add license plate image to the frame
            license_plate_image_height = self.add_license_plate_image()

            # Add background for the license plate number
            bg_height, bg_width = self.add_background(license_plate_image_height)

            # Add license plate number text to the frame
            self.add_license_plate_text(bg_height)

        except ValueError as e:
            print(f"ValueError occurred while adding license plate overlay: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while adding license plate overlay: {e}")

    def add_license_plate_image(self) -> int:
        """
        Adds license plate image to the frame.

        Returns:
            int: Height of the license plate image.
        """
        y_top = int(self.license_crop_shape['y1']) - self.license_crop_shape['height']
        y_bottom = int(self.license_crop_shape['y1'])
        height = y_bottom - y_top

        x_left, x_right = self.calculate_horizontal_coordinates()

        self.__frame[y_top:y_bottom, x_left:x_right, :] = self.license_crop

        return height

    def add_background(self, license_plate_image_height: int) -> Tuple[int, int]:
        """
        Adds background for the license plate number.

        Args:
            license_plate_image_height: Height of the license plate image.

        Returns:
            Tuple[int, int]: Height and width of the background.
        """
        y_bottom = int(self.license_crop_shape['y1']) - self.license_crop_shape['height']
        y_top = y_bottom - license_plate_image_height

        x_left, x_right = self.calculate_horizontal_coordinates()

        # Update the frame with white color
        self.__frame[y_top:y_bottom, x_left:x_right, :] = (255, 255, 255)

        bg_height = y_bottom - y_top
        bg_width = x_right - x_left

        return bg_height, bg_width

    def add_license_plate_text(self, bg_height: int) -> None:
        """
        Adds license plate number text to the frame.

        Args:
            bg_height: Height of the background.

        Returns:
            None
        """
        fontScale = bg_height * self.__coeff * self.__coeff
        fontThickness = math.ceil(17 * self.__coeff) * 3

        (text_width, text_height), _ = cv2.getTextSize(self.license_plate_number, cv2.FONT_HERSHEY_SIMPLEX, fontScale, fontThickness)

        x_left, x_right = self.calculate_horizontal_coordinates()
        text_x = int((x_left + x_right - text_width) / 2)
        text_y = int(self.license_crop_shape['y1']) - self.license_crop_shape['height'] - int(bg_height / 3)

        # Put text on the frame
        cv2.putText(self.__frame, self.license_plate_number, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, fontScale, (0, 0, 0), int(fontThickness))

    def calculate_horizontal_coordinates(self) -> Tuple[int, int]:
        """
        Calculates horizontal coordinates for adding license plate overlay.

        Returns:
            Tuple[int, int]: Left and right coordinates.
        """
        x_mid = int((self.license_crop_shape['x1'] + self.license_crop_shape['x2']) / 2)
        x_left = math.ceil(x_mid - self.license_crop_shape['width'] / 2)
        x_right = math.ceil(x_mid + self.license_crop_shape['width'] / 2)
        return x_left, x_right

    @staticmethod
    def parse_bbox(bbox: str) -> Tuple[float, float, float, float]:
        """
        Parses bounding box coordinates.

        Args:
            bbox: String representation of bounding box.

        Returns:
            Tuple[float, float, float, float]: Parsed bounding box coordinates.
        """
        # Replace multiple spaces with single space and remove leading space inside brackets
        bbox = bbox.replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ',')
        # Convert string representation of tuple to actual tuple using ast.literal_eval
        x1, y1, x2, y2 = ast.literal_eval(bbox)
        return x1, y1, x2, y2

    @staticmethod
    def draw_border(frame: np.ndarray, bbox: str, color: Tuple[int, int, int] = (0, 0, 255),
                    thickness: int = 8) -> None:
        """
        Draws border around a bounding box on the frame.

        Args:
            frame: Frame to draw on.
            bbox: Bounding box coordinates.
            color: Color of the border.
            thickness: Thickness of the border.

        Returns:
            None
        """
        # Extract coordinates from the bounding box
        x1, y1, x2, y2 = LicensePlateProcessor.parse_bbox(bbox)

        # Draw rectangle border on the frame
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, thickness)

    def crop_license_plate(self, license_plate_bbox: str, license_plate: Dict[str, Any]) -> None:
        """
        Crops license plate from license_plate dictionary and overlays onto the frame.

        Args:
            license_plate_bbox: Bounding box coordinates of the license plate.
            license_plate: License plate data.

        Returns:
            None
        """
        # Extract license plate crop and plate number from the license_plate dictionary
        self.license_crop = license_plate['license_crop']
        self.license_plate_number = license_plate['license_plate_number']

        # Overlay the license plate crop onto the frame
        self.add_license_plate_overlay(license_plate_bbox)


def get_plates_with_highest_score(csv_file: str):
    # Dictionary to store data for each unique license number
    license_data = {}

    # Read the CSV file
    with open(csv_file, 'r') as file:
        _reader = csv.DictReader(file)

        # Iterate through each row in the CSV file
        for row in _reader:
            car_id = row['car_id']
            license_number_score = float(row['license_number_score'])

            # If license number already exists in dictionary, update if current score is higher
            if car_id in license_data:
                if license_number_score > float(license_data[car_id]['license_number_score']):
                    license_data[car_id] = row
            # If license number is new, add it to dictionary
            else:
                license_data[car_id] = row

    # Convert dictionary values to list
    filtered_data = list(license_data.values())

    return filtered_data


def process_frame(frame: np.ndarray, results: pd.DataFrame, license_plate: Dict[int, Dict[str, Any]], frame_number: int,
                  license_plate_processor: LicensePlateProcessor,
                  bbox_color: Tuple[int, int, int] = (0, 0, 255)) -> np.ndarray:
    """
    Processes a single frame by overlaying license plate information.

    Args:
        frame: Input frame.
        results: DataFrame containing license plate data.
        license_plate: Dictionary containing license plate data.
        frame_number: Frame number.
        license_plate_processor: Instance of LicensePlateProcessor.
        bbox_color: Bounding box color.

    Returns:
        np.ndarray: Processed frame.
    """
    # Filter results DataFrame for the current frame number
    df_ = results[results['frame_number'] == frame_number]

    for row in range(len(df_)):
        LicensePlateProcessor.draw_border(frame, df_.iloc[row]['car_bbox'], color=bbox_color)
        LicensePlateProcessor.draw_border(frame, df_.iloc[row]['license_plate_bbox'], color=bbox_color)

        # Get license plate data for the current car
        license_plate_data = license_plate[df_.iloc[row]['car_id']]

        # Overlay license plate crop onto the frame
        license_plate_processor.crop_license_plate(df_.iloc[row]['license_plate_bbox'], license_plate_data)

    return license_plate_processor.get_frame()


def process_high_score_frames(cap: cv2.VideoCapture, results: pd.DataFrame, license_plate: Dict[int, Dict[str, Any]],
                              license_plate_processor: LicensePlateProcessor) -> None:
    """
    Process frames with the highest score from a CSV file.

    Args:
        cap: VideoCapture object.
        results: DataFrame containing license plate data.
        license_plate: Dictionary containing license plate data.
        license_plate_processor: Instance of LicensePlateProcessor.

    Returns:
        None
    """
    plates_with_highest_score_data = get_plates_with_highest_score(INTERPOLATED_CSV_FILE_PATH)
    for item in plates_with_highest_score_data:
        frame_number = int(item['frame_number'])
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()

        if ret:
            # Process the frame
            license_plate_processor.set_frame(frame)
            process_frame(frame, results, license_plate, frame_number, license_plate_processor, (0, 255, 0))

            uploaded_file_without_extension = remove_file_extension(uploaded_file['name'])
            processed_frame_path = str(os.path.join(PROCESSED_FRAMES_DIR,
                                       f'processed_frame_{frame_number}{uploaded_file_without_extension}.jpg'))
            cv2.imwrite(processed_frame_path, frame)


def remove_file_extension(filename: str):
    """Removes the file extension from a given filename."""
    return os.path.splitext(filename)[0]


def process_video(cap: cv2.VideoCapture, results: pd.DataFrame, license_plate: Dict[int, Dict[str, Any]],
                  out: cv2.VideoWriter, license_plate_processor: LicensePlateProcessor) -> None:
    """
    Processes a video by overlaying license plate information and writes the processed frames to output video.

    Args:
        cap: VideoCapture object.
        results: DataFrame containing license plate data.
        license_plate: Dictionary containing license plate data.
        out: VideoWriter object for output video.
        license_plate_processor: Instance of LicensePlateProcessor.

    Returns:
        None
    """
    frame_number = -1
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    while True:
        ret, frame = cap.read()
        frame_number += 1

        # Break the loop if no frame is returned
        if not ret:
            break

        # Process the current frame
        license_plate_processor.set_frame(frame)
        process_frame(frame, results, license_plate, frame_number, license_plate_processor)

        # Write the processed frame to the output video
        out.write(frame)

        frame = cv2.resize(frame, (1280, 720))

    process_high_score_frames(cap, results, license_plate, license_plate_processor)


def process_photo(image: np.ndarray, results: pd.DataFrame, license_plate: Dict[int, Dict[str, Any]],
                  license_plate_processor: LicensePlateProcessor) -> None:
    """
    Processes a single photo by overlaying license plate information and saves the processed photo.

    Args:
        image: Input image.
        results: DataFrame containing license plate data.
        license_plate: Dictionary containing license plate data.
        license_plate_processor: Instance of LicensePlateProcessor.

    Returns:
        None
    """
    frame_number = 0

    license_plate_processor.set_frame(image)
    process_frame(image, results, license_plate, frame_number, license_plate_processor)

    output_path = str(os.path.join(OUTPUTS_DIR, 'processed_' + uploaded_file['name']))
    cv2.imwrite(output_path, image)

    process_frame(image, results, license_plate, frame_number, license_plate_processor, (0, 255, 0))
    processed_frames_path = str(os.path.join(PROCESSED_FRAMES_DIR, f'processed_frame_' + uploaded_file['name']))
    cv2.imwrite(processed_frames_path, image)


def start_with_video(results: pd.DataFrame) -> None:
    """
    Starts processing with a video input.

    Args:
        results: DataFrame containing license plate data.

    Returns:
        None
    """
    # Load input video
    cap = cv2.VideoCapture(uploaded_file['path'])

    # Define codec and create VideoWriter object for output video
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    output_path = str(os.path.join(OUTPUTS_DIR, 'processed_' + uploaded_file['name']))
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    license_plate_processor = LicensePlateProcessor(results, cap=cap)
    license_plate = license_plate_processor.get_license_plate()

    # Process each frame of the video and write processed frames to output video
    process_video(cap, results, license_plate, out, license_plate_processor)

    # Release resources
    out.release()
    cap.release()


def start_with_photo(results: pd.DataFrame) -> None:
    """
    Starts processing with a photo input.

    Args:
        results: DataFrame containing license plate data.

    Returns:
        None
    """
    image = cv2.imread(uploaded_file['path'])

    license_plate_processor = LicensePlateProcessor(results, frame=image)
    license_plate = license_plate_processor.get_license_plate()

    process_photo(image, results, license_plate, license_plate_processor)


def main() -> None:
    """Main function to start the processing."""
    results = pd.read_csv(INTERPOLATED_CSV_FILE_PATH)

    if uploaded_file['name'].lower().endswith('.jpg'):  # ('.png', '.jpg', '.jpeg')
        start_with_photo(results)
    elif uploaded_file['name'].lower().endswith('.mp4'):  # ('.mp4', '.avi', '.mov')
        start_with_video(results)


if __name__ == '__main__':
    main()
