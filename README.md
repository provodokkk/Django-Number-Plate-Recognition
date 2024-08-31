# License Plate Recognition Web Application

## Overview
This is a web project to recognize license plates in photos and videos. It uses AI to detect vehicles, license plates and license plate symbols. The application also provides a modern user-friendly interface.

The project is under development and is updated regularly.


## Content list
1. [Technologies](#anchor_1)
2. [AI models](#anchor_2)
3. [Functionality](#anchor_3)
4. [Installation (Windows)](#anchor_4)
5. [Application Appearance](#anchor_5)


<a id = "anchor_1"></a>
## Technologies
- Python
- Django
- JavaScript
- HTML
- CSS


<a id = "anchor_2"></a>
## AI models
- **Vehicle Detection**: A YOLOv8 pretrained model is used to detect vehicles.
- **License Plate Detection**: A license plate detector pretrained model is used to detect license plates.


<a id = "anchor_3"></a>
## Functionality
- **Vehicle Detection**: Identifies vehicles in images.
- **License Plate Detection**: Detects and reads license plates from identified vehicles.
- **Multiple Input Formats**: Supports both photos and videos for processing.
- **Result Visualization**: After processing, users are presented with a page displaying intuitive visualizations of the results.
- **Export to Excel**: Provides the option to download processed data in Excel format.
- **File History**: Users can view previously processed files for reference.


<a id = "anchor_4"></a>
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

---
<a id = "anchor_5"></a>
## Application Appearance

### Main page
![main_page](https://github.com/user-attachments/assets/a96f2493-da69-43a7-9099-f615327165ba)

### Results page
![results_page](https://github.com/user-attachments/assets/6f60a4c5-b1ef-40c6-afdb-dfb4809d31d3)
