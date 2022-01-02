import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import filedialog
from patient_client import add_new_info_to_server
from ecg import input_data
import patientMonitoringServer
from patientMonitoringServer import ECGdriver
from patientMonitoringServer import convert_string_to_ndarray
from patientMonitoringServer import display_image_in_ndarray
from patientMonitoringServer import convert_string_to_image_file
from patientMonitoringServer import getECGPlotImage
from patientMonitoringServer import convert_image_file_to_string
from ecg import input_data, remove_non_numbers, above_three_hundred
from ecg import sampling_rate, filtering
import os.path
import ssl
from pymodm import connect, MongoModel, fields
import base64
global img_string
global img_string2


connect("mongodb+srv://dessertgrace:"
        "youcan@bme547.allsv.mongodb."
        "net/myFirstDatabase?retryWrites="
        "true&w=majority", ssl_cert_reqs=ssl.CERT_NONE)


def load_and_resize_image(filename):
    """Converts the image file to a b64 string and a
    tk image variable

    This function first converts the image file to a b64 string
    that is returned and sent to the server. Next, the image is
    opened, stored as a Pillow image, and resized. The
    resized image is then converted to a tk image and returned
    for display on the GUI, along with the b64 string.

    :param filename: JPG file selected from the local computer
    :return: Resized tk image to be displayed on the GUI
    :return: b64 string encoding the JPG file
    """
    img_string = convert_image_file_to_string(filename)
    medical_image = Image.open(filename)
    original_size = medical_image.size
    #  adj_factor = 0.2
    #  new_width = round(original_size[0] * adj_factor)
    #  new_height = round(original_size[1] * adj_factor)
    width = 200
    height = 200
    #  resized_image = medical_image.resize((new_width, new_height))
    resized_image = medical_image.resize((width, height))
    tk_image = ImageTk.PhotoImage(resized_image)
    #  print(tk_image)
    return tk_image, img_string


def get_ECG_data(ECG_file):
    """Gets the average heart rate and filename from
    the ECG file selected on the local computer

    This function takes in the ECG file selected on the local
    computer, calls a number of functions from ecg.py to
    determine the average heart rate of the selected file, then
    calls getECGPlotImage from patientMonitoringServer.py to
    plot the ECG trace of the selected file and save it as a JPG.
    It returns the filename of this JPG and the average heart
    rate to be displayed on the GUI.

    :param ECG_file: test_data file selected from the local computer,
        containing voltage and time data for a given ECG trace
    :return: int containing the average heart rate of the selected
    ECG file
    :return: JPG file containing the ECG trace image to be displayed
        on the GUI
    """
    times, voltages = input_data(ECG_file)
    mean_hr_bpm, stringECGImg = ECGdriver(times, voltages)
    #  print("Heart Rate: {:0.2f} bpm".format(mean_hr_bpm))
    times2, voltages2 = remove_non_numbers(times, voltages, ECG_file)
    voltages2 = above_three_hundred(voltages2, ECG_file)
    samp_rate = sampling_rate(times2)
    filtered = filtering(samp_rate, voltages2)
    filename = getECGPlotImage(times2, filtered)
    #  print(filename)
    #  mean_hr_bpm = str(mean_hr_bpm)
    #  mean_hr_bpm = "{:.2f}".format(mean_hr_bpm)
    return mean_hr_bpm, filename


def design_window():
    """Creates the main GUI window for the patient database

    A GUI window is created that is the main interface for the patient
    database. It accepts information from the user (patient name,
    medical record number, average heart rate, ECG image trace, and
    medical image. Upon hitting the Ok button, this information is sent
    to the server.  Upon hitting the Cancel button, the window closes.

    :return: None
    """
    global img_string
    global img_string2
    img_string = ""
    img_string2 = ""

    def ok_button_cmd():
        """Event to run when Ok button is pressed

        This function is connected to the "Ok" button of the GUI. It
        carries out the following steps:
        1. It gets the needed information from the GUI.
        2. It calls a function external to the GUI to process the data and
        receive the results
        3. It updates the GUI based on the received results.  In this case,
        that includes printing to the console and updating a Label in the GUI.

        :return: None
        """
        global img_string
        global img_string2
        #  Get needed data from GUI#
        name = name_data.get()
        record = record_data.get()
        medical_image = img_string
        #  print(medical_image[20:30])
        #  print(medical_image)
        ECG_image = img_string2
        heart_rate = HR_label.hr
        if heart_rate:
            heart_rate = int(round(heart_rate))
            print(heart_rate)
        #  print(ECG_image)
        #  Call external function to do the work that can be tested
        answer = add_new_info_to_server(record, name=name,
                                        heart_rate=heart_rate,
                                        medical_image=medical_image,
                                        ECG_image=ECG_image)
        #  Update GUI about what happened at server
        #  print(out_string)
        output_string.configure(text=answer)

    def cancel_button_cmd():
        """Closes window upon click of Cancel button

        This function is connected to the "Cancel" button of the GUI.  It
        destroys the root window causing the GUI interface to close.

        :return: None
        """
        root.destroy()

    def select_img_cmd():
        """Allows user to select an image to display

        Upon selecting the "Select Image" button on the GUI
        and choosing an image from the local computer,
        the image file will be opened, loaded and resized,
        and the label will be changed to reflect the updated image.
        The updated image is set to a tk image variable to be
        displayed on the GUI.

        :return: None
        """
        global img_string
        global img_string2
        filename = filedialog.askopenfilename()
        if filename == "":
            return
        tk_image, img_string = load_and_resize_image(filename)
        #  print(img_string[20:30])
        image_label.configure(image=tk_image)
        image_label.image = tk_image

    def select_ECG_cmd():
        """Allows user to select an ECG file to display patient's
        average heart rate and ECG trace.

        Upon selecting the "Select ECG File" button on the GUI
        and choosing a file from the local computer, the file
        will be opened and get_ECG_data will be called to determine
        the mean heart rate and JPG filename. The image is then
        resized and the label will be changed to reflect the updated
        image. The heart rate label on the GUI will also be updated
        to reflect the selected patient's heart rate.

        :return: None
        """
        global img_string
        global img_string2
        ECG_file = filedialog.askopenfilename()
        mean_hr_bpm, filename = get_ECG_data(ECG_file)
        if ECG_file == "":
            return
        new_tk_image, img_string2 = load_and_resize_image(filename)
        #  new_img_obj = Image.open(filename)
        #  new_tk_image = ImageTk.PhotoImage(resized_image)
        ECG_image_label.image = new_tk_image
        ECG_image_label.configure(image=new_tk_image)
        HR_label.configure(text="Heart Rate: {:0.2f} bpm".format(mean_hr_bpm))
        HR_label.hr = mean_hr_bpm

    root = tk.Tk()
    root.title("Patient Side GUI")

    ttk.Label(root, text="Patient Information").grid(column=0, row=0,
                                                     sticky="NSWE",
                                                     pady=10, padx=5)

    ttk.Label(root, text="Medical Record Number:").grid(column=0,
                                                        row=1,
                                                        sticky='e',
                                                        pady=30,
                                                        padx=5)
    record_data = tk.StringVar()
    record_entry_box = ttk.Entry(root, width=10, textvariable=record_data)
    record_entry_box.grid(column=1, row=1, sticky='w')

    ttk.Label(root, text="Name:").grid(column=0, row=2, sticky='e',
                                       pady=10, padx=5)
    name_data = tk.StringVar()
    name_entry_box = ttk.Entry(root, width=30, textvariable=name_data)
    name_entry_box.grid(column=1, row=2, sticky='')

    cancel_button = ttk.Button(root, text="Cancel", command=cancel_button_cmd)
    cancel_button.grid(column=3, row=10, sticky='se', pady=10, padx=10)

    ok_button = ttk.Button(root, text="Ok", command=ok_button_cmd)
    ok_button.grid(column=3, row=8, sticky='se', padx=10)
    output_string = ttk.Label(root)
    output_string.grid(column=2, row=5)

    tk_image, img_string3 = load_and_resize_image("images/blank.jpg")
    #  print(img_string3[20:30])
    image_label = ttk.Label(root, image=tk_image)
    image_label.grid(column=0, row=5, sticky='s', pady=10, padx=10)
    select_img_button = ttk.Button(root, text="Select Image",
                                   command=select_img_cmd)
    select_img_button.grid(column=0, row=8, pady=10)

    tk_image2, img_string4 = load_and_resize_image("images/blank.jpg")
    ECG_image_label = ttk.Label(root, image=tk_image2)
    ECG_image_label.image = tk_image2
    ECG_image_label.grid(column=1, row=5, pady=10, padx=10)
    select_ECG_button = ttk.Button(root, text="Select ECG File",
                                   command=select_ECG_cmd)
    select_ECG_button.grid(column=1, row=8)

    HR_label = ttk.Label(root)
    HR_label.grid(column=1, row=6, pady=10)
    HR_label.hr = None

    root.mainloop()


if __name__ == "__main__":
    design_window()
    #  get_ECG_data("test_data11.csv")
    #  load_and_resize_image("images/blank.jpg")
