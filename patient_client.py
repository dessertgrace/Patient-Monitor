import requests
from pymodm import connect, MongoModel, fields
import base64
import patientMonitoringServer
import ssl

patientMonitoringServer.initialize_server()

connect("mongodb+srv://dessertgrace:"
        "youcan@bme547.allsv.mongodb."
        "net/myFirstDatabase?retryWrites"
        "=true&w=majority", ssl_cert_reqs=ssl.CERT_NONE)

server_name = "http://127.0.0.1:5000/"


def add_new_info_to_server(number, name="", heart_rate=1,
                           ECG_image="", medical_image=""):
    """Makes request to server to add specified patient information

    This function takes patient information as parameter inputs and makes
    a post request to the patient monitoring server to store this patient
    information on the server. It prints the server response to the
    console and returns it to the caller.

    :param number: patient medical record number
    :param name: patient name
    :param heart_rate: patient heart rate
    :param ECG_image: patient image trace
    :param medical_image: patient medical image
    :return: server response string
    """
    info1 = {}
    if name:
        info1["name"] = name
    if heart_rate:
        info1["ECG_hr"] = heart_rate
    if ECG_image:
        info1["ECG_image"] = ECG_image
    if medical_image:
        info1["medical_image"] = medical_image
    info1["number"] = number
    r = requests.post(server_name+"new_info", json=info1)
    print(r.status_code)
    print(r.text)
    patientMonitoringServer.logInfo(info1, event="new_info")
    return r.json()
