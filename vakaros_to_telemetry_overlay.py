import os
import csv
from datetime import datetime, timezone

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

VERSION = '1.0.4' 

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
    'cog': 'heading (deg)',
}

class GUI:
    def __init__(self):
        self.path = os.path
        #initialize window object
        self.window = tk.Tk()
        self.window.title("Vakaros To Telemetry Overlay")
        self.run_flag = tk.BooleanVar(value=False)

        menuBar = tk.Menu(self.window)
        self.window.config(menu=menuBar)
        menuBar.add_command(label='About', command=self.about)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.frame = tk.Frame(master=self.window, padx=5, pady=0)
        self.line_frame = tk.Label(master=self.frame,
                                   text='Vakaros ')
        self.btn_load_vakaros_csv = tk.Button(master=self.frame,
                                     text='Load Vakaros CSV file',
                                     command=self.run)

        self.line_frame = tk.Label(master=self.frame,
                                   text='___________________________________________________________')
        
        
        self.btn_load_vakaros_csv.pack()
        self.line_frame.pack()
        self.frame.pack()
        
        self.window.mainloop()
    
    def about(self):
        messagebox.showinfo(
            'About', 
            'Python application from Richard Didham to convert Vakaros export csv to'
            f'Telemetry Overlay import csv.\n Version: {VERSION}'
        )
            
    def run(self):
        title_str = 'Select Vakaros CSV File'
        file_types = (('csv files','.csv'),)
        vakaros_file_path = tk.filedialog.askopenfilename(title= title_str,
                                                            filetypes=file_types)
        output_path = run(vakaros_file_path)
        messagebox.showinfo(
            'Success', 
            f'csv file output to:\n {output_path}'
        )

def run(vakaros_file_path):
    header_dict, data = read_vakaros_csv(vakaros_file_path)
    map_telemetry_overlay_headers(header_dict)
    convert_timestamp(header_dict, data)
    output_directory, vakaros_file_name = get_output_directory(vakaros_file_path)
    output_file_name = write_converted_file(output_directory, vakaros_file_name, header_dict, data)
    return os.path.join(output_directory, output_file_name)

def read_vakaros_csv(vakaros_csv_path:str) -> tuple:
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
        #remove first line of csv file since it initially moves backward in time
        next(vakaros_csv_reader) 
        for row in vakaros_csv_reader:
            if len(row) == 0:
                continue
            data.append(row) 
            
        return (header_dict, data)

def map_telemetry_overlay_headers(header_dict:dict) -> None:
    '''
    associate telemety overlay headers with header_dict
    Args:
        header_dict: dictionary returned from _read_vakaros_csv
    '''
    for key, sub_dict in header_dict.items():
        if key in LABEL_MAP:
            telemetry_overlay_label = LABEL_MAP[key]
        else:
            telemetry_overlay_label = f"{key} (units)"
        sub_dict['telemetry_overlay_label'] = telemetry_overlay_label

def convert_timestamp(header_dict:dict, data:list) -> None:
    """Converts time column of data from local time to Zulu Time
    
    Args:
        header_dict: dictionary returned from _read_vakaros_csv
        data: rows of data returned from _read_vakaros_csv
    """
    timestamp_index = header_dict['timestamp']['column']
    for row in data:
        time = row[timestamp_index]
        datetime_obj = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%f")
        utc_datetime_obj = datetime_obj.astimezone(timezone.utc)
        row[timestamp_index] = utc_datetime_obj.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'

def get_output_directory(vakaros_file_path):
    head_tail = os.path.split(vakaros_file_path)
    return head_tail
        
def write_converted_file(
        output_directory:str, vakaros_file_name:str, header_dict:dict, data:list
    ) -> str:
    """Writes Converted data to new csv file.
    
    Args:
        output_directory: directory to write new file to
        vakaros_file_name: nave of the vakaros csv file that was loaded
        header_dict: dictionary returned from _read_vakaros_csv
        data: rows of data returned from _read_vakaros_csv
    """
    output_name = 'vk2to_' + vakaros_file_name
    output_path = os.path.join(output_directory, output_name)
    
    header = [item['telemetry_overlay_label'] for item in header_dict.values()]
        
    # writing to csv file 
    with open(output_path, 'w', newline='') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL) 
            
        # write header 
        csvwriter.writerow(header) 
            
        # writing the data rows 
        csvwriter.writerows(data) 

    return output_name 

def get_app_version():  
    with open('Changelog.md') as f:
        line = f.readline()
        number = line[10:]
    return number

if __name__ == '__main__':
    GUI()
     