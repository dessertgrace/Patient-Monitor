import datetime
import requests
import patientMonitoringServer as pms

server_name = "http://127.0.0.1:5000/"


def check_server_status():
    """Check if the server is on

    Check if the server is on by making a get request
    to the base url 'http://0.0.0.0:5011/'
    Print the message and error code to the screen

    :return: None
    """
    r = requests.get(server_name)
    print(r.text)
    print(r.status_code)


def add_pats_for_test():
    imgS1 = pms.convert_image_file_to_string("test_data/test_image.jpg")
    imgS2 = pms.convert_image_file_to_string("images/esophagus2.jpg")
    imgS3 = pms.convert_image_file_to_string("images/esophagus 1.jpg")
    imgS4 = pms.convert_image_file_to_string("images/synpic50411.jpg")
    newPat = {"number": 100, "name": "Grace", "ECG_image": imgS1,
              "ECG_hr": 80,
              "medical_image": imgS2}
    r = requests.post(server_name + "new_info", json=newPat)
    newPat = {"number": 123, "name": "Grace", "ECG_image": imgS1,
              "ECG_hr": 60,
              "medical_image": imgS3}
    r = requests.post(server_name + "new_info", json=newPat)
    newPat = {"number": 123, "name": "Grace Dessert", "ECG_image": imgS2,
              "ECG_hr": 70,
              "medical_image": imgS4}
    r = requests.post(server_name + "new_info", json=newPat)
    print(r.text)
    print(r.status_code)


def getInfo(case, inputD):
    """Get information from patient database by making POST requests

    Get information by making a post request to the /get_info/<case> route
    on the server.
    Case 1 returns a list of medical record numbers in the database.
    The input dictionary should be empty and it returns a list of
    integers of the current medical record numbers, with an error code
    Case 2 returns the latest HR and ECG image for a given patient
    The input dictionary should be in the following form,
    {"number": int}, and the method returns a dictionary in the
    following format {"name": name, "latest_heart_rate": latest_heart_rate,
    "ECG_image": ECG_image}, with an error code.
    Case 3 returns a list of timestamps of ECG entries as strings
    for a given patient. The input dictionary should be in the following form,
    {"number": int}, and it returns a list of
    strings of the current timestamps of the ECG images in the following
    form: "%m/%d/%Y, %H:%M:%S", with an error code
    Case 4 returns a list of medical images as strings for a specific patient.
    The input dictionary should be in the following form, {"number": int},
    and it returns a list of 64-bit string encodings of the medical record
    numbers from the database.
    Case 5 returns a dictionary of a specific ECG image as a
    64-bit string encoding and the corresponding heart rate
    in the following form:
    {"ECG_image": str, "HR": int}.
    The input dictionary should be in the following form,
    {"number": 100,  "timestamp": ddtS}, where ddtS is a string of the
    specific datetime that the ECG was uploaded, "%m/%d/%Y, %H:%M:%S".
    This case returns a list of 64-bit string encodings of the medical record
    numbers from the database.
    Case 6 returns a specific medical image as a 64-bit string encoding.
    The input dictionary should be in the following form, {"number": int,
    "index": int} where the "index" value is a valid index for the list of
    medical images available for that patient in the database.
    This case returns a 64-bit string encoding of the corresponding
    medical image.

    :param case: an int from 1 to 6 representing the type of info
        to get from the server
    :param inputD: a dictionary of the POST request input information
        to each route case
    :return: the output the server request- usually a dictionary or list
        and an error code
    """
    inputD["case"] = case
    pms.logInfo(inputD, event="get_info")
    if case == 1:
        # return a list of medical record numbers in the database
        r = requests.post(server_name + "get_info/1", json=inputD)
        return r.json(), r.status_code
    elif case == 2:
        # return latest HR and ECG image
        # newPat = {"number": 100}
        r = requests.post(server_name + "get_info/2", json=inputD)
        return r.json(), r.status_code
    elif case == 3:
        # return list of timestamps as strings
        # inputD = {"number": 100}
        r = requests.post(server_name + "get_info/3", json=inputD)
        return r.json(), r.status_code
    elif case == 4:
        # return a list of medical images as strings
        # inputD = {"number": 100}
        r = requests.post(server_name + "get_info/4", json=inputD)
        return r.json(), r.status_code
    elif case == 5:
        # return a dictionary of a specific ECG image as a
        # 64-bit string encoding and the corresponding heart rate
        # ddtS = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        # newPat = {"number": 100,  "timestamp": ddtS}
        r = requests.post(server_name + "get_info/5", json=inputD)
        return r.json(), r.status_code
    elif case == 6:
        # return a specific medical image as a 64-bit string encoding
        # newPat = {"number": 100, "index": 0}
        r = requests.post(server_name + "get_info/6", json=inputD)
        return r.json(), r.status_code


if __name__ == "__main__":
    pms.initialize_server()
    pms.clearDB()
