import sys, os
import csv
from datetime import datetime, timezone

import tkinter as tk
from tkinter import filedialog


class GUI:
    def __init__(self):
        self.path = os.path
        #initialize window object
        self.window = tk.Tk()
        self.window.title("Vakaros To Telemetry Overlay")
        self.run_flag = tk.BooleanVar(value=False)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.frame = tk.Frame(master=self.window, padx=5, pady=0)
        self.btn_load_vakaros_csv = tk.Button(master=self.frame,
                                     text='Load Vakaros CSV file',
                                     command=self.run)

        self.line_frame = tk.Label(master=self.frame,
                                   text='___________________________________________________________')
        
        
        self.btn_load_vakaros_csv.pack()
        self.line_frame.pack()
        self.frame.pack()
        
        self.window.mainloop()
            
    def run(self):
        title_str = 'Select Vakaros CSV File'
        file_types = (('csv files','.csv'),)
        vakaros_file_path = tk.filedialog.askopenfilename(title= title_str,
                                                            filetypes=file_types)
        run(vakaros_file_path)

LABEL_MAP = {
    'timestamp': 'date',
    'latitude': 'lat (deg)',
    'longitude': 'lon (deg)',
    'sog_kts': 'speed (kn)',
    'sog_mps': 'speed (m/s)', # idk why you'd use something other than kts but writing out label maps anyway
    'sog_mph': 'speed (m/h)',
    'sog_kph': 'speed (k/h)',
    'roll': 'bank (deg)',
    'pitch': 'pitch angle (deg)',
    'cog': 'heading (deg)'
}

def run(vakaros_file_path):
    header_dict, data = _read_vakaros_csv(vakaros_file_path)
    _map_telemetry_overlay_headers(header_dict)
    _convert_timestamp(header_dict, data)

def _read_vakaros_csv(vakaros_csv_path:str) -> tuple:
    '''
    Reads the csv file which is output from vakaros and stores data
    
    Args:
    vakaros_csv_path: path to file to upload

    Returns:
    dictionary representation of vakaros csv with two key value pairs
    'header_dict' key for a dict of csv headers
    'data' key for a list of lists of all the rows in the csv file below the header
    
    '''
    with open(vakaros_csv_path) as vakaros_csv_file:
        vakaros_csv_reader = csv.reader(vakaros_csv_file, delimiter=',')
        header = next(vakaros_csv_reader)
        header_dict = {label: {'column': column} for column, label in enumerate(header)}
        data = []
        for row in vakaros_csv_reader:
            data.append(row) 
            
        return (header_dict, data)

def _map_telemetry_overlay_headers(header_dict:dict) -> None:
    '''
    associate telemety overlay headers with header_dict
    Args:
    header_dict: dictionary returned from _read_vakaros_csv
    '''
    for key, sub_dict in header_dict.items():
        if key in LABEL_MAP:
            telemetry_overlay_label = LABEL_MAP[key]
        else:
            telemetry_overlay_label = key
        sub_dict['telemetry_overlay_label'] = telemetry_overlay_label

def _convert_timestamp(header_dict:dict, data:list) -> None:
    timestamp_index = header_dict['timestamp']['column']
    for row in data:
        time = row[timestamp_index]
        datetime_obj = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%f")
        utc_datetime_obj = datetime_obj.astimezone(timezone.utc)
        time = utc_datetime_obj.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'
        

if __name__ == '__main__':
    GUI()
    # arguments = sys.argv
    # print(arguments)
    # if len(arguments) != 2:
    #     print("Error, zero or multiple input arguments given")
    #     sys.exit()
    
    # header_dict, data = _read_vakaros_csv(arguments[1])
    # _map_telemetry_overlay_headers(header_dict)
    
    
    