import filecmp
import os
import pytest
import patientMonitoringServer as pms
from patient_class import Patient
from pymodm import connect, MongoModel, fields
from testfixtures import LogCapture
from datetime import datetime
from flask import jsonify
from matplotlib import pyplot as plt
import logging
import time
import ssl

connect("mongodb+srv://dessertgrace:"
        "youcan@bme547.allsv.mongodb."
        "net/myFirstDatabase?retryWrites"
        "=true&w=majority", ssl_cert_reqs=ssl.CERT_NONE)


def test_add_new_patient():
    #  clearDB()
    p = pms.add_new_patient(1223)
    #  time.sleep(5)
    ps = []
    for patient in Patient.objects.raw({}):
        ps.append(patient)
    assert len(ps) == 1
    assert ps[0].number == 1223
    p.delete()


def test_add_patient_info():
    # clearDB()
    firstECG_image = "Fake64bitEncoding"
    firstECG_heartRate = 60
    p = pms.add_new_patient(123)
    pms.add_patient_info({"number": 123, "name": "Grace",
                          "ECG_image": firstECG_image,
                          "ECG_hr": firstECG_heartRate,
                          "medical_image": "ok"})
    secondECG_image = "Fake64bitEncoding2"
    secondECG_heartRate = 50
    pms.add_patient_info({"number": 123, "name": "Grace Dessert",
                          "ECG_image": secondECG_image,
                          "ECG_hr": secondECG_heartRate,
                          "medical_image": "okOK"})
    # time.sleep(5)
    dt_add = datetime.now()
    print(dt_add)
    ps = []
    for patient in Patient.objects.raw({}):
        ps.append(patient)
    assert len(ps) == 1
    assert ps[0].number == 123
    assert ps[0].name == "Grace Dessert"
    assert len(ps[0].ECG_images) == 2
    assert ps[0].ECG_images[0] == "Fake64bitEncoding"
    assert ps[0].ECG_images[1] == "Fake64bitEncoding2"
    assert len(ps[0].medicalImages) == 2
    assert ps[0].medicalImages[0] == "ok"
    assert ps[0].medicalImages[1] == "okOK"
    assert len(ps[0].ECG_dateTimes) == 2
    dt_exp = ps[0].ECG_dateTimes[0]
    dt_exp = datetime.strptime(dt_exp, "%m/%d/%Y, %H:%M:%S")
    diff = dt_add - dt_exp
    assert diff.seconds < 2
    p.delete()


def test_clearDB():
    #  clearDB()
    p = pms.add_new_patient(123)
    pms.add_patient_info({"number": 123, "name": "Grace"})
    # time.sleep(5)
    clearDB()
    # time.sleep(5)
    ps = []
    for patient in Patient.objects.raw({}):
        ps.append(patient)
    assert len(ps) == 0


@pytest.mark.parametrize("inputTest, inputValid, reqKeys, expectedOut", [
    ({"patient_id": 1,
      "attending_username": "dessert",
      "patient_age": 10}, {"patient_id": int,
                           "attending_username": str,
                           "patient_age": int}, [], ("", 200)),
    ({"patient_id": 1,
      "attending_username": 10,
      "patient_age": 10}, {"patient_id": int,
                           "attending_username": str,
                           "patient_age": int}, [],
     ("value type not valid", 400)),
    ({"attending_username": "dessert",
      "patient_age": 10}, {"patient_id": int,
                           "attending_username": str,
                           "patient_age": int}, [], ("", 200)),
    ({"patient_id": 1,
      "attending_username": "dessert",
      "patient_age": 10}, {"patient_age": int}, [], ("", 200)),
    ({"attending_username": "Smith.J"},
     {"attending_username": str}, ["key not there"],
     ("required key not present", 400)),
    ({"attending_username": 1,
      "attending_email": "dr_user_id@yourdomain.com"},
     {"attending_username": str,
      "attending_email": str,
      "attending_phone": str},
     ["attending_username"], ("value type not valid", 400)),
    ({"patient_id": 1, "heart_rate": 400},
     {"patient_id": int, "heart_rate": int},
     ["patient_id", "heart_rate"], ("", 200))
])
def test_validateInput(inputTest, inputValid, reqKeys, expectedOut):
    msg, err = pms.validate_input(inputTest, inputValid, reqKeys)
    assert msg == expectedOut[0] and err == expectedOut[1]


@pytest.mark.parametrize("indata, inDictEntries, expectedOut", [
    ({"patient_id": 1,
      "attending_username": "dessert",
      "patient_age": 10}, {"patient_id": int,
                           "attending_username": str,
                           "patient_age": int}, {"patient_id": 1,
                                                 "attending_username":
                                                     "dessert",
                                                 "patient_age": 10}),
    ({"patient_id": "1",
      "attending_username": "dessert",
      "patient_age": 10}, {"patient_id": int,
                           "attending_username": str,
                           "patient_age": int}, {"patient_id": 1,
                                                 "attending_username":
                                                     "dessert",
                                                 "patient_age": 10}),
    ({"attending_username": "dessert",
      "patient_age": "10a"}, {"patient_id": int,
                              "attending_username": str,
                              "patient_age": int}, {"attending_username":
                                                    "dessert",
                                                    "patient_age": "10a"}),
    ({"patient_id": "123",
      "attending_username": "dessert",
      "patient_age": 10}, {"patient_id": int}, {"patient_id": 123,
                                                "attending_username":
                                                    "dessert",
                                                "patient_age": 10}),
    ({"patient_id": "123",
      "attending_username": 123,
      "patient_age": 10}, {"patient_id": int,
                           "attending_username": str}, {"patient_id": 123,
                                                        "attending_username":
                                                            "123",
                                                        "patient_age": 10}),
    ({"patient_id": "123",
      "attending_username": 123,
      "ECG_image": "10",
      "ECG_hr": 10}, {"patient_id": int,
                      "ECG_image": str,
                      "ECG_hr": int}, {"patient_id": 123,
                                       "attending_username": 123,
                                       "ECG_image": "10",
                                       "ECG_hr": 10}),
])
def test_attemptFixInput(indata, inDictEntries, expectedOut):
    outD = pms.attemptFixInput(indata, inDictEntries)
    assert outD == expectedOut


def test_getECGPlotImage():
    import ecg
    # if image file exists already, delete it
    filename_exp = "cache/tempPlotData.jpg"
    filenameTrue = "cache/tempPlotData_true.jpg"
    if os.path.isfile(filename_exp):
        os.remove(filename_exp)
    if os.path.isfile(filenameTrue):
        os.remove(filenameTrue)
    times, voltages = ecg.input_data("test_data1.csv")
    plt.clf()
    plt.plot(times, voltages)
    if not os.path.isdir("cache"):
        os.mkdir("cache")
    plt.savefig(filenameTrue)
    filename = pms.getECGPlotImage(times, voltages)
    assert filename == "cache/tempPlotData.jpg"
    assert os.path.isfile(filename)
    answer = filecmp.cmp(filenameTrue,
                         filename_exp)
    if answer:
        assert True
    else:
        assert False
    os.remove(filename)
    os.remove(filenameTrue)


def test_convert_image_file_to_string():
    expected_str = "/9j/4AAQSkZJRgABAQEAZABk" \
                   "AAD/2wBDAAgGBgcGBQgHBwcJ" \
                   "CQgKDBQNDAsLDBkSEw8UHRofH" \
                   "h0aHBwgJC4nICI"
    filename = "test_data/test_image.jpg"
    strOut = pms.convert_image_file_to_string(filename)
    assert strOut[0:len(expected_str)] == expected_str


filename2 = "test_data/test_image.jpg"
b64string2 = pms.convert_image_file_to_string(filename2)
nd = pms.convert_string_to_ndarray(b64string2)


def test_convert_string_to_ndarray():
    answer = nd[0][0:5]
    expected = [[255, 255, 255],
                [255, 255, 255],
                [255, 255, 255],
                [255, 255, 255],
                [255, 255, 255]]
    assert (answer == expected).all


def test_convert_image_in_ndarray_to_string():
    expected_str2 = "iVBORw0KGgoAAAANSUhEUgAAAoAAA"
    string = pms.convert_image_in_ndarray_to_string(nd)
    assert string[0:len(expected_str2)] == expected_str2


def test_convert_string_to_image_file():
    b64str = pms.convert_image_file_to_string("test_data/test_image.jpg")
    pms.convert_string_to_image_file(b64str, "test_data/test_image_output.jpg")
    answer = filecmp.cmp("test_data/test_image.jpg",
                         "test_data/test_image_output.jpg")
    os.remove("test_data/test_image_output.jpg")
    if answer:
        assert True
    else:
        assert False


@pytest.mark.parametrize("patient_id, expected", [
    ("123s", ("Patient id was not a valid integer", 400)),
    ("123", ("Patient id does not exist in database", 400)),
    ("456", (456, 200))])
def test_validate_patient_id(patient_id, expected):
    # clearDB()
    p = pms.add_new_patient(456)
    # time.sleep(5)
    answer = pms.validate_patient_id(patient_id)
    assert answer == expected
    p.delete()


def test_find_patient():
    # clearDB()
    p = pms.add_new_patient(888)
    # time.sleep(5)
    patient = Patient.objects.raw({"_id": 888}).first()
    answer = pms.find_patient(888)
    answer2 = pms.find_patient(887)
    assert answer == patient
    if answer2:
        assert False
    p.delete()


def test_ECGdriver():
    import ecg
    times, voltages = ecg.input_data("test_data1.csv")
    # get true values
    filename_Truth = "test_data/test_image.jpg"
    times2, voltages2 = ecg.remove_non_numbers(times, voltages, "")
    voltages2 = ecg.above_three_hundred(voltages2, "")
    samp_rate = ecg.sampling_rate(times2)
    filtered = ecg.filtering(samp_rate, voltages2)
    num_beats, beats, mean_hr_bpm = ecg.peak_detection(filtered, times2)
    plt.clf()
    plt.plot(times2, filtered)
    if not os.path.isdir("cache"):
        os.mkdir("cache")
    plt.savefig(filename_Truth)
    b64str = pms.convert_image_file_to_string(filename_Truth)
    # get exp values
    hr, expStr = pms.ECGdriver(times, voltages)
    assert mean_hr_bpm == hr
    assert expStr == b64str


@pytest.mark.parametrize("new_dict, expected", [
    ({"name": "Rachel", "number": 788}, "New patient added to database"),
    ({"name": "Grace", "number": 556, "medical_image": ""},
     "Patient info added to database")])
def test_is_patient_new(new_dict, expected):
    # clearDB()
    p = pms.add_new_patient(556)
    q = pms.add_new_patient(123)
    # time.sleep(5)
    answer, r = pms.is_patient_new(new_dict)
    assert answer == expected
    p.delete()
    q.delete()
    r.delete()


@pytest.mark.parametrize("indata, inDictEntries, reqKeys, expected", [
    ({"name": "Rachel",
      "ECG_image": "ya",
      "ECG_hr": 1}, {"name": str, "number": int, "ECG_image": str,
                     "ECG_hr": int, "medical_image": str}, ["number"],
     ("required key not present", 400)),
    ({"name": "Grace", "number": 123, "medical_image": ""},
     {"name": str, "number": int, "ECG_image": str, "ECG_hr": int,
      "medical_image": str},
     ["number"], ("New patient added to database", 200)),
    ({"name": "Cassidy", "number": 556,
      "ECG_image": "ya", "ECG_hr": 1}, {"name": str, "number": int,
                                        "medical_image": str},
     ["number"], ("Patient info added to database", 200)),
    ({"name": "Emma", "number": "123"}, {"name": str, "number": int,
                                         "medical_image": str},
     ["number"], ("New patient added to database", 200)),
    ({"name": "Emma", "number": "123s"}, {"name": str, "number": int,
                                          "medical_image": str},
     ["number"], ("value type not valid", 400))])
def test_modify_indata(indata, inDictEntries, reqKeys, expected):
    # clearDB()
    p = pms.add_new_patient(556)
    # time.sleep(5)
    answer, code, pat = pms.modify_indata(indata, inDictEntries, reqKeys)
    assert answer == expected[0]
    assert code == expected[1]
    p.delete()
    if type(pat) != str:
        pat.delete()


def test_get_medImages():
    # clearDB()
    firstECG_image = "Fake64bitEncoding"
    firstECG_heartRate = 60
    p = pms.add_new_patient(123)
    pms.add_patient_info({"number": 123, "name": "Grace",
                          "ECG_image": firstECG_image,
                          "ECG_hr": firstECG_heartRate,
                          "medical_image": "ok"})
    in_data = {"number": 123, "index": 1}
    # time.sleep(5)
    imgs, err = pms.get_medImages(in_data)
    assert err == 200
    assert imgs == ["ok"]
    p.delete()


def test_get_ECGImg():
    # clearDB()
    firstECG_image = "Fake64bitEncoding"
    firstECG_heartRate = 60
    p = pms.add_new_patient(123)
    pms.add_patient_info({"number": 123, "name": "Grace",
                          "ECG_image": firstECG_image,
                          "ECG_hr": firstECG_heartRate,
                          "medical_image": "ok"})
    patient = Patient.objects.raw({"_id": 123}).first()
    times = patient.ECG_dateTimes
    in_data = {"number": 123, "timestamp": times[0]}
    # time.sleep(5)
    dictR, err = pms.get_ECGImg(in_data)
    assert err == 200
    assert dictR['ECG_image'] == "Fake64bitEncoding"
    assert dictR['HR'] == 60
    p.delete()


def test_get_MedicalImg():
    # clearDB()
    firstECG_image = "Fake64bitEncoding"
    firstECG_heartRate = 60
    p = pms.add_new_patient(123)
    pms.add_patient_info({"number": 123, "name": "Grace",
                          "ECG_image": firstECG_image,
                          "ECG_hr": firstECG_heartRate,
                          "medical_image": "ok"})
    pms.add_patient_info({"number": 123, "name": "GraceD",
                          "medical_image": "okThere"})
    # patient = Patient.objects.raw({"_id": 123}).first()
    in_data = {"number": 123, "index": 1}
    # time.sleep(5)
    img, err = pms.get_MedicalImg(in_data)
    print(img)
    assert err == 200
    assert img == "okThere"
    p.delete()


def test_get_n_hr_ECG():
    # clearDB()
    firstECG_image = "Fake64bitEncoding"
    firstECG_heartRate = 60
    secondECG_image = "Fake64bitEncoding2"
    secondECG_heartRate = 90
    p = pms.add_new_patient(123)
    pms.add_patient_info({"number": 123, "name": "Grace",
                          "ECG_image": firstECG_image,
                          "ECG_hr": firstECG_heartRate,
                          "medical_image": "ok"})
    pms.add_patient_info({"number": 123, "name": "Grace",
                          "ECG_image": secondECG_image,
                          "ECG_hr": secondECG_heartRate})
    # time.sleep(5)
    # patient = Patient.objects.raw({"_id": 123}).first()
    indata = {"number": 123, "index": 1}
    # dict = {"name": name, "latest_heart_rate": latest_heart_rate,
    #         "ECG_image": ECG_image}
    dict, code = pms.get_n_hr_ECG(indata)
    assert code == 200
    assert dict["name"] == "Grace"
    assert dict["latest_heart_rate"] == 90
    assert dict["ECG_image"] == "Fake64bitEncoding2"
    p.delete()


def test_get_medical_record_numbers():
    # clearDB()
    p = pms.add_new_patient(123)
    q = pms.add_new_patient(124)
    r = pms.add_new_patient(125)
    # time.sleep(5)
    answer = pms.get_medical_record_numbers()
    expected = ([123, 124, 125], 200)
    assert answer == expected
    p.delete()
    q.delete()
    r.delete()


def test_get_ECG_image_timestamps():
    # clearDB()
    firstECG_image = "Fake64bitEncoding"
    firstECG_heartRate = 60
    p = pms.add_new_patient(123)
    # time.sleep(5)
    pms.add_patient_info({"number": 123, "name": "Grace",
                          "ECG_image": firstECG_image,
                          "ECG_hr": firstECG_heartRate, "medical_image": "ok"})
    patient = Patient.objects.raw({"_id": 123}).first()
    times = patient.ECG_dateTimes
    indata = {"number": 123}
    ECG_timestamps, err = pms.get_ECG_image_timestamps(indata)
    assert err == 200
    assert ECG_timestamps == times
    p.delete()


@pytest.mark.parametrize("indata, event, expectedOut", [
    ({"number": 1234}, "new_patient", "Added new patient "
                                      "with medical record number: 1234"),
    ({"number": 2920,
      "name": "dessert",
      "ECG_image": "10", "ECG_hr": 10}, "new_info",
     "Added or updated the following information for patient with "
     "record number: 2920: name, ECG_image, ECG_hr"),
    ({"number": 2920,
      "medical_image": "dessert"}, "new_info",
     "Added or updated the following information for patient with "
     "record number: 2920: medical_image"),
    ({"number": 2920}, "new_info",
     "Added or updated the following information for patient with "
     "record number: 2920: "),
    ({"number": "Smith.J"}, "new_physician",
     "Invalid logging event type!"),
    ({"case": 1}, "get_info", (1, "")),
    ({"case": 2, "number": 123}, "get_info",
     (2, "for patient with record number: 123")),
    ({"case": 3, "number": 123}, "get_info",
     (3, "for patient with record number: 123")),
    ({"case": 4, "number": 123}, "get_info",
     (4, "for patient with record number: 123")),
    ({"case": 5, "number": 123}, "get_info",
     (5, "for patient with record number: 123")),
    ({"case": 6, "number": 123}, "get_info",
     (6, "for patient with record number: 123"))
])
def test_logInfo(indata, event, expectedOut):
    if event == "get_info":
        firstECG_image = "Fake64bitEncoding"
        firstECG_heartRate = 60
        p = pms.add_new_patient(123)
        pms.add_patient_info({"number": 123, "name": "Grace",
                              "ECG_image": firstECG_image,
                              "ECG_hr": firstECG_heartRate,
                              "medical_image": "ok"})
        caseStrs = ["medical record numbers", "latest "
                                              "ECG image and heart rate",
                    "timestamps of all ECG entries",
                    "encodings of all medical images",
                    "string encoding and heart rate for a specific ECG",
                    "string encoding for a specific medical image"]
        expectedOutS = "Retrieved " + caseStrs[expectedOut[0] - 1]
        if "number" in indata:
            expectedOutS = expectedOutS + expectedOut[1]
        expectedOut = expectedOutS
    with LogCapture() as log_c:
        pms.logInfo(indata, event)
    if expectedOut == "":  # check that no log entries
        log_c.check()
    else:  # check that correct log entries.
        log_c.check(("root", "INFO", expectedOut))
    if event == "get_info":
        p.delete()


def clearDB():
    """Clear MongoDB patient database
    Remove all entries from the patient database.
    :return: none
    """
    a = Patient.objects.raw({})
    for patient in a:
        patient.delete()


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
    logging.basicConfig(filename="patientMonitoringServer.log",
                        level=logging.DEBUG)
    print("Connecting to MongoDB...")
    connect("mongodb+srv://dessertgrace:"
            "youcan@bme547.allsv.mongodb."
            "net/myFirstDatabase?retryWrites="
            "true&w=majority")
    print("Connection attempt finished.")


if __name__ == '__main__':
    clearDB()
    initialize_server()
    clearDB()
