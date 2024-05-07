from tkinter import filedialog, messagebox
from datetime import datetime
import os
import re
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
from sklearn.linear_model import LinearRegression
import tkinter as tk
import threading
import io
import base64
from PIL import Image

class Processing:
    
    def __init__(self):
        pass

    def prediction_look_ahead(self, folderpath,predictionnumber):
        output_folder_path = folderpath
        if not output_folder_path:
            messagebox.showwarning("Warning", "Please select an output folder.")
            return

        try:
            prediction_vector = int(predictionnumber)
            if not (100 <= prediction_vector <= 10000):
                messagebox.showwarning("Warning", "Please choose a value between 100 and 10000 samples.")
                return
        except ValueError:
            messagebox.showwarning("Warning", "Please enter a valid number for prediction.")
            return

        #user_response = messagebox.askquestion("Approve procedure", "Do you want to perform the prediction?")
        #if user_response == 'no':
            #return

        # Rest of the code for prediction goes here
        element_data = self.load_data_from_output_folder(output_folder_path)
        elements_crossing_limits = []
        prediction_images = []
        quantity_of_pictures=0

        for element_name, data in element_data.items():
            measured_values = np.array(data['measured_values'])
            lower_limits = np.array(data['lower_limits'])
            upper_limits = np.array(data['upper_limits'])
           

            if any(np.isnan(measured_values)):
                messagebox.showwarning("Warning",
                                       f"No measured values found for element '{element_name}'. Skipping prediction.")
                continue

            x_values = np.arange(len(measured_values))
            model = LinearRegression().fit(x_values.reshape(-1, 1), measured_values)

            prediction_range = np.arange(0, prediction_vector)
            predicted_values = model.predict(prediction_range.reshape(-1, 1))

            lower_limit_crossed = any(predicted_values < data['lower_limits'][0])
            upper_limit_crossed = any(predicted_values > data['upper_limits'][0])

            if lower_limit_crossed or upper_limit_crossed:
                elements_crossing_limits.append(element_name)

                plt.figure()

                plt.plot(prediction_range, predicted_values, linestyle='--', label='Prediction')

                x_extended = np.arange(len(x_values), len(x_values) + prediction_vector)

                limit_range = np.arange(0, prediction_vector)

                lower_limits_extended = np.full(len(limit_range), data['lower_limits'][0])
                upper_limits_extended = np.full(len(limit_range), data['upper_limits'][0])

                plt.plot(limit_range, lower_limits_extended, linestyle='--', label='Lower Limit')
                plt.plot(limit_range, upper_limits_extended, linestyle='--', label='Upper Limit')

                plt.xlabel("Sample number", fontsize="10",fontfamily="Arial")
                plt.ylabel(self.get_y_axis_label(element_name),fontsize="7",fontfamily="Arial")
                plt.title(f'Prediction for {element_name}',fontsize="10")
                plt.subplots_adjust(left=0.15)
                plt.legend(bbox_to_anchor=(1.30, 0.9), loc='center right', fontsize="7")
                plt.subplots_adjust(right=0.8)


                #prediction_plots_folder = os.path.join(output_folder_path, f"prediction_plots_{prediction_vector}")
                #if not os.path.exists(prediction_plots_folder):
                    #os.makedirs(prediction_plots_folder)
                #plt.savefig(os.path.join(prediction_plots_folder, f"{element_name}_prediction.png"))
                
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                plt.close()
                buffer.seek(0)

                # Return base64-encoded data for PySimpleGUI
                encoded_image = base64.b64encode(buffer.getvalue())
                image = Image.open(buffer)
                width, height = image.size
                
                quantity_of_pictures = quantity_of_pictures+1
                prediction_images.append((encoded_image, width, height))
                
            if quantity_of_pictures >= 100:
                break
             
        return prediction_images

        #messagebox.showinfo("Plotting data","Data was saved to the files")

        if not elements_crossing_limits:
            messagebox.showinfo("Info","No limits crossed for the elements during the prediction.")

        #self.master.after(0, self.save_prediction_plots, output_folder_path, elements_crossing_limits,
                          #prediction_vector)


    def load_data_from_output_folder(self, output_folder_path):
        element_data = defaultdict(lambda: {'names': [], 'measured_values': [], 'lower_limits': [], 'upper_limits': []})

        for filename in os.listdir(output_folder_path):
            if filename.endswith(".txt"):
                file_path = os.path.join(output_folder_path, filename)
                with open(file_path, 'r') as file:
                    for line in file:
                        parts = line.split()
                        if len(parts) >= 5 and all(
                                part.replace('.', '').replace('-', '').isdigit() or part == 'None' for part in
                                parts[2:]):
                            element_name = parts[1]
                            element_data[element_name]['names'].append(filename)
                            element_data[element_name]['measured_values'].append(float(parts[2]))
                            element_data[element_name]['lower_limits'].append(float(parts[3]) if parts[3] != 'None' else None)
                            element_data[element_name]['upper_limits'].append(float(parts[4]) if parts[4] != 'None' else None)

        return element_data


    def execute_processing(self, filespath):
 
        input_folder_path = filespath
        output_folder_path = filespath

        if not input_folder_path or not output_folder_path:
            messagebox.showwarning("Warning", "Please select input and output folders.")
            return

        for filename in os.listdir(input_folder_path):
            if filename.endswith(".log"):
                input_file_path = os.path.join(input_folder_path, filename)

                current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file_name = f"{current_datetime}.txt"
                output_file_path = os.path.join(output_folder_path, output_file_name)

                with open(input_file_path, 'r') as f:
                    prefixes = ("R", "C", "L", "Q", "P", "I", "V","B")
                    counter = 0

                    with open(output_file_path, 'w') as output_file:
                        for eachLine in f.readlines():
                            if "=" in eachLine:
                                if eachLine.startswith(prefixes):
                                    updated_line = re.sub(r'(\d*\.\d+|\d+)([UPK]|MEG|N|M)', self.replace_prefix,
                                                          eachLine.strip())
                                    var = re.split(r"[=(,)]", updated_line)
                                    var = ' '.join(var).split()
                                    var.pop()
                                    length = len(var)
                                    if length >= 3:
                                        counter += 1
                                        var.insert(0, counter)
                                        converted_line = self.convert_list_to_string(var)
                                        print(converted_line)
                                        output_file.write(converted_line + '\n')


                pn_match = re.search(r'[A-Z0-9]{8}', filename)
                if pn_match:
                    pn_folder_name = pn_match.group()
                    pn_folder_path = os.path.join(output_folder_path, pn_folder_name)
                    if not os.path.exists(pn_folder_path):
                        os.makedirs(pn_folder_path)
                  
                    files_in_pn_folder = len(os.listdir(pn_folder_path))
                    new_output_file_name = f"{files_in_pn_folder}_{current_datetime}.txt"
                    new_output_file_path = os.path.join(pn_folder_path, new_output_file_name)
                    os.rename(output_file_path, new_output_file_path)

        messagebox.showinfo("Procedure","The conversion is done")
        
    def execute_plotting(self, folderpath,elementname):

        output_folder_path = folderpath
        element_name = elementname

        if not output_folder_path or not element_name:
            messagebox.showwarning("Warning", "Please select output folder and enter element name.")
            return

        element_data = defaultdict(lambda: {'names': [], 'measured_values': [], 'lower_limits': [], 'upper_limits': []})

        file_list = os.listdir(output_folder_path)
        file_list.sort(key=lambda x: self.extract_file_info(x))

        for filename in file_list:
            if filename.endswith(".txt"):
                file_path = os.path.join(output_folder_path, filename)

                with open(file_path, 'r') as file:
                    element_found = False
                    for line in file:
                        parts = line.split()
                        if len(parts) >= 4 and all(part.replace('.', '').replace('-', '').isdigit() or part == 'None' for part in parts[2:]):
                            current_element_name = parts[1]
                            if current_element_name == element_name:
                                element_found = True
                                element_data[current_element_name]['names'].append(filename)
                                element_data[current_element_name]['measured_values'].append(float(parts[2]))
                                if len(parts) == 5:  # Jeśli są 5 części, to oznacza, że mamy oba limity
                                    element_data[current_element_name]['lower_limits'].append(float(parts[3]) if parts[3] != 'None' else None)
                                    element_data[current_element_name]['upper_limits'].append(float(parts[4]) if parts[4] != 'None' else None)
                                elif len(parts) == 4:  # Jeśli są 4 części, to oznacza, że mamy tylko jeden limit
                                    element_data[current_element_name]['lower_limits'].append(float(parts[3]) if parts[3] != 'None' else None)
                                    element_data[current_element_name]['upper_limits'].append(None)  # Dodajemy None dla brakującego górnego limitu

                    if not element_found:
                        element_data[element_name]['names'].append(filename)
                        element_data[element_name]['measured_values'].append(None)
                        element_data[element_name]['lower_limits'].append(None)
                        element_data[element_name]['upper_limits'].append(None)

        data = element_data.get(element_name)
        if data:
            plt.figure()

            plt.plot(data['names'], data['measured_values'], marker='o', markersize="1", linewidth="2", linestyle='-',
                     label='Measured Value')

            if any(limit is not None for limit in data['lower_limits']):
                plt.plot(data['names'], data['lower_limits'], marker='o', markersize="1", linewidth="2", linestyle='--',
                         label='Lower Limit')

            if any(limit is not None for limit in data['upper_limits']):
                plt.plot(data['names'], data['upper_limits'], marker='o', markersize="1", linewidth="2", linestyle='--',
                         label='Upper Limit')

            measured_values = np.array([float(value) if value is not None else np.nan for value in data['measured_values']])
            non_nan_indices = ~np.isnan(measured_values)
            if any(non_nan_indices):
                x_values = np.arange(len(measured_values))
                trend_line_coefficients = np.polyfit(x_values[non_nan_indices], measured_values[non_nan_indices], 1)
                trend_line = np.poly1d(trend_line_coefficients)
                plt.plot(data['names'], trend_line(x_values), linestyle='-', label='Trend Line', color='red')

            plt.xlabel("Sample number", fontsize="10",fontfamily="Arial")
            plt.ylabel(self.get_y_axis_label(element_name), fontsize="7",fontfamily="Arial")
            plt.title(f'Measured Value and Limits for {element_name}', fontsize="10")
            plt.legend(bbox_to_anchor = (1.30, 0.9), loc='center right', fontsize="7")
            plt.subplots_adjust(left=0.15)
            plt.subplots_adjust(right=0.8)
            plt.xticks([])
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)  # Reset buffer to start
            # Return base64-encoded data for PySimpleGUI
            image = Image.open(buffer)
            width, height = image.size
            
            return base64.b64encode(buffer.getvalue()), width, height

            if any(non_nan_indices):
                exceed_lower_limit = any(measured_values[non_nan_indices] < trend_line(x_values)[non_nan_indices])
                exceed_upper_limit = any(measured_values[non_nan_indices] > trend_line(x_values)[non_nan_indices])
        else:
            print(f"No data found for element '{element_name}' in the specified directory.")

    def check_values_within_range(self, folderpath,procentnumber):
        output_folder_path = folderpath
        procentnumber=int(procentnumber)
        if not output_folder_path:
            messagebox.showwarning("Warning", "Please select an output folder.")
            return

        results = []

        element_data = self.load_data_from_output_folder(output_folder_path)

        for element_name, data in element_data.items():
            measured_values = np.array(data['measured_values'])
            lower_limits = np.array(data['lower_limits'])
            upper_limits = np.array(data['upper_limits'])

            if any(np.isnan(measured_values)):
                messagebox.showwarning("Warning",f"No measured values found for element '{element_name}'. Skipping checking.")
                continue

            percent_change = procentnumber / 100
            lower_limit_range_1 = percent_change * (upper_limits - lower_limits)
            range_1_indices = \
                np.where((measured_values >= lower_limits) & (measured_values <= lower_limits + lower_limit_range_1))[0]

            upper_limit_range_2 = percent_change * (upper_limits - lower_limits)
            range_2_indices = \
                np.where((measured_values >= upper_limits - upper_limit_range_2) & (measured_values <= upper_limits))[0]

            if range_1_indices.size > 0 or range_2_indices.size > 0:
                results.append(element_name)
            if int(len(results))>=10:
                results.append('+ others')
                break
        if results:
            self.display_results_message(results,procentnumber)
        else:
            messagebox.showinfo("Results", "No elements found within the specified range.")

    def display_results_message(self, results, procentnumber):
        percent_change = procentnumber
        result_message = f"Elements with values within {percent_change}% of the limits:\n\n" + "\n".join(results)
        messagebox.showinfo("Results", result_message)

    @staticmethod
    def replace_prefix(match):
        prefix_mapping = {
            "U": 1e-6,
            "K": 1e3,
            "P": 1e-12,
            "MEG": 1e6,
            "N": 1e-9,
            "M": 1e-3,



        }
        value, prefix = match.group(1), match.group(2)
        if prefix in prefix_mapping:
            return '{:.15f}'.format(float(value) * prefix_mapping[prefix])
        return match.group(0)

    @staticmethod
    def convert_list_to_string(lst):
        return ' '.join(map(str, lst))

    @staticmethod
    def extract_file_info(filename):
        parts = filename.split('_')
        if len(parts) == 3:
            return int(parts[0]), int(parts[1])
        return float('inf'), None

    @staticmethod
    def get_y_axis_label(element_name):
        if element_name.startswith('R'):
            return 'Resistance (\u03A9)'
        elif element_name.startswith('C'):
            return 'Capacity (F)'
        elif element_name.startswith('L'):
            return 'Inductance (H)'
        elif element_name.startswith('Q'):
            return 'Voltage (V)'
        else:
            return 'Value'