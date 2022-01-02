import base64
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import asksaveasfile

import requests
import patientMonitoringServer as pms
import io
from skimage.io import imsave
from PIL import ImageTk, Image
import pmsClient as pmsC

# global vars
global pats
global currECGTsAvail
global currPatsAvail
global currPatNum
global currPatNumOld
currPatNumOld = None
currPatNum = None
global latestECGstrImg
latestECGstrImg = None
global selectedECGstrImg
selectedECGstrImg = None
global medStrImg
medStrImg = None
currECGTsAvail = []
currPatsAvail = []
currMedITsAvail = []


def design_window():
    """Creates the main GUI window for patient monitoring

    It gets information from the patient info database (name, id,
    ECG images & corresponding heart rates, and medical images),
    allows the user to select from available patients and patient
    images, and displays the information to the user.
    Upon hitting one of two "download image" buttons, the user can
    download the displayed images to their device.

    Returns: None
    """

    def downloadECG():
        """When the download button is clicked for the
        selected ECG image, download the current selected ECG image

        If the 'selectedECGstrImg' global variable exists,
        meaning the image is not
        blank, save the image by calling saveImg, and display to the
        output label 'Image saved!'
        If not, display that you cannot save a blank image
        to the output label.

        :return: None
        """
        if selectedECGstrImg:
            imStr = selectedECGstrImg
            saveImg(imStr)
            outputMsgL['text'] = "Image saved!"
        else:
            outputMsgL['text'] = "Cannot save blank image! " \
                                 "Please select image first."

    def downloadLatestECG():
        """When the download button is clicked for the
        latest ECG, download the latest ECG image

        If the 'latestECGstrImg' global variable exists, meaning
        the image is not
        blank, save the image by calling saveImg, and display to the
        output label 'Image saved!'
        If not, display that you cannot save a blank image
        to the output label.

        :return: None
        """
        if latestECGstrImg:
            imStr = latestECGstrImg
            saveImg(imStr)
            outputMsgL['text'] = "Image saved!"
        else:
            outputMsgL['text'] = "Cannot save blank image! " \
                                 "Please select image first."

    def downloadMed():
        """When the download button is clicked in the
        medical image frame, download the current medical image

        If the 'medStrImg' global variable exists, meaning the image is not
        blank, save the image by calling saveImg, and display to the
        output label 'Image saved!'
        If not, display that you cannot save a blank image
        to the output label.

        :return: None
        """
        if medStrImg:
            imStr = medStrImg
            saveImg(imStr)
            outputMsgL['text'] = "Image saved!"
        else:
            outputMsgL['text'] = "Cannot save blank image! " \
                                 "Please select image first."

    def saveImg(imStr):
        """Save an image to the local computer

        Given a string encoding of an image, use the asksaveasfile()
        function to get a file. If the file exists, save the image
        to the filename by decoding the base64 string.

        :param imStr: a 64-bit string encoding of an image
        :return: None
        """
        filet = (('JPEG', ('*.jpg', '*.jpeg', '*.jpe', '*.jfif')),
                 ('PNG', '*.png'), ('BMP', ('*.bmp', '*.jdib')),
                 ('GIF', '*.gif'))
        # asksaveasfile()  #  initialdir="/",
        file = asksaveasfile(title="Select file",
                             filetypes=filet, defaultextension=filet)
        if file:
            fn = file.name
            image_bytes = base64.b64decode(imStr)
            with open(fn, "wb") as out_file:
                out_file.write(image_bytes)
            # file.close()

    def selectedECG_changed(ok):
        """When ECG is selected, display the image, HR, and datetime

        After the event of selecting an ECG timestamp,
        get the string 64-bit encoding of the ECG image and the
        corresponding heart rate by
        calling the client function 'getInfo()' with case number 5,
        giving the current patient number and the timestamp selected
        in the combobox (selectECG).
        Display this image by first converting to an ndarray and
        then calling the dispImageGivenND function
        on the 'selectedECG' image label.
        Then, update the heart rate and datetime labels (selectedHRL
        and selectedDTL)

        :param ok: TK event. Not used.
        :return: None
        """
        global currECGTsAvail, currPatNum, selectedECGstrImg
        currECGT = currECGTsAvail[selectECG.current()]
        inputD = {"number": int(currPatNum), "timestamp": currECGT}
        dictR, errcode = pmsC.getInfo(5, inputD)
        selectedECGstrImg = dictR['ECG_image']
        hr = dictR['HR']
        img_ndarray = pms.convert_string_to_ndarray(selectedECGstrImg)
        dispImageGivenND(img_ndarray, selectedECG)
        selectedHRL['text'] = str(hr)
        selectedDTL['text'] = currECGT

    def selectedMedI_changed(ok):
        """When medical image is selcted, display that image

        After the event of selecting a medical image,
        get the string 64-bit encoding of that image by indexing
        the global 'currMedITsAvail' list of encodings with the
        integer version of the current index selected in
        the 'selectMed' combobox. Then, convert this string
        to an ndarray and display it using the 'dispImageGivenND'
        function on the 'selectedMedI' image label.

        :param ok: TK event. Not used.
        :return: None
        """
        global currMedITsAvail, medStrImg
        strImg = currMedITsAvail[int(selectMed.current())]
        img_ndarray = pms.convert_string_to_ndarray(strImg)
        dispImageGivenND(img_ndarray, selectedMedI)
        medStrImg = currMedITsAvail[int(selectMed.current())]

    def quitGUI():
        """Quit the GUI

        This function quits the GUI by calling root.destroy()

        :return: none
        """
        root.destroy()

    def selectedPat_changed(event):
        """When the selected patient is changed, update patient information

        Update the 'currPatNum' current patient number global variable,
        clear the selected ECG and medical image fields, as well as the
        selected ECG information fields.
        Call updatePatInfo() to update the ECG and medical image selection
        options as well as the latest ECG image and information fields.

        :param event: event of the changed patient selection.
            This is not used.
        :return: None
        """
        global currPatNum, selectedECGstrImg, medStrImg, currPatNumOld
        currPatNum = int(currPatsAvail[int(selectPat.current())])

        if currPatNum < 0:
            return

        if currPatNumOld:
            if currPatNumOld == currPatNum:
                # if patient number hasn't changed, don't update everything
                return

        updatePatInfo()

        # clear selected ECG and medical image fields
        image_objR = Image.open('images/blank_imgR.jpg')
        tk_image = ImageTk.PhotoImage(image_objR)
        selectedECG.image = tk_image
        selectedECG.configure(image=tk_image)
        selectedMedI.image = tk_image
        selectedMedI.configure(image=tk_image)
        selectedHRL['text'] = ""
        selectedDTL['text'] = ""
        # clear the string images so they cannot be saved
        selectedECGstrImg = None
        medStrImg = None

        currPatNumOld = currPatNum

    def updatePatInfo():
        global currECGTsAvail, currMedITsAvail, latestECGstrImg
        """Update the current patient information in the GUI

        Given the current patient number, make function calls
        from the client file to get information from the database.
        Get the patient name, and update it on the GUI in the
        pNameL label. Also update the current patient medical record
        number on the GUI in the pNumL label.
        Get all ECG timestamps for the current patient and update
        the combobox values (combobox selectECG).
        Get all medical images for the current patient and update
        the combobox values to be the valid indices (combobox selectMed).
        Update the output label with the number of ECG images and
        medical images found for the current patient.
        If ECGs are found, update the latest ECG fields including
        the latest ECG image (latestECG label) and the latest
        heart rate (latestHRL) and datetime of that entry (latestDTL).
        If no ECGs are found, display a blank image on the latest
        ECG image label (latestECG).

        :return: None
        """
        # Get patient name
        inputD = {"number": currPatNum}
        dict, errcode = pmsC.getInfo(2, inputD)
        name = dict['name']

        # change name, number
        pNameL['text'] = name
        pNumL['text'] = str(currPatNum)

        # get all ECG timestamps
        inputD = {"number": currPatNum}
        currECGTsAvail, errcode = pmsC.getInfo(3, inputD)

        # update selection options for available ECGs
        selectECG['values'] = currECGTsAvail
        selectECG.set("")

        # get avail med images
        patI = {"number": currPatNum}
        currMedITsAvail, errCode = pmsC.getInfo(4, patI)

        # update combobox of avail med images
        selectMed['values'] = [str(i) for i in range(len(currMedITsAvail))]
        selectMed.set("")

        # update output label
        outstr = str(len(currECGTsAvail))
        outstr = outstr + " ECG entries found and "
        outstr = outstr + str(len(currMedITsAvail)) + " medical images found."
        outputMsgL['text'] = outstr

        # if ECGs are found, update latest ECG fields
        if len(currECGTsAvail) > 0:
            # get latest ECG as str64
            patI = {"number": currPatNum}
            latestECGdict, errCode = pmsC.getInfo(2, patI)

            # display latest ECG
            latestECGstrImg = latestECGdict["ECG_image"]
            img_ndarray = pms.convert_string_to_ndarray(latestECGstrImg)
            dispImageGivenND(img_ndarray, latestECG)

            # display HR
            latestHRL['text'] = str(latestECGdict["latest_heart_rate"])
            # display DT
            latestDTL['text'] = currECGTsAvail[-1]
        else:
            # if no ECGs are found, display a blank image
            # and clear the latestECGstrImg so it cannot be saved
            latestECGstrImg = None
            image_objR = Image.open('images/blank_imgR.jpg')
            tk_image = ImageTk.PhotoImage(image_objR)
            latestECG.image = tk_image
            latestECG.configure(image=tk_image)
            latestHRL['text'] = ""
            latestDTL['text'] = ""

    def dispImageGivenND(img_ndarray, my_img_labelL):
        """Display image in given TK image label

        Given an image as an nd-array, convert it to a PIL
        image object, resize it to have a width of 200,
        and display it in the given image label.

        :param img_ndarray: image as nd-array
        :param my_img_labelL: Tinker image label to configure
        :return: None
        """
        f = io.BytesIO()
        imsave(f, img_ndarray, plugin='pil')
        out_img = io.BytesIO()
        out_img.write(f.getvalue())
        img_obj = Image.open(out_img)
        newWidth = 200
        newHeight = img_obj.size[1] / img_obj.size[0] * newWidth
        img_objR = img_obj.resize((int(newWidth), int(newHeight)))
        tk_image = ImageTk.PhotoImage(img_objR)
        my_img_labelL.image = tk_image
        my_img_labelL.configure(image=tk_image)

    def updateGlobals():
        """Update the information displayed on the GUI to reflect
        the current information in the database.

        Get the current patient medical record numbers in the database
        using the client function getInfo() with case 1.
        If the patient number options are different from before
        display the number of patients found on the output label.
        If we have a current patient selected, call the 'updatePatInfo'
        function to update the ECG information and selection options for
        ECGs and medical images.
        Run this function repetitively every 10 seconds.

        :return: None
        """
        global currPatsAvail, currPatNumOld
        currPatsAvailNew, errCode = pmsC.getInfo(1, {})
        selectPat["values"] = currPatsAvailNew
        if currPatsAvailNew != currPatsAvail:
            outputMsgL['text'] = str(len(currPatsAvailNew)) + " patients found"
            currPatsAvail = currPatsAvailNew

        if currPatNum:
            currPatNumOld = currPatNum
            updatePatInfo()

        root.after(30000, updateGlobals)  # run again after 30 seconds

    root = tk.Tk()
    root.title("Patient Monitoring GUI")
    root.geometry('950x750')
    root.config(bg="grey")
    # root.columnconfigure(tuple(range(2)), weight=1)
    # root.rowconfigure(tuple(range(2)), weight=1)

    # set up patient selection frame with grid
    patFrame = tk.Frame(root, width=800, height=200, bg='white')
    patFrame.grid(column=0, row=0, padx=5, pady=5, sticky='NW')
    # patFrame.columnconfigure(tuple(range(3)), weight=1)
    # patFrame.rowconfigure(tuple(range(3)), weight=1)

    # set up ECG Frame with grid
    ECGframe = tk.Frame(root, width=600, height=300, bg='white')
    ECGframe.grid(column=0, row=1, padx=5, pady=5, sticky='NW', columnspan=3)
    ECGframe.columnconfigure(tuple(range(10)), weight=1)
    ECGframe.rowconfigure(tuple(range(10)), weight=1)

    # set up med record frame with grid
    medRecFrame = tk.Frame(root, width=200, height=300, bg='white')
    medRecFrame.grid(column=4, row=1, padx=5, pady=5, sticky='NW')
    # medRecFrame.columnconfigure(tuple(range(2)), weight=1)
    # medRecFrame.rowconfigure(tuple(range(5)), weight=1)

    # Patient Monitor title
    tk.Label(patFrame, text="Patient Monitor",
             font=('Arial', 16, 'bold'),
             bg="white").grid(column=0,
                              row=0, sticky="NW", padx=5, pady=5)
    # select patient medical record number (0,1)
    ttk.Label(patFrame, text="Select "
                             "Patient Medical Record "
                             "Number:", width=35,
              font=('Arial', 14)).grid(column=0, row=1,
                                       sticky="W", padx=5, pady=5)

    # Select Patient Combobox
    selectedPat_var = tk.StringVar()
    selectPat = ttk.Combobox(patFrame, textvariable=selectedPat_var,
                             width=10)
    selectPat["values"] = currPatsAvail
    selectPat.state(["readonly"])
    selectPat.grid(column=1, row=1, padx=5, pady=5)
    selectPat.bind('<<ComboboxSelected>>', selectedPat_changed)

    # Display patient medical record number (1,0) and (1,1)
    label1 = tk.Label(patFrame, text="Medical Record Number: ")
    label1.grid(column=0, row=2, sticky="W", padx=5, pady=5)
    pNumber = tk.StringVar()
    pNumL = ttk.Label(patFrame, text=pNumber)
    pNumL.grid(column=1, row=2, sticky="W", padx=5, pady=5)
    pNumL['text'] = ""

    # Display patient name (2,3) and (3,3)
    tk.Label(patFrame,
             text="Patient Name: ").grid(column=0,
                                         row=3, sticky="W",
                                         padx=5, pady=5)
    pName = tk.StringVar()
    pNameL = ttk.Label(patFrame, text=pName)
    pNameL.grid(column=1, row=3, sticky="W", padx=5, pady=5)
    pNameL['text'] = ""

    # Display Latest ECG & ECG info
    tk.Label(ECGframe, text="ECG Entries",
             font=('Arial', 16, 'bold'),
             bg="white").grid(column=0,
                              row=0, sticky="NW", padx=5, pady=5)
    ttk.Label(ECGframe, text="Latest ECG:").grid(column=0,
                                                 row=1, sticky="NW",
                                                 pady=5, padx=5)
    # latest ECG image
    image_obj = Image.open("images/blank_imgR.jpg")
    tk_image = ImageTk.PhotoImage(image_obj)
    latestECG = ttk.Label(ECGframe, image=tk_image)
    latestECG.grid(column=0, row=3, padx=5, pady=5)

    # latest ECG HR
    ttk.Label(ECGframe,
              text="Heart Rate:").grid(column=0, row=4,
                                       sticky="W", padx=5, pady=5)
    latestHR = tk.StringVar()
    latestHRL = ttk.Label(ECGframe, text=latestHR)
    latestHRL.grid(column=0, row=5, sticky="E", padx=5, pady=5)
    latestHRL['text'] = ""
    # latest ECG Date & Time (4,6) and (4,7)
    ttk.Label(ECGframe,
              text="Date & Time Uploaded:").grid(column=0, padx=5, pady=5,
                                                 row=6, sticky="W")
    latestDT = tk.StringVar()
    latestDTL = ttk.Label(ECGframe, text=latestDT)
    latestDTL.grid(column=0, row=7, sticky="E", padx=5, pady=5)
    latestDTL['text'] = ""
    # Download Image
    button = ttk.Button(ECGframe, text="Download Image", width=15,
                        command=downloadLatestECG).grid(column=0,
                                                        row=8,
                                                        padx=5, pady=5)

    # Select ECG Combobox [label at (5,4), box at (6,4)]
    # Prompt:
    ttk.Label(ECGframe, text="Select Historical ECG:").grid(column=2,
                                                            row=1,
                                                            sticky="NW",
                                                            pady=5,
                                                            padx=5)
    # ComboBox:
    selectedECG_var = tk.StringVar()
    selectECG = ttk.Combobox(ECGframe, textvariable=selectedECG_var,
                             width=20)
    selectECG["values"] = currECGTsAvail
    selectECG.state(["readonly"])
    selectECG.grid(column=3, row=1, pady=5, padx=5)
    selectECG.bind('<<ComboboxSelected>>', selectedECG_changed)

    # add buffer column
    tk.Label(ECGframe, text="", bg="white").grid(column=1, row=2,
                                                 sticky="W", padx=20)

    # Selected ECG  [label: (5,5), image:
    #   (5,6), info: (5,7), (5,8), (5,9), (5,10)]
    ttk.Label(ECGframe, text="Selected ECG:").grid(column=2,
                                                   row=2, sticky="W",
                                                   padx=5, pady=5)
    # selected ECG image
    tk_imageS = ImageTk.PhotoImage(image_obj)
    selectedECG = ttk.Label(ECGframe, image=tk_imageS)
    selectedECG.grid(column=2, row=3, padx=5, pady=5)

    # selected ECG HR
    ttk.Label(ECGframe,
              text="Heart Rate:").grid(column=2,
                                       row=4, sticky="W", padx=5, pady=5)
    selectedHR = tk.StringVar()
    selectedHRL = ttk.Label(ECGframe, text=selectedHR)
    selectedHRL.grid(column=2, row=5, sticky="E", padx=5, pady=5)
    selectedHRL['text'] = ""
    # selected ECG date & time
    ttk.Label(ECGframe,
              text="Date & Time Uploaded:").grid(column=2, row=6,
                                                 sticky="W", padx=5, pady=5)
    selectedDT = tk.StringVar()
    selectedDTL = ttk.Label(ECGframe, text=selectedDT)
    selectedDTL.grid(column=2, row=7, sticky="E")
    selectedDTL['text'] = ""

    # Download Image
    button = ttk.Button(ECGframe, text="Download Image", width=15,
                        command=downloadECG).grid(column=2, row=8,
                                                  padx=5, pady=5)

    # Medical Image frame title
    tk.Label(medRecFrame, text="Medical Images",
             font=('Arial', 16, 'bold'), bg="white").grid(column=0,
                                                          row=0, sticky="NW",
                                                          padx=5, pady=5)
    # Select medical image
    # Prompt:
    ttk.Label(medRecFrame, text="Select Medical Image:").grid(column=0,
                                                              row=1,
                                                              sticky="NW",
                                                              padx=5,
                                                              pady=5)
    # ComboBox:
    selectedMed_var = tk.StringVar()
    selectMed = ttk.Combobox(medRecFrame, textvariable=selectedMed_var)
    selectMed["values"] = currMedITsAvail
    selectMed.state(["readonly"])
    selectMed.grid(column=0, row=2)
    selectMed.bind('<<ComboboxSelected>>', selectedMedI_changed)

    # Selected Med Image
    ttk.Label(medRecFrame, text="Selected Medical Image:").grid(column=0,
                                                                row=3,
                                                                sticky="W",
                                                                padx=5,
                                                                pady=5)
    # selected ECG image
    tk_imageMed = ImageTk.PhotoImage(image_obj)
    selectedMedI = ttk.Label(medRecFrame, image=tk_imageMed)
    selectedMedI.grid(column=0, row=4)

    # Download Image
    button = ttk.Button(medRecFrame, text="Download Image", width=15,
                        command=downloadMed).grid(column=0, row=5,
                                                  padx=5, pady=5)

    # App Monitor frame Button
    quitFrame = tk.Frame(root, width=100, height=100, bg='white')
    quitFrame.grid(column=0, row=3, sticky="W", padx=5, pady=5)
    # Quit Button
    button = ttk.Button(quitFrame,
                        text="Quit", command=quitGUI).grid(column=0, row=0,
                                                           padx=5, pady=5)

    # output message Label
    outputMsg = tk.StringVar()
    outputMsgL = ttk.Label(quitFrame, text=outputMsg)
    outputMsgL.grid(column=1, row=0, sticky="W", padx=15, pady=5)
    outputMsgL['text'] = ""

    # Get available patients and current patient data
    updateGlobals()

    root.mainloop()


if __name__ == "__main__":
    # check_server_status()
    # pmsC.add_pats_for_test()
    design_window()
