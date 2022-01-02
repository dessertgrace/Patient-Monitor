import pytest
import patient_GUI as pg
import patientMonitoringServer as pms
import os.path
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from pymodm import connect, MongoModel, fields
import ssl

pms.initialize_server()

connect("mongodb+srv://dessertgrace:"
        "youcan@bme547.allsv.mongodb."
        "net/myFirstDatabase?retryWrites="
        "true&w=majority", ssl_cert_reqs=ssl.CERT_NONE)

filename = "test_data11.csv"
expected1, expected2 = pg.get_ECG_data("test_data11.csv")
print(expected2)


@pytest.mark.parametrize("filename, expected1, expected2", [
    ("test_data11.csv", 69.12691269126913, "cache/tempPlotData.jpg")])
def test_get_ECG_data(filename, expected1, expected2):
    mean_hr_bpm, filename = pg.get_ECG_data(filename)
    assert mean_hr_bpm == expected1
    assert filename == expected2


filename2 = "images/blank.jpg"
medical_image = Image.open(filename2)
original_size = medical_image.size
resized_image = medical_image.resize((200, 200))
new_size = resized_image.size
assert (200, 200) == new_size


if __name__ == "__main__":
    pms.clearDB()
