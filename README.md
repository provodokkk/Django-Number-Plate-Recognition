# License Plate Recognition Web Application

## Overview

This project is a web application for recognizing vehicle license plates. It is built using Python and the Django framework.

## Models

- **Vehicle Detection**: A YOLOv8 pretrained model is used to detect vehicles.
- **License Plate Detection**: A license plate detector pretrained model is used to detect license plates.

## Features

- **Vehicle Detection**: Identifies vehicles in images.
- **License Plate Detection**: Detects and reads license plates from identified vehicles.
- **Multiple Input Formats**: Supports both photos and videos for processing.
- **Result Visualization**: After processing, users are presented with a page displaying intuitive visualizations of the results.
- **Export to Excel**: Provides the option to download processed data in Excel format.
- **File History**: Users can view previously processed files for reference.

## Installation (Windows)

1. **Clone the repository**:
   ```bash
   git clone git@github.com:provodokkk/Django-Number-Plate-Recognition.git
    ```

2. Create a virtual environment:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3. Navigate to the application folder:
    ```bash
    cd app
    ```
    
4. Install necessary libraries:
    ```bash
    pip install -r requirements.txt
    ```

5. Create database:
    ```bash
    python manage.py makemigrations main
    python manage.py migrate
    ```

6. Run the development server:
    ```bash
    python manage.py runserver
    ```

The development server will start, and you will see a link in the console where the server is running.

> Note: This application currently supports processing JPG and MP4 file types.