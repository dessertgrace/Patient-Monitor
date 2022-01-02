# BME 547 Final Project: Patient Monitoring Client/Server

## Overview

This project is a culmination of everything we have learned in BME 547 this semester. It requires us to design a Patient Monitoring System with a patient-side client, a monitoring-station client, and a server/database that allows for patient data to be uploaded and stored on the server and retrieved for continuous monitoring.


## Database

This project utilizes a non-relational database called MongoDB, which is run on a virtual machine with the url <http://152.3.69.122:5011/>. The database is accessed through post requests to the database API. To create a database item, we defined the class name `Patient`, which inherits the `MongoModel` class. The class is structured as followed:
```

class Patient(MongoModel):
    name = fields.CharField()
    number = fields.IntegerField(primary_key=True)
    ECG_images = fields.ListField()
    ECG_heartRates = fields.ListField()
    ECG_dateTimes = fields.ListField()
    medicalImages = fields.ListField()
```

Because a patient's medical record number is unique to each patient, `number` is set as the primary key.


## Server

The server for this project is a cloud based web service running on the virtual machine with a RESTful API that implements the following tasks needed by the clients:

* Accepts uploads from the patient-side client that includes the patient medical record number at a minimum. The upload may also contain a patient name, medical image, and/or heart rate & ECG image.
* Communicate with and use the database to store the uploaded data for future retrieval.
* Store the date and time of receipt when a heart rate and ECG image are received.
* If the upload contains a medical record number that does not exist in the database, a new entry is made for that unique patient, and the information sent with the request is stored in the new record.
* If the upload contains a medical record number that already exists in the database, any medical image and/or heart rate & ECG image sent with that request is added to the existing information for that patient. If a patient name is sent, it updates the existing name in the database.
* Accepts requests from the monitoring station client to retrieve the following information from the database and download it to the client:
  + A list of existing patient medical record numbers
  + The name and latest heart rate & ECG image for a specific patient
  + A list of ECG Image timestamps for a specific patient
  + A specific ECG Image based on the timestamp for a specific patient
  + A medical Image for a specific patient
* Provide any other necessary services for the client to perform its needed functions.


## API

* `POST/new_info` takes a JSON in the following format:
  ```

  {
    "name": str,
    "number": int, 
    "ECG_image": str,
    "ECG_hr": int,
    "medical_image": str
  }
  ```

The JSON-encoded string will include the patient medical record number at a minimum. The JSON will be checked to ensure that the needed keys and data types exist. If they do exist, the database will be checked to see if the medical record number exists. If the number already exists, the patient is added to the database. If the number does not already exist, the information in the JSON is added to the preexisting patient. An error code of 400 and a validation error are returned if the mandatory key is not present or if the values are not of the desired types. If there is no validation error, a message is returned that the patient has been added or that information has been added to the preexisting patient.

* `POST/get_info/<case>` takes a JSON with a different format based on the desired client information, specified by the varibale URL "case". The JSON-encoded string contains the key `number` at a minimum. Depending on the desired client information, one of six functions will be called to return the requested information along with an error code. A status code of 400 and a validation error is returned if the mandatory key is not present, if the values are not of the desired types, or if the patient id is not valid. If there is no validation error, the function will return the desired information specified by `case`.


## Patient-side GUI Client

The patient-side GUI client provides a graphical user interface with the following functionality:

* Allow the user to enter a patient name.
* Allow the user to enter a patient medical record number.
* Allow the user to select and display a medical image from the local computer.
* Allow the user to select an ECG data file from the local computer that will then be analyzed for heart rate in beats per minute to be displayed on the GUI along with an image of the ECG trace.
* Upon user command, issue a RESTful API request to the server to upload whatever information has been uploaded. The interface will only allow this request to be made if at least a medical record number has been entered. Data to upload includes the medical record number, patient name, measured heart rate/ECG image, and medical image. An item does not need to be uploaded if it was not selected. 

The existing ECG analysis code module is modified with a function that the GUI calls to analyze the patient heart rate.


## Monitoring Station GUI Client

The monitoring station GUI client provides a graphical user interface with the following functionality:

* Allow the user to select a patient medical record number from a list of available numbers on the server.
* Display the medical record number, patient name, latest measured heart rate & ECG image (if ones exists), and the date/time at which the latest heart rate data was uploaded to the server for the selected patient.
* Allow the user to select from a list of historical ECG images and their date/times for the selected patient, download the selected image, and display the selected image side-by-side with the latest ECG image already displayed.
* Allow the user to save a downloaded ECG image, either the historical one chosen or the latest, to a file on the local computer.
* Allow the user to select from a list of saved medical images for the patient, download and display the image, and save it locally.
* When the user selects a new patient, any information on the interface from the previous patient will be replaced with the information from the new patient or removed from the interface.
* Make periodic requests (at least every 30 seconds) to the server to check for updated information from the selected patient. If a new heart rate and ECG image are available, they will be automaticallu downloaded and displayed on the interface.
* When the user wants to select a new patient, select an historical ECG, or select a medical image for a patient, the choices on the interface should represent the most recent options on the server.
* Make RESTful API requests to the server to get lists of available patient medical record numbers, available data for the selected patient, and the data themselves.


## Patient-side GUI User Instructions

1. To run the server on a users's local computer, type `python patientMonitoringServer.py` in one terminal window.
2. In another window, run `patient_GUI.py`. The Patient-side GUI will pop up on the local computer.
3. The user MUST enter a patient medical record number in the `Medical Record Number` entry box that contains ONLY integers. If the user fails to input a medical record number or the input contains letters or special characters other than integers, the GUI will display "value type not valid" upon selecting the `Ok` button, and any information will not be uploaded to the server.
4. The user should follow the same process for the `Name` entry box. There is no need to use quotation marks around the inputted name, as the default value type is a string. Entering a patient name is optional.
5. To select a medical image from the users's local computer, press the `Select Image` button below the first blank image. The user can navigate to any directory or folder on their local computer to select a JPG image. Once the user selects an image, it will be resized and displayed in the first blank image template. Selecting a medical image is optional.
6. To select an ECG file from the users's local computer, press the `Select ECG File` button below the second blank image. The user can navigate to any directory or folder on their local computer to select a CSV ECG file. Once the user selects a file, the ECG image trace will be displayed in the second blank image template, and the patient's average heart rate will be displayed in beats per minute between the second blank image and the `Select ECG File` button. Selecting an ECG file is optional.
7. When the user is ready to upload the input patient data, he or she will select the `Ok` button, which sends a request to the server to upload whatever information has been entered and/or selected. If the user fails to provide a patient medical record number, a message will appear on the GUI that says "value type not valid" when the user presses the `Ok` button. This message will remain until the user uploads a valid medical record number. The same message will be displayed if the user uploads any entry with the incorrect data type. If the user uploads a valid medical record number that does not already exist within the database, the GUI will display a message that says "New patient added to database". If the medical record number already exists in the database, the GUI will display a message that reads "Patient info added to database".
8. To cancel the program and no longer display the GUI, the user must select the `Cancel` button in the bottom right corner.


## Monitoring Station GUI User Instructions

1. To run the server on a users's local computer, type `python patientMonitoringServer.py` in one terminal window.
2. In another window, run `monitoringGUI.py`. The Patient-side GUI will pop up on the local computer.
3. To select the desired patient medical record number, the user must choose from the drop down menu in the upper left corner of the GUI next to the label `Select Patient Medical Record Number`. The corresponding medical record number will be displayed next to the label `Medical Record Number` and the patient name associated with this number will be displayed next to the `Patient Name` label.
4. The latest EGC image trace and corresponding heart rate data that have been sent from the Patient-side GUI will be displayed in the first blank image template, along with the time at which the information was uploaded to the server.
5. The drop down menu next to the label `Select Historical ECG` contains all of the date times at which ECG data have been sent from the Patient-side GUI. The user can select any date time to display the ECG image trace that was uploaded to the server at that time in the second blank image template. The heart rate associated with that image trace will also be displayed under the image.
6. To select the desired medical image that has been uploaded to the server from the Patient-side GUI, the user should use the drop down menu in the `Medical Images` section of the GUI. The selected image will be displayed below in the third blank image template.
7. To download and save any of the displayed images, the user should select the download button directly below the desired image.
8. The user should wait 30 seconds from the time the Patient-side GUI sends information before attempting to select that patient medical record number.
9. To cancel the program and no longer display the GUI, the user should select the `Quit` button in the bottom left corner.


## Logging
Log messages will be added to both the local client log file as well as the remote server log file on the virtual machine.


## Video URL

<https://drive.google.com/file/d/1PWkV9IJmzFpRatDi6QVuMnHKRQQvGcz9/view?usp=sharing>

Copyright (c) [2021] [RachelLopez][GraceDessert]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "final-project-graceandrachel"), to deal in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE

![example branch parameter](https://github.com/dessertgrace/Patient-Monitor/actions/workflows/pytest_runner.yml/badge.svg?event=push)
