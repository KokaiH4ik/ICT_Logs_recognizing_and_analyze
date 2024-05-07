from gc import disable
from tkinter import filedialog, messagebox
from turtle import position
import PySimpleGUI as sg
from numpy import size
import pandas as pd
import os.path
import subprocess
import sys
import multiprocessing
import time
import pickle
import threading
import re
from Processing import Processing
import io
import base64
from PIL import Image

# Global variable to control animation thread
continue_animation = False
event_filerecognaizng = threading.Event()
stop_animation = threading.Event()

min_width = 700
min_height = 480

prediction_images = []
size_of_prediction_images = 0
current_image=0

bar_striped = b'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'
bar_striped_image = sg.Image(data=bar_striped, enable_events=True, key='-LOADING_ANIMATION-', right_click_menu=['UNUSED', ['Exit']], pad=0, visible=False)

#First column with file list and search button and loading animation
folder_list_column_elements = [
    [
        #find and open documents
        sg.Text("Logs Folder"),
        sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [sg.Checkbox("The data has already been processed",enable_events=True,default=False,key="-Data_Prepared-",disabled=True),
     sg.Push(), sg.Button("Execute Procesing",enable_events=True,key="-Execute_Procesing-",),sg.Push(),
     ],
    #file list
    [sg.Listbox(values=['Chose Working Folder'], enable_events=True, key="-FILE LIST-",expand_x=True, expand_y=True,disabled=True )],
    #progress bar, not used
    #[sg.ProgressBar(100, orientation='h', size=(20, 20), key='-PROGRESS-', visible=False)],
    #loading information
    [bar_striped_image, sg.Text("",enable_events=True,key="-PROGRESS_TEXT-",visible=False),],
]

# Data list
Data_List_column_elements = [
    [sg.Text("Data:"),
     sg.Text("", key="-Quantity-",visible=False)
     ],
     [sg.Button("<-", enable_events=True, key="-Previos-", visible=False),
      sg.Image(data="", key="-PLOT IMAGE-",size=(480,500),visible=False),
      sg.Button("->", enable_events=True, key="-Next-", visible=False)],
     #[sg.Text('Resize to'), sg.In(key='-W-', size=(5,1)), sg.In(key='-H-', size=(5,1))],
    #[sg.Listbox(
     #       values=['Choose a fucntion on left'], enable_events=False, size=(60, 20), key="-PN DATA-",horizontal_scroll=True, expand_x=True, expand_y=True
      #  )]
]


#PN list
function_column_elements = [
    [   sg.Text("Element Name:"),
        sg.In(size=(15,1),enable_events=True,key="-Element_Name-")],
    [sg.Push(),sg.Button("Execute Plotting",enable_events=True,key="-Execute_Plotting-"),sg.Push()],
     [   sg.Text("Prediction Number:"),
        sg.In(size=(15,1),enable_events=True,key="-Prediction_Number-")],
    [sg.Push(),sg.Button("Execute Prediction",enable_events=True,key="-Execute_Prediction-"),sg.Push()],
    [   sg.Text("Procent of Value:"),
        sg.In(size=(15,1),enable_events=True,key="-Procent_Value-",change_submits=True)],
    [sg.Push(),sg.Button("Check Value in Range",enable_events=True,key="-Procent_value_range-"),sg.Push()],
    [sg.VPush()],  # Push the last button to the bottom
    [sg.Push(),sg.Button("Software guide",enable_events=True,key="-Software_guide-"),sg.Push()],
]

folder_list_column = sg.Column(folder_list_column_elements, expand_x=True, expand_y=True)
function_column = sg.Column(function_column_elements, justification='center', expand_x=True, expand_y=True)
data_list_column = sg.Column(Data_List_column_elements, expand_x=True, expand_y=True)


# ----- Full layout -----
layout = [
    [folder_list_column, 
     sg.VSeparator(), 
     function_column, 
     sg.VSeparator(), 
     data_list_column],
]


#Set up the window
window = sg.Window("ICT Data Viewer", layout, resizable=True)

#run animation of loadingvv
def run_animation():
     while continue_animation:
        window['-LOADING_ANIMATION-'].update_animation(bar_striped,time_between_frames=100)

def run_in_thread(filespath):
    if continue_animation:
        sg.popup_ok('Another process is running, wait for it to finish!',title="Attention!", keep_on_top=True)
        return
    thread = threading.Thread(target=run_processing, args=(filespath,event_filerecognaizng))
    thread.start()




def run_in_thread_plotting(folderpath,elementname):
    if continue_animation:
        sg.popup_ok('Another process is running, wait for it to finish!',title="Attention!", keep_on_top=True)
        return
    thread = threading.Thread(target=run_processing_plotting, args=(folderpath,elementname,event_filerecognaizng))
    thread.start()

def run_in_thread_prediction(folderpath,predictionnumber):
    if continue_animation:
        sg.popup_ok('Another process is running, wait for it to finish!',title="Attention!", keep_on_top=True)
        return
    thread = threading.Thread(target=run_processing_prediction, args=(folderpath,predictionnumber,event_filerecognaizng))
    thread.start()

def run_in_thread_procent_check(folderpath,procentnumber):
    if continue_animation:
        sg.popup_ok('Another process is running, wait for it to finish!',title="Attention!", keep_on_top=True)
        return
    thread = threading.Thread(target=run_processing_procent_check, args=(folderpath,procentnumber,event_filerecognaizng))
    thread.start()

processing_instance = Processing()

def show_info_box():
        info_text = (
            "Guide:\n"
            "\n"
            "1. Choose input folder with raw data and convert it into proper form by using button 'Execute processing' or select folder with already processed data and select checkbox ' data already prcessed '.\n"
            "\n"
            "Tip: All the converted data will be saved in input folder \n"
            "\n"
            "2. To confirm the conversion, click on the Execute Processing button."
            "\n"
            "\n"
            "You can plot the graphs by typing the name of the circuit element. The graph will be plotted based on the files you select PN list and plotted according to the data of the files."
            "\n"
            "\n"
            "Tip: The graph will be shown for the selected element and plotted with the measured data, both upper and lower limits and regression function aswell."
            "\n"
            "\n"
            "3. To predict the element with the risk of being out of the limits in a nearby future, click on the fill the number of prediction and Execute Prediction button."
            "\n"
            "\n"
            "Tip: The risky elements can be found only for prediction number between 100 and 10000. Each number is equal to single tested product."
            "\n"
            "\n"
            "Example:"
            "\n"
            "\n"
            "If you type 1000, the prediction will be done for the next 1000 electronic panels of the same, chosen PCBA PN."
            "\n"
            "\n"
            "You can also test how close the components are to the limits by entering the percentage of the limit in the corresponding field and using the 'Chcek value in range' button."
        )
        messagebox.showinfo("About the program:", info_text)

def run_processing_procent_check (folderpath,procentnumber, event_filerecognaizng):
    global continue_animation
    window['-LOADING_ANIMATION-'].update(visible=True)
    continue_animation = True
    animation_thread = threading.Thread(target=run_animation)
    animation_thread.start()
    window['-PROGRESS_TEXT-'].Update('Procent check for '+os.path.basename(folderpath) +' is loading',visible=True)
    processing_instance.check_values_within_range(folderpath,procentnumber)
    event_filerecognaizng.set()
    window['-PROGRESS_TEXT-'].Update(visible=False)
    continue_animation = False
    window['-LOADING_ANIMATION-'].update(visible=False)
    

def run_processing_prediction(folderpath,predictionnumber, event_filerecognaizng):
    global continue_animation, min_width, min_height, prediction_images, size_of_prediction_images, current_image
    size_of_prediction_images = 0
    prediction_images = []
    window['-LOADING_ANIMATION-'].update(visible=True)
    continue_animation = True
    animation_thread = threading.Thread(target=run_animation)
    animation_thread.start()
    window['-PROGRESS_TEXT-'].Update('Prediction for '+os.path.basename(folderpath) +' is loading',visible=True)
    prediction_images=processing_instance.prediction_look_ahead(folderpath,predictionnumber)
    #new_size=width,height
    #data_list_column.size=(width, height + 200)
    #window.size=(current_width+width,current_height+height)
    #return width,height
    event_filerecognaizng.set()
    # Adjust the data list column size to fit the new image
    # Adjust the main window size based on the new image size
    #current_window_width, current_window_height = window.size
    #additional_width = 700  # Additional space for other UI elements
    #additional_height = 10  # Additional space for other UI elements
    #min_width = max(current_window_width, width + additional_width)
    #min_height = max(current_window_height, height + additional_height)
    #window.size = (min_width, min_height)
    #window['-PLOT IMAGE-'].update(data=image_data, size=(width, height)
    size_of_prediction_images = int(len(prediction_images))
    if size_of_prediction_images != 0:
        current_image = 0
        window['-Previos-'].Update(visible=True)
        image_data, width, height = prediction_images[current_image]
        current_window_width, current_window_height = window.size
        additional_width = 800  # Additional space for other UI elements
        additional_height = 10  # Additional space for other UI elements
        min_width = max(current_window_width, width + additional_width)
        min_height = max(current_window_height, height + additional_height)
        window.size = (min_width, min_height)
        window['-PLOT IMAGE-'].update(data=image_data, size=(width, height),visible=True)
        window['-Quantity-'].Update(value="1/"+str(size_of_prediction_images),visible=True)
        window['-Next-'].Update(visible=True)
    window['-PROGRESS_TEXT-'].Update(visible=False)
    continue_animation = False
    window['-LOADING_ANIMATION-'].update(visible=False)
    

def run_processing_plotting(folderpath,elementname, event_filerecognaizng):
    global continue_animation, min_width, min_height
    window['-Next-'].Update(visible=False)
    window['-Previos-'].Update(visible=False)
    window['-Quantity-'].Update(visible=False)
    window['-LOADING_ANIMATION-'].update(visible=True)
    continue_animation = True
    animation_thread = threading.Thread(target=run_animation)
    animation_thread.start()
    window['-PROGRESS_TEXT-'].Update('Plot '+elementname +' is loading',visible=True)
    image_data, width, height=processing_instance.execute_plotting(folderpath,elementname)
    #new_size=width,height
    #data_list_column.size=(width, height + 200)
    #window.size=(current_width+width,current_height+height)
    #return width,height
    event_filerecognaizng.set()
    # Adjust the data list column size to fit the new image
    # Adjust the main window size based on the new image size
    current_window_width, current_window_height = window.size
    additional_width = 700  # Additional space for other UI elements
    additional_height = 10  # Additional space for other UI elements
    min_width = max(current_window_width, width + additional_width)
    min_height = max(current_window_height, height + additional_height)
    window.size = (min_width, min_height)
    window['-PLOT IMAGE-'].update(data=image_data, size=(width, height),visible=True)
    window['-PROGRESS_TEXT-'].Update(visible=False)
    continue_animation = False
    window['-LOADING_ANIMATION-'].update(visible=False)

def run_processing(filespath, event_filerecognaizng):
    global continue_animation
    window["-FILE LIST-"].Update(disabled=False)
    window['-LOADING_ANIMATION-'].update(visible=True)
    continue_animation = True
    animation_thread = threading.Thread(target=run_animation)
    animation_thread.start()
    window['-PROGRESS_TEXT-'].Update('Folder '+(os.path.basename(filespath)) +' is loading',visible=True)
    processing_instance.execute_processing(filespath)
    event_filerecognaizng.set()
    window['-PROGRESS_TEXT-'].Update(visible=False)
    continue_animation = False
    window['-LOADING_ANIMATION-'].update(visible=False)
    file_list = os.listdir(filespath)
    foldernamesnames = [
                f
                for f in file_list
                if not os.path.isfile(os.path.join(filespath, f))
            ]
    window["-FILE LIST-"].update(foldernamesnames)
    
def is_numeric(input_str):
    return input_str.isdigit() or (input_str.startswith('-') and input_str[1:].isdigit())

        
def MianLoop(window):
    while True:
        global min_width, min_height, current_image, size_of_prediction_images, prediction_images
        event, values = window.read(timeout=100)  # Check every 100ms
        if event == sg.WINDOW_CLOSED or event == "Exit":
            break
    
     # Check and enforce minimum size
        current_width, current_height = window.size
        if current_width < min_width or current_height < min_height:
            window.size = (max(min_width, current_width), max(min_height, current_height))
        
        if event == "-Execute_Procesing-":
            try:
               run_in_thread(os.path.join(values["-FOLDER-"]))
            except:
                pass
        if values["-FOLDER-"]:
           window["-Data_Prepared-"].Update(disabled=False)
        elif not values["-FOLDER-"]:
           window["-Data_Prepared-"].Update(disabled=True)
        if event == "-Data_Prepared-":
            if values["-Data_Prepared-"]:
                sg.popup_ok ('The data must have already been processed previously with “Execute Procesing”. If you are not sure if the data has been previously processed with “Execute Procesing” then please use Execute Procesing!',title="Attention!", keep_on_top=True)
                try:
                    window["-FILE LIST-"].Update(disabled=False)
                    file_list = os.listdir(os.path.join(values["-FOLDER-"]))
                    foldernamesnames = [
                        f
                        for f in file_list
                        if not os.path.isfile(os.path.join(os.path.join(values["-FOLDER-"]), f))]
                    window["-FILE LIST-"].update(foldernamesnames)
                except:
                    pass
            else:
                pass
        if event == "-Execute_Plotting-":
            if values["-FILE LIST-"] and values["-Element_Name-"]:
               try:
                   run_in_thread_plotting(os.path.join(values["-FOLDER-"], values["-FILE LIST-"][0]),values["-Element_Name-"].replace(" ", ""))
                   
               except:
                   pass
            else:
                sg.popup_ok('Select PN on the left! and provide element name',title="Attention!", keep_on_top=True)
        if event == "-Execute_Prediction-":
            if values["-FILE LIST-"] and values["-Prediction_Number-"]:
                input_value = values["-Prediction_Number-"]
                if is_numeric(input_value):
                    try:
                        run_in_thread_prediction(os.path.join(values["-FOLDER-"], values["-FILE LIST-"][0]),values["-Prediction_Number-"].replace(" ", ""))
                    except:
                        pass
                else:
                   sg.popup_ok('Procent value is not numeric',title="Attention!", keep_on_top=True) 
            else:
                sg.popup_ok('Select PN on the left! and provide prediction number',title="Attention!", keep_on_top=True)
                
        if event == "-Procent_value_range-":
            if values["-FILE LIST-"] and values["-Procent_Value-"]:
                input_value = values["-Procent_Value-"]
                if is_numeric(input_value):
                    try:
                        pass
                        run_in_thread_procent_check(os.path.join(values["-FOLDER-"], values["-FILE LIST-"][0]),values["-Procent_Value-"].replace(" ", ""))
                    except:
                        pass
                else:
                    sg.popup_ok('Procent value is not numeric',title="Attention!", keep_on_top=True)
            else:
                sg.popup_ok('Select PN on the left! and provide procent',title="Attention!", keep_on_top=True)
                
        if event == "-Previos-":
            if current_image-1 <= 0:
                current_image=size_of_prediction_images-1
                image_data, width, height = prediction_images[current_image]
                current_window_width, current_window_height = window.size
                additional_width = 800  # Additional space for other UI elements
                additional_height = 10  # Additional space for other UI elements
                min_width = max(current_window_width, width + additional_width)
                min_height = max(current_window_height, height + additional_height)
                window.size = (min_width, min_height)
                window['-PLOT IMAGE-'].update(data=image_data, size=(width, height))
                window['-Quantity-'].Update(value=str(current_image+1)+"/"+str(size_of_prediction_images))
            elif current_image-1 >= size_of_prediction_images:
                current_image=0
                image_data, width, height = prediction_images[current_image]
                current_window_width, current_window_height = window.size
                additional_width = 800  # Additional space for other UI elements
                additional_height = 10  # Additional space for other UI elements
                min_width = max(current_window_width, width + additional_width)
                min_height = max(current_window_height, height + additional_height)
                window.size = (min_width, min_height)
                window['-PLOT IMAGE-'].update(data=image_data, size=(width, height))
                window['-Quantity-'].Update(value=str(current_image+1)+"/"+str(size_of_prediction_images))
            else :
                current_image=current_image-1
                image_data, width, height = prediction_images[current_image]
                current_window_width, current_window_height = window.size
                additional_width = 800  # Additional space for other UI elements
                additional_height = 10  # Additional space for other UI elements
                min_width = max(current_window_width, width + additional_width)
                min_height = max(current_window_height, height + additional_height)
                window.size = (min_width, min_height)
                window['-PLOT IMAGE-'].update(data=image_data, size=(width, height))
                window['-Quantity-'].Update(value=str(current_image+1)+"/"+str(size_of_prediction_images))
        if event == "-Next-":
            if current_image+1 <= 0:
                current_image=size_of_prediction_images-1
                image_data, width, height = prediction_images[current_image]
                current_window_width, current_window_height = window.size
                additional_width = 800  # Additional space for other UI elements
                additional_height = 10  # Additional space for other UI elements
                min_width = max(current_window_width, width + additional_width)
                min_height = max(current_window_height, height + additional_height)
                window.size = (min_width, min_height)
                window['-PLOT IMAGE-'].update(data=image_data, size=(width, height))
                window['-Quantity-'].Update(value=str(current_image+1)+"/"+str(size_of_prediction_images))
            elif current_image+1 >= size_of_prediction_images:
                current_image=0
                image_data, width, height = prediction_images[current_image]
                current_window_width, current_window_height = window.size
                additional_width = 800  # Additional space for other UI elements
                additional_height = 10  # Additional space for other UI elements
                min_width = max(current_window_width, width + additional_width)
                min_height = max(current_window_height, height + additional_height)
                window.size = (min_width, min_height)
                window['-PLOT IMAGE-'].update(data=image_data, size=(width, height))
                window['-Quantity-'].Update(value=str(current_image+1)+"/"+str(size_of_prediction_images))
            else :
                current_image=current_image+1
                image_data, width, height = prediction_images[current_image]
                current_window_width, current_window_height = window.size
                additional_width = 800  # Additional space for other UI elements
                additional_height = 10  # Additional space for other UI elements
                min_width = max(current_window_width, width + additional_width)
                min_height = max(current_window_height, height + additional_height)
                window.size = (min_width, min_height)
                window['-PLOT IMAGE-'].update(data=image_data, size=(width, height))
                window['-Quantity-'].Update(value=str(current_image+1)+"/"+str(size_of_prediction_images))
                
        if event == '-Procent_Value-':
            input_value = values['-Procent_Value-']
            if not is_numeric(input_value):
                window['-Procent_Value-'].update(input_value[:-1])
            elif int(input_value)>=100:
                window['-Procent_Value-'].update(input_value[:-1])
            elif int(input_value)<=0:
                window['-Procent_Value-'].update(input_value[:-1])
        
        if event == '-Prediction_Number-':
            input_value = values['-Prediction_Number-']
            if not is_numeric(input_value):
                window['-Prediction_Number-'].update(input_value[:-1])
            elif int(input_value)>=100000:
                window['-Prediction_Number-'].update(input_value[:-1])
            elif int(input_value)<=0:
                window['-Prediction_Number-'].update(input_value[:-1])
                
        if event=='-Software_guide-':
            try:
                show_info_box()
            except:
                pass
                
                

 
        
#start the main window loop in new thread
event_loop_thread = threading.Thread(target=MianLoop, args=(window,))
event_loop_thread.start()