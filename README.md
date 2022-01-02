# Patient Monitoring System

## Overview

The Patient Monitoring System uses a client-server structure and two graphical user interfaces (GUIs) to allow patient data to be stored in a cloud database and retrieved for continuous monitoring. It includes a patient-side GUI and a monitoring-station GUI as clients to communicate with the server and interface with the database. This project was developed with a partner as the final project for BME 547: Medical Software Design.


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

## User Instructions & Project Overview

Please watch the following instructional video. 
<https://drive.google.com/file/d/1PWkV9IJmzFpRatDi6QVuMnHKRQQvGcz9/view?usp=sharing>



## Database

This project uses MongoDB, a non-relational database. We defined the class `Patient`, which inherits the `MongoModel` class. The class is structured as followed:
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

The server is run on a virtual machine with the url <http://152.3.69.122:5011/>. **The server is currently inactive.** 
We developed a **RESTful API** that implements the following tasks needed by the clients:

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


### Server API

* `POST/new_info` takes a JSON-encoded dictionary in the following format:
  ```
  { "name": str,
    "number": int, 
    "ECG_image": str,
    "ECG_hr": int,
    "medical_image": str }
  ``` 
  The dictionary must include the patient medical record number at a minimum. The dictionary will be checked to ensure that the needed keys and data types exist. If the medical record number is not present in the database, the patient is added to the database. If the number is present, the information in the dictionary is added to the preexisting patient entry. An error code of 400 and a validation error are returned if the mandatory key is not present or if the values are not of the desired types. If there is no validation error, a message is returned that the patient has been added or that information has been added to the preexisting patient.


* `POST/get_info/<case>` takes a JSON-encoded dictionary with a different format based on the desired client information, specified by the "case" field, which must be the string of an integer from 1 to 6. Depending on the desired client information, one of six functions will be called to return the requested information along with an error code. A status code of 400 and a validation error is returned if the mandatory key is not present, if the values are not of the desired types, or if the patient id is not valid. If there is no validation error, the function will return the desired information specified by `case`. See server code for further information. 


## Logging
Log messages will be added to both the local client log file as well as the remote server log file on the virtual machine.


## License 


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

![example branch parameter](https://github.com/dessertgrace/Patient-Monitor/actions/workflows/main.yml/badge.svg?branch=status_badge)
