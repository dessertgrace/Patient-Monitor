from os import EX_CONFIG
import pymodm
from pymodm import errors as pymodm_errors
from patient_class import Patient
from pymodm import connect, MongoModel, fields
from flask import Flask, jsonify, request
import logging
from datetime import datetime
import requests
import base64
import io
import matplotlib.image as mpimg
from matplotlib import pyplot as plt
from skimage.io import imsave
import os.path
import ssl

app = Flask(__name__)
logFileName = "patientMonitoringServer.log"


def initialize_server():
    """ Initializes server conditions
    This function initializes the server log as well as creates a connection
    with the MongoDB database.  User will need to edit the connection string
    to match their specific MongoDB connect string.  If you are posting to a
    public repository, you would want to make sure that your MongoDB database
    access ID and password were not stored in the code but rather protected
    in a file or environment variable that is not pushed to GitHub.
    Note:  Just because the `connect` function completes does not ensure that
    the connection was actually made.  You will need to check that data is
    successfully stored in your MongoDB database.
    Note:  This function does not need a unit test.
    """
    # logging.basicConfig(filename=logFileName,
    #                     level=logging.DEBUG)
    print("Connecting to MongoDB...")
    connect("mongodb+srv://dessertgrace:"
            "youcan@bme547.allsv.mongodb."
            "net/myFirstDatabase?retryWrites="
            "true&w=majority", ssl_cert_reqs=ssl.CERT_NONE)
    print("Connection attempt finished.")


@app.route("/", methods=["GET"])
def server_status():
    """Server route for testing if server is on.

    A GET request with the base server URL
    returns a string if the server is on.

    :return: "Server is on"
    """
    return "Server is on"


@app.route("/new_info", methods=['POST'])
def new_info():
    """Implements /new_info route for adding patient data to the server
    database

    The /new_info route is a POST request that should receive a
    JSON-encoded string with the following format:
    {"name": str, "number": int, "ECG_image": str,
    "ECG_hr": int, "medical_image": str},
    but will include the medical record "number" at a minimum.
    The function then calls modification functions to ensure that the needed
    keys and data types exist in the received JSON, then calls a function that
    adds the patient to the database, in the case that the record number
    is new, and adds the patient info to the patient if the record number
    already exists in the database. The function then returns to the
    caller either a status code of 400 and a validation error if the mandatory
    key is not present or if the values are not of the desired types. If there
    is no validation error, the function will return a message that the patient
    has been added, or that info has been added to a preexisting patient.

    :return: string message, and error code
    """
    indata = request.get_json()
    inDictEntries = {"name": str,
                     "number": int,
                     "ECG_image": str,
                     "ECG_hr": int,
                     "medical_image": str}
    reqKeys = ["number"]
    message, code, p = modify_indata(indata, inDictEntries, reqKeys)
    return jsonify(message), code


@app.route("/get_info/<case>", methods=["POST"])
def get_info(case):
    """Implements /get_info route for getting patient data from the
    database

    The /get_info route is a POST request that should receive a JSON-encoded
    string with a different format based on the desired client information,
    specified by the variable URL "case". The JSON will contain the key
    "number" at a minimum. Depending on the desired information, one of six
    functions will be called to return the information along with an error
    code. A status code of 400 and a validation error is returned if the
    mandatory key is not present, if the values are not of the desired
    types, or if the patient id is not valid. If there is no validation
    error, the function will return the desired information specifed by
    the "case".

    :param case: int specifying wha client information is desired
    :return: requested information specified by "case" and error code
    """
    indata = request.get_json()
    try:
        case = int(case)
    except TypeError:
        return "Error: invalid case number", 400
    if case == 1:
        medical_record_numbers, code = get_medical_record_numbers()
        return jsonify(medical_record_numbers), code
    if case == 2:
        dict, code = get_n_hr_ECG(indata)
        return jsonify(dict), code
    if case == 3:
        ECG_image_timestamps, code = get_ECG_image_timestamps(indata)
        return jsonify(ECG_image_timestamps), code
    if case == 4:
        out, err = get_medImages(indata)
        return jsonify(out), err
    if case == 5:
        out, err = get_ECGImg(indata)
        return jsonify(out), err
    if case == 6:
        out, err = get_MedicalImg(indata)
        return jsonify(out), err
    indata["case"] = case
    logInfo(indata, event="get_info")
    return "Error: case number for info requested not found", 400


def get_n_hr_ECG(indata):
    """Get name, latest heart rate, and latest ECG image
    from the patient database

    Given a patient ID, get the corresponding patient name,
    latest heart rate, and latest ECG image as a 64bit encoded
    string image from the database and download it to that client

    :param in_data: dictionary of patient ID with
        the following format: {"number": int}
    :return: dict with the following format, and an error code
        dict = {"name": name, "latest_heart_rate": latest_heart_rate,
            "ECG_image": ECG_image} where the values are:
        string containing patient name, int containing
        patient's latest heart rate, string containing ECG
        image encoding
    """
    print("one")
    inDictEntries = {"number": int}
    reqKeys = ["number"]
    msg, code1 = validate_input(indata, inDictEntries, reqKeys)
    print("two")
    patient_id, code2 = validate_patient_id(indata["number"])
    print("three")
    if code1 != 200 or code2 != 200:
        return "Invalid patientID", 400
    patient = Patient.objects.raw({"_id": patient_id}).first()
    print("four")
    name = patient.name
    if len(patient.ECG_heartRates) > 0:
        latest_heart_rate = patient.ECG_heartRates[-1]
    else:
        latest_heart_rate = []
    if len(patient.ECG_images) > 0:
        ECG_image = patient.ECG_images[-1]
    else:
        ECG_image = []
    print("five")
    dict = {"name": name, "latest_heart_rate": latest_heart_rate,
            "ECG_image": ECG_image}
    return dict, 200


def get_medical_record_numbers():
    """Get a list of available patient medical record numbers
    from the patient database

    Appends each medical record number existing in the database to
    a list and returns the list along with an error code

    :return: list of ints containing patient medical record numbers
    and an error code
    """
    medical_record_numbers = []
    for patient in Patient.objects.raw({}):
        medical_record_numbers.append(patient.number)
    return medical_record_numbers, 200


def logInfo(indata, event):
    """Log event in 'INFO' level using logging module.

    Store event data in a log file with 'INFO' level.
    This method works differently for three events:
    addition of a new patient, new information for
    an existing patient, and retrieving information
    from the database (with the /get_info route).
    This method will add a message to the log
    file stored globally with name 'logFileName'.

    :param indata: dictionary of information, some of
        which will be logged
    :param event: one of three strings for three types of
        events that can be handled. ("new_patient",
        "new_info", or "get_info")
    :return: none
    """
    logging.basicConfig(filename=logFileName, filemode="w", level=logging.INFO)
    if event == "new_patient":
        patID = indata["number"]
        logging.info("Added new patient with medical record "
                     "number: " + str(patID))
    elif event == "new_info":
        fieldsPresent = []
        for key in indata:
            if key == "number":
                continue
            fieldsPresent.append(key)
        patID = indata["number"]
        fieldsS = ", ".join(fieldsPresent)
        logging.info("Added or updated the following information "
                     "for patient with record number: " +
                     str(patID) + ": " + fieldsS)
    elif event == "get_info":
        case = indata["case"]
        caseStrs = ["medical record numbers", "latest ECG image "
                                              "and heart rate",
                    "timestamps of all ECG entries", "encodings "
                                                     "of all medical images",
                    "string encoding and heart rate for a specific ECG",
                    "string encoding for a specific medical image"]
        outStr = "Retrieved " + caseStrs[int(case)-1]
        if "number" in indata:
            patID = indata["number"]
            outStr = outStr + "for patient with record number: " + str(patID)
        logging.info(outStr)
    else:
        logging.info("Invalid logging event type!")
    return


def get_ECG_image_timestamps(indata):
    """Get ECG image timestamps for a specific patient
    from the patient database

    Given a patient ID, get the corresponding ECG image
    timestamps from the database and download it to the
    client

    :param in_data: dictionary of patient ID with
        the following format: {"number": int}
    :return: list of ECG image timestamps as strings for a specific
    patient and an error code. The dt strings have the following
    format:  "%m/%d/%Y, %H:%M:%S"
    """
    inDictEntries = {"number": int}
    reqKeys = ["number"]
    msg, code1 = validate_input(indata, inDictEntries, reqKeys)
    patient_id, code2 = validate_patient_id(indata["number"])
    if code1 != 200 or code2 != 200:
        return "Invalid patientID", 400
    patient = Patient.objects.raw({"_id": patient_id}).first()
    ECG_image_timestamps = patient.ECG_dateTimes
    return ECG_image_timestamps, 200


def get_medImages(in_data):
    """get list of medical images from patient database

    Given a patient ID, get the medical images from the database,
    as 64bit encoded strings.

    :param in_data: dictionary of patient ID with
        the following format: {"number": int}
    :return: list of strings of medical image encodings or error message,
        and error code
    """
    inDictEntries = {"number": int}
    reqKeys = ["number"]
    msg, code1 = validate_input(in_data, inDictEntries, reqKeys)
    patient_id, code2 = validate_patient_id(in_data["number"])
    if code1 != 200 or code2 != 200:
        return "Invalid patientID", 400
    patient = Patient.objects.raw({"_id": patient_id}).first()
    return patient.medicalImages, 200


def get_ECGImg(in_data):
    """get specific ECG image from patient database

    Given a patient ID and a timestamp of an ECG object,
    get the corresponding ECG image from the database,
    as a 64bit encoded string image.

    :param in_data: dictionary of patient ID and timestamp of
        relevant medical record number in patient entry with
        the following format: {"number": int, "timestamp": str}
    :return: dictionary containing string of ECG image encoding
        and the corresponding heart rate with the following format:
        {"ECG_image": str, "HR": int}, or an error message,
        and an error code
    """
    inDictEntries = {"number": int, "timestamp": str}
    reqKeys = ["number", "timestamp"]
    msg, code1 = validate_input(in_data, inDictEntries, reqKeys)
    patient_id, code2 = validate_patient_id(in_data["number"])
    if code1 != 200 or code2 != 200:
        return "Invalid patientID or timestamp type", 400
    patient = Patient.objects.raw({"_id": patient_id}).first()
    times = patient.ECG_dateTimes
    hrs = patient.ECG_heartRates
    for t in range(len(times)):  # t.strftime("%m/%d/%Y, %H:%M:%S")
        if times[t] == in_data["timestamp"]:
            dictR = {"ECG_image": patient.ECG_images[t], "HR": hrs[t]}
            return dictR, 200
    return "ECG with given timestamp not found!", 400


def get_MedicalImg(in_data):
    """get specific medical image from patient database

    Given a patient ID and an index of a medical record number,
    get the corresponding medical image from the database,
    as a 64bit encoded string image.

    :param in_data: dictionary of patient ID and index of
        relevant medical record number in patient entry with
        the following format: {"number": int, "index": int}
    :return: string of medical image encoding or error message,
        and error code
    """
    inDictEntries = {"number": int, "index": int}
    reqKeys = ["number", "index"]
    msg, code1 = validate_input(in_data, inDictEntries, reqKeys)
    patient_id, code2 = validate_patient_id(in_data["number"])
    if code1 != 200 or code2 != 200:
        return "Invalid patientID or image index", 400
    patient = Patient.objects.raw({"_id": patient_id}).first()
    index = in_data["index"]
    imgs = patient.medicalImages
    if index in range(len(imgs)):
        return patient.medicalImages[index], 200
    return "Medical image with given index not found!", 400


def find_patient(id_no):
    """Retrieves patient record from database based on patient id

    This function searches the MongoDB "Patient" database for the record
    with an "id" of that given as the "id_no" parameter.  If a match is
    found, that Patient instance is returned.  If no match is found, the
    boolean False is returned.

    :param id_no: id number of patient to be found in database
    :return: Patient instance if patient found in database, False if not
    """
    try:
        patient = Patient.objects.raw({"_id": id_no}).first()
    except pymodm.errors.DoesNotExist:
        patient = False
    return patient


def validate_patient_id(patient_id):
    """Validates that the string obtained from the variable URL of
    /get_results/<patient_id> contains an integer and that a patient exists
    in the database with that id.

    A string is sent to this function which first checks if the string contains
    an integer.  If not, an appropriate error message is returned.  If the
    string does contain an integer, that integer is used to check the database.
    If a patient exists with that id number, then the integer is returned
    along with a status code of 200.  Otherwise, an error message is returned
    with a status code of 400.

    :param: patient_id (str): string containing an inputted patient_id
    :return: str or int , int: the patient_id if it exists in
        database or an error
        message followed by a status code
    """
    try:
        id_no = int(patient_id)
    except ValueError:
        return "Patient id was not a valid integer", 400
    patient = find_patient(id_no)
    if patient is False:
        return "Patient id does not exist in database", 400
    return id_no, 200


#  on the client side, the image contained in a file is transformed
#  into a base64 string to
#  be sent to the server.
#  The server receives the base64 string and sends it to the
#  database for storage.
#  The base64 string is converted into an ndarray that contains
#  the image data.
#  This ndarray can be processed and converted back to a base64
#  string and then sent back to the client.
#  The client receives the base64 string with the encoded
#  processed image.
# The base64 string is converted to an ndarray for display
# using matplotlib and is also converted to a file
#  for storage on the computer.


def convert_image_file_to_string(filename, width=200, height=0):
    """convert an image file to a base64 string

    Transforms the image contained in a file into a
    base64 string to be sent to the server and sent to
    the database for storage

    :param filename: filename: string variable containing
        the path and name of the image file on computer
    :return: string variable containing the image bytes
        encoded as a base64 string
    """
    with open(filename, "rb") as image_file:
        b64_bytes = base64.b64encode(image_file.read())
    b64_string = str(b64_bytes, encoding='utf-8')
    return b64_string


def convert_string_to_image_file(b64_string, new_filename):
    """convert a base64 string to an image file

    Transforms the base64 string into an image contained in a file
    to be stored on the local computer

    :param b64_string: string variable containing the image bytes
        encoded as a base64 string
    :param new_filename: string containing name of desired image file
    :return: an image file on the local computer with the path and
        name contained in the new_filename variable
    """
    image_bytes = base64.b64decode(b64_string)
    with open(new_filename, "wb") as out_file:
        out_file.write(image_bytes)
    return out_file


def convert_string_to_ndarray(b64_string):
    """convert base64 string to ndarray

    Transforms the base64 string to an ndarray containing
    image data for image processing and display

    :param b64_string: string variable containing the image bytes
        encoded as a base64 string
    :return: variable containing an ndarray with image data
    """
    image_bytes = base64.b64decode(b64_string)
    image_buf = io.BytesIO(image_bytes)
    img_ndarray = mpimg.imread(image_buf, format='JPG')
    return img_ndarray


def display_image_in_ndarray(img_ndarray):
    """displays image in ndarray format using matplotlib

    Uses ndarray format to display a matplotlib window with
    an image

    :param img_ndarray: variable containing an ndarray with image
        data
    """
    plt.clf()
    plt.imshow(img_ndarray, interpolation='nearest')
    plt.show()


def convert_image_in_ndarray_to_string(img_ndarray):
    """convert image in ndarray format into base64 string

    Transforms image in ndarray format into a base64 string
    to be sent to the server and stored in the database

    :param img_ndarray: variable containing an ndarray with image
        data
    :return: string variable containing image bytes encoded as
        a base64 string
    """
    f = io.BytesIO()
    imsave(f, img_ndarray, plugin='pil')
    y = base64.b64encode(f.getvalue())
    b64_string = str(y, encoding='utf-8')
    return b64_string


# @app.route("/api/<client>", methods=['POST'])
# def access_info_from_db():
# indata = request.get_json()
# inDictEntries = {"records": list,
# "ECG_image_timestamps": list,
# "medical_images:": list,
# "ECG_image": str,
# "medical_image": str}


def modify_indata(indata, inDictEntries, reqKeys):
    """Calls several functions for input validation, and then adds
    the new patient or patient info to the database in the
    is_patient_new function

    This method calls the validate input function to ensure that the
    mandatory keys are present in the input dictionary and that the
    values are of the desired types. If the mandatory keys are not
    present or the values are not of the desired types, a status code
    of 400 and the corresponding error message is returned. If the
    mandatory keys are present, but the values are not of the desired
    types, the attemptFixInput function is called to try to convert
    the values to the desired types. A new dictionary is returned and
    validated once again. This new dictionary is input to the function
    is_patient_new to check if the patient already exists in the database,
    in which case their info will be added, or if the patient is new, in
    which case the patient and their info will be added. A message is
    returned confirming that the patient and/or their info has been added
    to the database.

    :param indata: dictionary to try to fix
    :param inDictEntries: template dictionary with keys to check
        existance of in indata, and values of the valid types for the
        value of each key in indata
    :param  reqKeys: a list of strings of the
        keys that are required to be in the input dict
    :return: string message, error code, and patient obj
    """
    # print('ok')
    err, code = validate_input(indata, inDictEntries, reqKeys)
    # print(err)
    if err == "required key not present":
        return err, code, ""
    if err == "value type not valid":
        # print("ok0")
        new_dict = attemptFixInput(indata, inDictEntries)
        # print("ok1")
        # print(new_dict)
        err2, code2 = validate_input(new_dict, inDictEntries, reqKeys)
        # print("ok2")
        # print(err2)
        # print(str(code2))
        if code2 != 200:
            return err2, code2, ""
        else:
            message, p = is_patient_new(new_dict)
            return message, 200, p
    # print("one")
    message, p = is_patient_new(indata)
    # print("two")
    # print(message)
    # print("three")
    return message, 200, p


def is_patient_new(new_dict):
    """Checks whether the patient exists in the database and
    adds the corresponding information.

    This method determines whether or not the patient exists in the
    datbase. If the upload from the patient side contains a medical
    record number already found in the database, a new entry will be made
    for that patient, and the information sent with the request stored in
    the new record. If the upload contains a medical record number already
    found in the database, any medical image and/or heart rate/ECG image
    sent with the request should be added to the existing information.
    If a patient name is also sent, it should update the existing name in
    the database.

    :param: the validated input dictionary
    :return: string message indicating if the patient and/or patient
    info has been added, and patient object
    """
    found = 0
    id_list = []
    # print("p")
    for patient in Patient.objects.raw({}):
        # print("q")
        id_list.append(patient.number)
        # print(id_list)
    for id in id_list:
        if new_dict["number"] == id:
            found = 1
            p = add_patient_info(new_dict)
            print("Patient info added to database")
            return "Patient info added to database", p
    if found == 0:
        # print("r")
        add_new_patient(new_dict["number"])
        # print("s")
        p = add_patient_info(new_dict)
        print("New patient added to database")
        return "New patient added to database", p


def ECGdriver(times, voltages):
    """When new ECG data is received, calculate the
    heart rate and get the ECG plot image.

    Given input time and voltage arrays,
    call functions to clean/filter ECG data,
    calculate the heart rate, and plot it.
    First, save the plot as an image file,
    then call the encoding function to
    convert it to a string, and save.
    ECG analysis functions that have been tested already.
    Tests are located in test_ecg.py.

    :param: times: an array of floats of time data
    :param: voltages: an array of floats of voltage data
    :return: heartRate: average HR across data as float
    :return: stringECGImg: plot of clean ECG data
        as 64bit string-encoded image
    """
    import ecg
    # times, voltages = ecg.input_data("test_data20.csv")
    times2, voltages2 = ecg.remove_non_numbers(times, voltages, "")
    voltages2 = ecg.above_three_hundred(voltages2, "")
    samp_rate = ecg.sampling_rate(times2)
    filtered = ecg.filtering(samp_rate, voltages2)
    num_beats, beats, mean_hr_bpm = ecg.peak_detection(filtered, times2)
    imgECG_filename = getECGPlotImage(times2, filtered)
    stringECGImg = convert_image_file_to_string(imgECG_filename)
    return mean_hr_bpm, stringECGImg


def getECGPlotImage(time, data):
    """Plot data and save the image of the plot as a .jpg file

    Given input x and y data as arrays of floats, plot a simple
    line plot using matplotlib, and save the image of the plot
    as a .jpg file.

    :param time: array of floats of time data data
    :param data: array of floats of filtered ECG voltage data
    :return: filename for the cached .jpg file
    """
    plt.clf()
    plt.plot(time, data)
    # plt.plot(peaks, data[peaks], "x")
    filename = "cache/tempPlotData.jpg"
    # make dir cache if doesnt exist
    if not os.path.isdir("cache"):
        os.mkdir("cache")
    plt.savefig(filename)
    return filename


def attemptFixInput(indata, inDictEntries):
    """Attempt to fix input dictionary input to make values of
    desired type.

    Return a dictionary with all the same keys but with values
    that are the same or if possible, converted types to the
    desired type,
    specified in the inDictEntries input dictionary.

    :param indata: dictionary to try to fix
    :param inDictEntries: template dictionary with keys to check
        existance of in indata, and values of the valid types for the
        value of each key in indata
    :return: dictionary with same keys as indata and either the same
        values or with some converted to the correct type
    """
    newDict = {}
    for k in indata:
        # print(k)
        if k in inDictEntries:
            # print(k)
            if isinstance(indata[k], type(inDictEntries[k])):
                newDict[k] = indata[k]
            else:
                try:
                    newDict[k] = inDictEntries[k](indata[k])
                except ValueError:
                    newDict[k] = indata[k]
                except TypeError:
                    newDict[k] = indata[k]
        else:
            newDict[k] = indata[k]
    return newDict


def validate_input(inputTest, inputValid, reqKeys):
    """Validate dictionary entry for data transfer

    Make sure that the dictionary entries
    have the right value types and that
    all mandatory keys are present. Keys in the input
    that are not in the validation or req dictionaries
    are kept and not tested.

    :param inputTest: the input dictionary to
        test that the required keys are present
        and the values are of the right type
    :param inputValid: a dict of keys
        and types for the values in inDictEntries
    :param  reqKeys: a list of strings of the
        keys that are required to be in the input dict
    :return: string message, and error code
    """
    # print(inputTest)
    # print(inputValid)
    # print(reqKeys)
    for key in reqKeys:
        # print(key)
        if key not in inputTest:
            return "required key not present", 400
    for key in inputTest:
        # print(key)
        if key in inputValid:
            if type(inputTest[key]) != inputValid[key]:
                return "value type not valid", 400
    # print("returning")
    return "", 200


def clearDB():
    """Clear MongoDB patient database

    Remove all entries from the patient database.

    :return: none
    """
    a = Patient.objects.raw({})
    for patient in a:
        patient.delete()


def add_new_patient(number_arg):
    """Add a new patient Mongo DB entry

    This function adds a new Patient to the DB
    with all empty fields except for the
    number argument. This function should only
    be called when this medical number is not present
    in the patient database.

    :param number_arg: an integer of the medical record number
        for this new patient
    :return: none
    """
    u = Patient(number=number_arg)
    u.save()
    print("Saved to database")
    indata = {"number": number_arg}
    logInfo(indata, event="new_patient")
    return u


def add_patient_info(indata):
    """Add new info to patient Mongo DB entry

    This function adds a new info to the patient DB.
    The only field that is required is the number_arg.
    This function should only
    be called when this patient number is present
    in the patient database. If ECG data is present,
    there must be both a string image encoding and
    a heart rate present.
    Each piece of information is added to the existing
    patient entry if possible. If it cannot be added
    (the field is a single int, not a list), then it
    replaces the current patient info.
    When ECG data is received, it calls the heart rate and
    the ECG image (encoded as a string),
    and it saves the date and time of receipt.

    :param indata: dictionary of patient info with
        the following format. Only the "number" field is required.
        {"name": str,
        "number": int,
        "ECG_image": str,
        "ECG_hr": int,
        "medical_image": str}
    :return: patient object
    """
    print('adding new pat')
    patient = Patient.objects.raw({"_id": indata["number"]}).first()
    if "name" in indata:
        patient.name = indata["name"]
    if "ECG_image" in indata:
        patient.ECG_images.append(indata["ECG_image"])
        patient.ECG_heartRates.append(indata["ECG_hr"])
        dateTime = datetime.now()
        dts = dateTime.strftime("%m/%d/%Y, %H:%M:%S")
        print(dts)
        patient.ECG_dateTimes.append(dts)
    if "medical_image" in indata:
        patient.medicalImages.append(indata["medical_image"])
    patient.save()
    print("Saved to database")
    logInfo(indata, event="new_info")
    return patient


if __name__ == '__main__':
    initialize_server()
    server_status()
    clearDB()
    # app.run(host="0.0.0.0", port=5011)
    app.run()
