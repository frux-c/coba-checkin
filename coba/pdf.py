from fpdf import FPDF
import time
import os
import pathlib
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shutil

FILE_PATH = pathlib.Path(__file__).parent.resolve()

class PDF(FPDF):
    def __init__(self,start=None,end=None):
        super().__init__()
        self.WIDTH = 210
        self.HEIGHT = 297
        self.TITLE = "Weekly CoBA-Checkin Report"
        today = time.strftime("%d/%m/%Y")
        self.date_range_start = today if start is None else start
        self.date_range_end = today if end is None else end
        
    def header(self):
        # Custom logo and positioning
        self.image(os.path.join(FILE_PATH,
            'static','assets','utep_logo.png'), 5, 0, 25)
        self.set_font('Helvetica', 'B', 15)
        self.cell(self.WIDTH - 80)
        self.cell(60, 1, self.TITLE, 0, 0, 'R')
        self.ln(5)
        # Add date of report
        self.set_font('Helvetica', '', 10)
        self.cell(self.WIDTH - 80)
        self.set_text_color(r=128,g=128,b=128)
        # today = time.strftime("%d/%m/%Y")
        self.cell(60, 1,  f'From : {self.date_range_start} To : {self.date_range_end}', 0 , 0, 'R')
        self.ln(20)
            
    def footer(self):
        # Page numbers in the footer
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def page_body(self, images):
        # Determine how many plots there are per page and set positions
        # and margins accordingly
        if len(images) == 3:
            self.ln(10)
            self.image(images[0], 15, 25, self.WIDTH - 30)
            self.image(images[1], 15, self.WIDTH / 2 + 5, self.WIDTH - 30)
            self.image(images[2], 15, self.WIDTH / 2 + 90, self.WIDTH - 30)
        elif len(images) == 2:
            self.image(images[0], 15, 40, self.WIDTH - 30)
            self.image(images[1], 15, self.WIDTH / 2 + 60, self.WIDTH - 30)
        else:
            self.image(images[0], 15, 25, self.WIDTH - 30)
            
    def print_page(self, images):
        # Generates the report
        self.add_page()
        self.page_body(images)

def generate_table(data,filename:str):
    # print(list(data.keys()))
    fig,ax = plt.subplots()
    fig.patch.set_visible(False)
    ax.set_axis_off()
    plt.box(on=None)
    # fig.subplot_adjust(left=0.2,bottom=0.2)
    day_of_week = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
    today = datetime.now()
    count = 0
    day_count = 0
    while count < len(day_of_week):
        current = today - timedelta(days=day_count)
        try:
            day_of_week[current.weekday()] += f" ({current.date().month}/{current.date().day})"
            count += 1
            day_count += 1
        except IndexError as e:
            day_count += 1
    student_names = list(data.keys())
    plot_data = [["No Hours" for _ in day_of_week] for __ in student_names]
    for row,name in enumerate(student_names):
        for day,hours in data[name]:
            try:
                day_num = datetime.strptime(day,'%Y-%m-%d')
                plot_data[row][day_num.weekday()] = f"{hours} hr(s)"
            except:
                print(day,day_num)
                continue
    plt.subplots_adjust(left=0.2,bottom=0.2)
    plt.suptitle("Student Hours per Day")
    table = ax.table(
        cellText = plot_data,
        # cellText = [[data[student][date] for date in data[student]] for student in data],
        rowLabels = student_names,#list(data.values()),
        colLabels = day_of_week,
        loc='center'
        )
    table.scale(1,1.5)
    plt.savefig(filename, dpi=300, bbox_inches='tight', pad_inches=0)

def plot_data_horizontal(names, hours, filename) -> None:
    fig,ax = plt.subplots(figsize=(16,9))
    ax.barh(names,hours)
    # Remove x, y Ticks
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')
     
    # Add padding between axes and labels
    ax.xaxis.set_tick_params(pad = 5)
    ax.yaxis.set_tick_params(pad = 10)

    # Add x, y gridlines
    ax.grid(visible=True, color ='grey',
        linestyle ='-.', linewidth = 0.5,
        alpha = 0.2)
    # Show top values
    ax.invert_yaxis()

    # Add annotation to bars
    for i in ax.patches:
        plt.text(i.get_width()+0.2, i.get_y()+0.5,
                 str(round((i.get_width()), 2)),
                 fontsize = 10, fontweight ='bold',
                 color ='grey')

    # Add Plot Title
    # ax.set_title('hr',loc ='left')
    plt.title("Student Hours per Week\n\n",fontsize=28,ha='center')
    plt.savefig(filename, dpi=300, bbox_inches='tight', pad_inches=0)

def construct(students : list):
    FOLDER_DIR = os.path.join(FILE_PATH,'plots')
    # Delete folder if exists and create it again
    try:
        shutil.rmtree(FOLDER_DIR)
        os.mkdir(FOLDER_DIR)
    except FileNotFoundError:
        os.mkdir(FOLDER_DIR)
        
    # generate total hour for week per student
    name_and_hour = dict()
    name_and_day = dict()
    for student in students:
        t_in = student.get("Real Time In")
        t_out = student.get("Real Time Out")
        total_hr = 0 if '-' in (t_in+t_out) else (datetime.strptime(t_out.split('.')[0],"%H:%M:%S") - datetime.strptime(t_in.split('.')[0],"%H:%M:%S")).seconds/3600
        # generate total hour for week per student
        if name_and_hour.get(student.get('Name')) is None:
            name_and_hour[student.get('Name')] = total_hr
        else:
            name_and_hour[student.get('Name')] += total_hr
        #generate total hour for each day per student   
        if name_and_day.get(student.get('Name')) is None:
            name_and_day[student.get('Name')] = [(str(student.get("Date Created")),total_hr)]
        else:
            name_and_day[student.get('Name')].append((str(student.get("Date Created")),total_hr))
    for name in name_and_hour:
        name_and_hour[name] = round(name_and_hour[name],2)
    for name in name_and_day:
        name_and_day[name] = [(date,round(hours,2)) for date,hours in name_and_day[name]]

    names = list(name_and_hour.keys())
    hours = list(name_and_hour.values())
    plot_data_horizontal(names,hours,f'{FOLDER_DIR}/total_hours.png')

    #generate total hour for each day per student
    generate_table(name_and_day,f'{FOLDER_DIR}/student_table.png')
        
    # Construct data shown in document
    counter = 0
    pages_data = []
    temp = []
    # Get all plots
    files = os.listdir(FOLDER_DIR)

    # Iterate over all created visualization
    for fname in files:
        # We want 3 per page
        if counter == 3:
            pages_data.append(temp)
            temp = []
            counter = 0

        temp.append(f'{FOLDER_DIR}/{fname}')
        counter += 1

    return [*pages_data, temp]