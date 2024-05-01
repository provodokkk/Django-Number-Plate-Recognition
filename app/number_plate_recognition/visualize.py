import ast

import cv2
import numpy as np
import pandas as pd


def add_license_plate_overlay(frame: np.ndarray, license_crop: np.ndarray,
                              license_plate_number: str, license_plate_bbox: str) -> None:
    """
    Add license plate overlay to a frame.

    Args:
        frame: Input frame to which the overlay will be added.
        license_crop: Cropped license plate image.
        license_plate_number: License plate number.
        license_plate_bbox: Bounding box coordinates of the license plate in string format.

    Returns:
        None
    """
    try:
        # Parse bounding box coordinates
        car_x1, car_y1, car_x2, car_y2 = parse_bbox(license_plate_bbox)

        # Get dimensions of the license crop
        H, W, _ = license_crop.shape

        # Store car shape data in a dictionary
        car_shape_data = {'x1': car_x1, 'y1': car_y1,
                          'x2': car_x2, 'y2': car_y2,
                          'height': H, 'width': W, }

        # Add license plate image to the frame
        add_license_plate_image(frame, license_crop, car_shape_data)

        # Add background for the license plate number
        add_background(frame, car_shape_data)

        # Add license plate number text to the frame
        add_license_plate_text(frame, license_plate_number, car_shape_data)

    except ValueError as e:
        print(f"ValueError occurred while adding license plate overlay: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while adding license plate overlay: {e}")


def add_license_plate_image(frame, license_crop, car_shape):
    """
    Add license plate image to the frame.

    Args:
        frame: Input frame to which the overlay will be added.
        license_crop: Cropped license plate image.
        car_shape: Dictionary containing the shape data of the car.

    Returns:
        None
    """
    frame[int(car_shape['y1']) - car_shape['height'] - 100:int(car_shape['y1']) - 100,
          int((car_shape['x1'] + car_shape['x2'] - car_shape['width']) / 2):int(
              (car_shape['x1'] + car_shape['x2'] + car_shape['width']) / 2), :] = license_crop


def add_background(frame, car_shape):
    """
    Add background for the license plate number.

    Args:
        frame: Input frame to which the overlay will be added.
        car_shape: Dictionary containing the shape data of the car.

    Returns:
        None
    """
    frame[int(car_shape['y1']) - car_shape['height'] - 400:int(car_shape['y1']) - car_shape['height'] - 100,
          int((car_shape['x1'] + car_shape['x2'] - car_shape['width']) / 2):int(
              (car_shape['x1'] + car_shape['x2'] + car_shape['width']) / 2), :] = (255, 255, 255)


def add_license_plate_text(frame, license_plate_number, car_shape):
    """
    Add license plate number text to the frame.

    Args:
        frame: Input frame to which the overlay will be added.
        license_plate_number: License plate number.
        car_shape: Dictionary containing the shape data of the car.

    Returns:
        None
    """
    (text_width, text_height), _ = cv2.getTextSize(license_plate_number, cv2.FONT_HERSHEY_SIMPLEX, 4.3, 17)
    cv2.putText(frame, license_plate_number, (int((car_shape['x1'] + car_shape['x2'] - text_width) / 2),
                                              int(car_shape['y1'] - car_shape['height'] - 250 + (text_height / 2))),
                cv2.FONT_HERSHEY_SIMPLEX, 4.3, (0, 0, 0), 17)


def extract_license_plate_data(results: pd.DataFrame) -> dict:
    """
    Extract license plate data from the results DataFrame.

    Args:
        results: DataFrame containing the results.

    Returns:
        dict: Dictionary containing extracted license plate data for each car_id.
    """
    license_plate_data = {}
    grouped_results = results.groupby('car_id')

    for car_id, group in grouped_results:
        max_row = group.loc[group['license_number_score'].idxmax()]

        license_bbox_str = max_row['license_plate_bbox']
        license_bbox = [float(coord) for coord in license_bbox_str.split()]

        license_plate_data[car_id] = {'max_score': max_row['license_number_score'],
                                      'license_plate_number': max_row['license_number'],
                                      'frame_number': max_row['frame_number'],
                                      'license_bbox': license_bbox, }

    return license_plate_data


def capture_license_plate_crop(frame, license_bbox):
    """
    Capture and resize the license plate crop from the frame.

    Args:
        frame: The input image frame.
        license_bbox: Bounding box coordinates of the license plate in the format (x1, y1, x2, y2).

    Returns:
        The cropped and resized license plate image.
    """
    x1, y1, x2, y2 = license_bbox

    # Extracting the region of interest from the frame
    license_crop = frame[int(y1):int(y2), int(x1):int(x2), :]

    # Resizing the license plate crop to a fixed height of 400 pixels while maintaining the aspect ratio
    height = 400
    width = int((x2 - x1) * height / (y2 - y1))
    license_crop = cv2.resize(license_crop, (width, height))

    return license_crop


def process_license_plate_data(cap, results):
    """
    Process license plate data by extracting relevant information from the results DataFrame,
    capturing license plate crops from corresponding frames, and storing them along with their associated plate numbers.

    Args:
        cap: VideoCapture object.
        results: DataFrame containing the results.

    Returns:
        Dictionary containing license plate crops and plate numbers for each car ID.
    """
    license_plate_data = extract_license_plate_data(results)
    license_plate = {}

    for car_id, data in license_plate_data.items():
        # Set video capture to the frame containing the license plate
        cap.set(cv2.CAP_PROP_POS_FRAMES, data['frame_number'])

        # Read the frame
        ret, frame = cap.read()

        # Capture the license plate crop
        try:
            license_crop = capture_license_plate_crop(frame, data['license_bbox'])
        except Exception as e:
            print(f"Error capturing license plate crop for car ID {car_id}: {e}")
            continue

        # Store license plate crop and number
        license_plate[car_id] = {'license_crop': license_crop,
                                 'license_plate_number': data['license_plate_number']}

    return license_plate


def parse_bbox(bbox):
    # Replace multiple spaces with single space and remove leading space inside brackets
    bbox = bbox.replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ',')
    # Convert string representation of tuple to actual tuple using ast.literal_eval
    x1, y1, x2, y2 = ast.literal_eval(bbox)
    return x1, y1, x2, y2


def draw_border(frame, bbox, color=(0, 0, 255)):
    """
    Draw a colored rectangle border around the object specified by the bounding box coordinates on the given frame.

    Args:
        frame: Input frame to which the rectangle border will be drawn.
        bbox: Bounding box coordinates of the object in the format (x1, y1, x2, y2).
        color: Color of the rectangle border in BGR format (default is red: (0, 0, 255)).

    Returns:
        None
    """
    # Extract coordinates from the bounding box
    x1, y1, x2, y2 = parse_bbox(bbox)

    # Draw rectangle border on the frame
    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 12)


def crop_license_plate(frame, license_plate_bbox, license_plate):
    """
    Overlay the license plate crop onto a frame.

    Args:
        frame: Input frame to which the license plate crop will be overlaid.
        license_plate_bbox: Bounding box coordinates of the license plate in the format (x1, y1, x2, y2).
        license_plate: Dictionary containing license plate crop and plate number.

    Returns:
        None
    """
    # Extract license plate crop and plate number from the license_plate dictionary
    license_crop = license_plate['license_crop']
    license_plate_number = license_plate['license_plate_number']

    # Overlay the license plate crop onto the frame
    add_license_plate_overlay(frame, license_crop, license_plate_number, license_plate_bbox)


def process_frame(frame, results, license_plate, frame_number):
    """
    Process a single frame by drawing borders around detected cars and license plates,
    and overlaying license plate crops.

    Args:
        frame: Input frame to be processed.
        results: DataFrame containing detection results.
        license_plate: Dictionary containing license plate crops and plate numbers for each car ID.
        frame_number: Number of the frame to be processed.

    Returns:
        None
    """
    # Filter results DataFrame for the current frame number
    df_ = results[results['frame_number'] == frame_number]

    for row in range(len(df_)):
        draw_border(frame, df_.iloc[row]['car_bbox'], color=(0, 0, 255))
        draw_border(frame, df_.iloc[row]['license_plate_bbox'], color=(0, 255, 0))

        # Get license plate data for the current car
        license_plate_data = license_plate[df_.iloc[row]['car_id']]

        # Overlay license plate crop onto the frame
        crop_license_plate(frame, df_.iloc[row]['license_plate_bbox'], license_plate_data)


def process_video(cap, results, license_plate, out):
    """
    Process each frame of a video by applying object detection results and overlaying license plate information.

    Args:
        cap: VideoCapture object for the input video.
        results: DataFrame containing object detection results.
        license_plate: Dictionary containing license plate crops and plate numbers for each car ID.
        out: VideoWriter object for the output video.

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
        process_frame(frame, results, license_plate, frame_number)

        # Write the processed frame to the output video
        out.write(frame)

        frame = cv2.resize(frame, (1280, 720))


def main():
    results = pd.read_csv('./test_interpolated.csv')

    # Load input video
    video_path = './assets/sample.mp4'
    cap = cv2.VideoCapture(video_path)

    # Define codec and create VideoWriter object for output video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter('./out.mp4', fourcc, fps, (width, height))

    license_plate = process_license_plate_data(cap, results)

    # Process each frame of the video and write processed frames to output video
    process_video(cap, results, license_plate, out)

    # Release resources
    out.release()
    cap.release()


if __name__ == '__main__':
    main()
