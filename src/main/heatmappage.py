from tkinter.ttk import Style
from create_image_label import DrawLabelImage

import matplotlib
import pandas as pd
import numpy as np
import scipy.spatial as ss
from PIL import ImageTk
import math

from errors import *
import time

import matplotlib.cm as cm
import matplotlib.image as mpimg

import time

matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.axes
import PIL.ImageTk
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

import os
import json
import re
import shlex

from tksheet import Sheet
import csv
import os
import win32api

LARGE_FONT = ("Bell Gothic Std Black", 40, 'bold')
MEDIUM_FONT = ("Bell Gothic Std Black", 25, 'bold')
BUTTON_FONT = ('Calibiri', 14, 'bold')
BACKGROUND_COLOR = '#407297'
LIGHT_BLUE = '#d4e1fa'
LIGHT_BLUE1 = '#407297'

class HeatMapPage(tk.Frame):
    """
    Class that creates the frame for the graph and handles real time point clicking and distance calculations
    """

    def __init__(self, parent, controller, data_frame=None, options=None):
        self.old_point, self.last_point = [-1, -1, -2], [-1, -1, -1]
        self.lastUpdate = 0
        self.image_name = ''
        self.pa_dict = {}
        
        if options is not None:
            self.unit_string = options['unit_type']
            if options['habitat_image'] != '':
                self.image_name = options['habitat_image']
                self.img = mpimg.imread(self.image_name)

        if (data_frame is not None) and (options is not None):
            tk.Frame.__init__(self, parent)

            # df[end] - df[begin]/(end-begin)
            self.label_var = tk.StringVar()
            if options['z_column'] != '':
                self.label_var.set("3d Graph Page")
            else:
                self.label_var.set("Click points to calculate distance")

            self.label = tk.Label(self, textvariable=self.label_var, font=MEDIUM_FONT, bg=LIGHT_BLUE)

            def resizeLabel(event):
                pageWidth = event.width
                try:
                    self.label.config(wraplength=math.floor(pageWidth / 2))
                except Exception:
                    pass

            parent.bind('<Configure>', resizeLabel)

            self.label.pack(pady=10, padx=10)

            button1 = ttk.Button(self, text="Back to Home",
                                 command=lambda: self.handle_back_to_home(controller))
            button1.pack()

            self.fig = Figure()
            self.fig.patch.set_facecolor(LIGHT_BLUE)

            self.canvas = FigureCanvasTkAgg(self.fig, self)
            # canvas.create_image(20, 20, anchor=NW, image=options['habitat_image'])
            self.canvas.draw()

            cal_ratio = self.get_calibration_ratio(data_frame, options)
            if (options['x_ratio'] != '' and options['y_ratio'] != ''):
                self.x_ratio = float(options['x_ratio'])
                self.y_ratio = float(options['y_ratio'])
            else:
                self.x_ratio = cal_ratio
                self.y_ratio = cal_ratio

            # filtering the data frame into the row range specified in options
            if options['begin_index'] != '' and options['end_index'] != '':
                data_frame = data_frame.iloc[int(options['begin_index']):int(options['end_index'])]

            # loop through column filters and filter data frame
            for k, v in options['filters'].items():
                allowed_vals = HeatMapPage.process_string_input(v)
                if data_frame[k].dtypes == 'object':
                    data_frame = data_frame.loc[
                        (data_frame[k].astype(str).apply(HeatMapPage.standardize_string, 1).isin(allowed_vals))]
                else:
                    data_frame = data_frame.loc[(data_frame[k].isin(allowed_vals))]

            self.x_col, self.y_col, self.z_col = self.get_columns_from_options(options)
            # print(data_frame[self.x_col])
            """
            x_low = data_frame[self.x_col].quantile(0.01)
            x_hi = data_frame[self.x_col].quantile(0.99)

            data_frame = data_frame[(data_frame[self.x_col] < x_hi) &
                                    (data_frame[self.x_col] > x_low)]
            """
            # now we filter out null values for .x/self.y/self.z columns
            if self.z_col != '':
                data_frame = data_frame.loc[(pd.notnull(data_frame[self.x_col])) &
                                            (pd.notnull(data_frame[self.y_col])) &
                                            (pd.notnull(data_frame[self.z_col]))]
            else:
                data_frame = data_frame.loc[(pd.notnull(data_frame[self.x_col])) &
                                            (pd.notnull(data_frame[self.y_col]))]

            button2 = ttk.Button(self, text="Open Spreadsheet",
                                 command=lambda: self.show_spreadsheet(controller, data_frame, options))
            button2.pack()

            # Adds a button for launching Calculation Output Overlay
            button3 = ttk.Button(self, text="Calculate Name Distances",
                                 command=lambda: controller.calc_name_distance(controller, self.data_frame,
                                                                               self.options, cal_ratio))
            button3.pack()

            '''
            add new button
            '''
            new_add_frame = tk.Frame(self)
            new_add_frame.pack()
            button4 = ttk.Button(new_add_frame, text="Add Image",
                                 command=lambda: self.add_image_label())
            button4.pack(side='left')
            self.delete_point_button = ttk.Button(new_add_frame, text="Start Delete Points",
                                                  command=lambda: self.delete_point_bind_button())
            self.delete_point_button.pack(side='right')
            self.delete_point_flag = False
            
            self.options, self.cal_ratio, self.data_frame = options, cal_ratio, data_frame

            self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
            self.toolbar = ZooMapperToolbar(self.canvas, self)
            self.toolbar.update()
            self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            self.z_col_ratio = 1
            if self.z_col != "":
                self.z_col_ratio = self.z_col_adjust()

            self.createPlot()

            def highlightRow(event=None):
                """
                Highlights row in spreasheet according to point that was clicked.
                Only gets highlighted if a sheet is already open.
                """
                if hasattr(controller, "sheet") and self.z_col == "":

                    xarr = data_frame[self.x_col].values
                    yarr = data_frame[self.y_col].values
                    selectedIndex = 0
                    while xarr[selectedIndex] * self.x_ratio != self.last_point[0] or yarr[
                        selectedIndex] * self.y_ratio != self.last_point[1]:
                        selectedIndex += 1

                    controller.sheet.sheet.select_row(selectedIndex, redraw=True)
                    controller.sheet.sheet.see(row=selectedIndex, keep_xscroll=True)

                    # print(self.x_col, self.y_col)
                    # controller.sheet.sheet.select_row(self.selectedIndex, redraw = True)
                    # controller.sheet.sheet.see(row = self.selectedIndex, keep_xscroll = True)

            self.numOnpick3Calls = 0

            self.overlapping_points = []
            self.fig.canvas.mpl_connect('pick_event', self.delete_point_clickevent)
            

            if self.z_col == "":
                self.fig.canvas.mpl_connect('button_press_event', self.clickevent)
                self.fig.canvas.mpl_connect('button_press_event', highlightRow)

        else:
            tk.Frame.__init__(self, parent)
            button1 = ttk.Button(self, text="Back to Home",
                                 command=lambda: controller.show_frame(StartPage))
            button1.pack()

    def handle_back_to_home(self, controller):
        """
        Returns to start page and closes and spreadsheet and calculations windows if open
        """
        if hasattr(controller, "sheet"):
            controller.sheet.close(controller)
        if hasattr(controller, "name_window"):
            controller.name_window.return_cancel()
        controller.show_frame(StartPage)

    def show_spreadsheet(self, controller, data_frame, options):
        """
        Open new spreadsheet if not already open
        """
        if hasattr(controller, "sheet"):
            controller.sheet.deiconify()
        else:
            controller.show_sheet(data_frame, options)

    def z_col_adjust(self):
        """
        Adjusts z column depending on the name of the column
        For example, depth is a negative z so if values are not negative, then make them negative
        """
        z_data = self.data_frame[self.z_col]
        contains_negative_val = (z_data < 0).values.any()

        if "depth" in self.z_col.lower() and not contains_negative_val:
            ratio = -1
        elif "height" in self.z_col.lower() and contains_negative_val:
            ratio = -1
        else:
            ratio = 1

        return ratio

    '''
    Add image label related code
    '''

    def add_card(self, con, x=100, y=100, width=200, height=200, fg='black', bg='white'):
        pa = DrawLabelImage(self, width=width, height=height)
        pa.place(x=x, y=y, width=width, height=height)
        pa.update()
        pa.create_label_image(con)

    def add_image_label(self):
        """
        Opens file selection window to choose an image. Add to the Frame
        """

        imagename = tk.filedialog.askopenfilename(initialdir="",
                                                  title="Select a File",
                                                  filetypes=(("Image files",
                                                              "*.png*"),
                                                             ("Image files",
                                                              "*.jpg"),
                                                             ("Image files",
                                                              "*.jpeg"),
                                                             ("all files",
                                                              "*.*")))
        if imagename:
            self.add_card(imagename)

    '''
    Delete Point Related Code
    '''

    def delete_point_bind_button(self):
        if self.delete_point_flag:
            self.delete_point_button['text'] = 'Start Delete Points'
            self.delete_point_flag = False
        else:
            self.delete_point_button['text'] = 'Stop Delete Points'
            self.delete_point_flag = True

    def delete_point_clickevent(self, event):
        # print(event)
        # print(event.ind)
        if self.delete_point_flag:
            if self.z_col != '':
                self.points.delpoint([event.ind[0]], z='1')
            else:
                self.points.delpoint([event.ind[0]])
            self.createPlot()
            
    def clickevent(self, event):
        """
        Handles clicking on graph and finding closest point to highlight
        """
        if event.button == 3:
            if hasattr(self, "defaultDims"):
                self.ax.set_xlim(self.defaultDims[0][0], self.defaultDims[0][1])
                self.ax.set_ylim(self.defaultDims[1][0], self.defaultDims[1][1])
                self.createPlot()
        if event.button == 1:
            try:
                self.find_closest_point(event)
            except TypeError:
                # clicked outside of plot
                pass

    def find_closest_point(self, event):
        """
        Finds closest point to click location and highlights the point
        """
        click_coords = self.get_click_data(event)
        if self.z_col == '':
            point_coords = self.get_data_point(self.ax.collections, click_coords[0], click_coords[1])
        else:
            point_coords = self.get_data_point(self.ax.collections, click_coords[0], click_coords[1], click_coords[2])
        distance = self.calculate_distance(point_coords)
        if self.old_point != [-1, -1, -2]:
            self.display_distance(event, distance)

        self.highlight_point()
        # self.canvas.draw()
        self.createPlot()
        # app.update_graph()

    def highlight_point(self):
        """
        Recolors most recently clicked points. The most recent point is black and the previous is grey
        """
        colors = cm.rainbow(np.linspace(0, 1, len(self.points)))
        for i in range(len(self.points)):
            color = colors[i]
            color_points = self.points[i].getcolors()
            for color_ind in range(len(color_points)):
                if type(color_points[color_ind]) != np.ndarray:
                    self.points[i].modcolor(color_ind, color)
            x_vals = self.points[i].getx()
            y_vals = self.points[i].gety()
            if self.old_point[0] in x_vals and self.old_point[1] in y_vals:
                for j in range(len(x_vals)):
                    if [x_vals[j], y_vals[j]] == self.old_point:
                        self.points[i].modcolor(j, "#808080")
            if self.last_point[0] in x_vals and self.last_point[1] in y_vals:
                for j in range(len(x_vals)):
                    if [x_vals[j], y_vals[j]] == self.last_point:
                        self.points[i].modcolor(j, "black")

    def get_click_data(self, event):
        """
        Gets the x and y data from the click event
        """
        x_data = event.xdata
        y_data = event.ydata

        if self.z_col != '':
            converted_point_str = self.ax.format_coord(x_data, y_data)
            point_str = converted_point_str.split(",")
            x_data = float(point_str[0].strip()[2:])
            y_data = float(point_str[1].strip()[2:])
            z_data = float(point_str[2].strip()[2:])

            return [x_data, y_data, z_data]
        else:
            return [x_data, y_data]

    def get_data_point(self, collections, x, y, z=None):
        """
        Gets the data point of the closest point to the click
        """
        prev_point, prev_err = [], 0

        for collection in collections:
            for point in collection.get_offsets():
                if len(prev_point) == 0:
                    if len(point) == 3:
                        prev_point = [point[0], point[1], point[2]]
                        prev_err = np.sqrt(
                            (x - prev_point[0]) ** 2 + (y - prev_point[1]) ** 2 + (z - prev_point[2]) ** 2)
                    else:
                        prev_point = [point[0], point[1]]
                        prev_err = np.sqrt((x - prev_point[0]) ** 2 + (y - prev_point[1]) ** 2)
                else:
                    if len(point) == 3:
                        temp_point = [point[0], point[1], point[2]]
                        temp_err = np.sqrt(
                            (x - temp_point[0]) ** 2 + (y - temp_point[1]) ** 2 + (z - temp_point[2]) ** 2)
                    else:
                        temp_point = [point[0], point[1]]
                        temp_err = np.sqrt((x - temp_point[0]) ** 2 + (y - temp_point[1]) ** 2)
                    if temp_err < prev_err:
                        prev_err, prev_point = temp_err, temp_point

        return prev_point

    def calculate_distance(self, point):
        """
        Calculates distance between the two most recently clicked points
        """
        distance = 0

        if self.last_point[0] == -1 and self.last_point[1] == -1:
            self.last_point = point
        else:
            self.old_point = self.last_point
            self.last_point = point
            if len(point) == 3:
                distance = np.sqrt(
                    (self.old_point[0] - self.last_point[0]) ** 2 + (self.old_point[1] - self.last_point[1]) ** 2 + (
                                self.old_point[2] - self.last_point[2]) ** 2)
            else:
                distance = np.sqrt(
                    (self.old_point[0] - self.last_point[0]) ** 2 + (self.old_point[1] - self.last_point[1]) ** 2)

        return distance

    def display_distance(self, event, distance):
        """
        Displays distance at the top of the frame
        """
        self.label_var.set("Distance Between Last Two Selected Points: " + str(distance) + " " + str(self.unit_string))

        def resize_label(event):
            pageWidth = event.width
            try:
                self.label_var.config(wraplength=math.floor(pageWidth / 2))
            except Exception:
                pass

        self.bind('<Configure>', resize_label)

    def createPlot(self, event=None):
        """
        Creates graph of data points. Handles both 2D and 3D data.
        """
        if hasattr(self, "ax"):
            x0, x1, y0, y1 = self.ax.get_xlim()[0], self.ax.get_xlim()[1], self.ax.get_ylim()[0], self.ax.get_ylim()[1]
            if x0 != self.plotDims[0][1] or x1 != self.plotDims[0][1] or y0 != self.plotDims[1][0] or y1 != \
                    self.plotDims[1][1]:
                zoomed = True
            else:
                zoomed = True
            self.plotDims = [[x0, x1], [y0, y1]]
            self.ax.clear()
            initialPlot = False
        else:
            initialPlot = True

            if self.z_col != '':
                self.ax = self.fig.add_subplot(111, projection='3d')
                self.ax.set_zlabel(self.options['unit_type'])
            else:
                self.ax = self.fig.add_subplot(111)

        self.ax.set_xlabel(self.options['unit_type'])
        self.ax.set_ylabel(self.options['unit_type'])

        if self.options['name_column'] != '':
            names = self.data_frame[self.options['name_column']].unique()
            self.filter_names_from_user_options(names, self.options)

            # Deprecation Warning: "Creating an ndarray from ragged rested sequences is deprecated. Specify 'dtype=object'""
            np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)

            names = list(filter(None, names))

            for n in names:
                if type(n) != str:
                    names.remove(n)

            colors = cm.rainbow(np.linspace(0, 1, len(names)))

            if initialPlot:
                self.points = []
                for i in range(len(names)):
                    self.points.append(Dataset())

                for i in range(len(names)):
                    name = names[i]
                    color = colors[i]
                    df_filtered = self.data_frame.loc[self.data_frame[self.options['name_column']] == name]
                    self.x = df_filtered[self.x_col].values.flatten()
                    self.x = self.x * self.x_ratio
                    self.y = df_filtered[self.y_col].values.flatten()
                    self.y = self.y * self.y_ratio

                    for j in range(len(self.x)):
                        xj, yj = self.x[j], self.y[j]

                        if self.z_col != "":
                            zj = df_filtered[self.z_col].values.flatten()[j]
                            zj *= self.z_col_ratio

                            self.points[i].addpoint(colors[i], xj, yj, zj)
                        else:
                            self.points[i].addpoint(colors[i], xj, yj)

            for i in range(len(names)):
                if self.z_col != "":
                    # hull = ss.ConvexHull(np.vstack((self.points[i].getx(), self.points[i].gety(), self.points[i].getz())).T)
                    self.ax.scatter3D(self.points[i].getx(), self.points[i].gety(), self.points[i].getz(),
                                      color=self.points[i].getcolors(), label=names[i], picker=True)
                else:
                    self.ax.scatter(self.points[i].getx(), self.points[i].gety(), color=self.points[i].getcolors(),
                                    label=names[i], picker=True)

            self.ax.legend()
        else:
            if initialPlot:
                self.points = Dataset()
                color = '#1f77b4'

                self.x = self.data_frame[self.x_col].values.flatten()
                self.y = self.data_frame[self.y_col].values.flatten()
                # self.x = np.true_divide(self.x, self.cal_ratio)
                # self.y = np.true_divide(self.y, self.cal_ratio)

                for j in range(len(self.x)):
                    xj, yj = self.x[j], self.y[j]

                    if self.z_col != '':
                        zj = self.data_frame[self.z_col].values.flatten()[j]
                        zj *= self.z_col_ratio
                        self.points.addpoint(color, xj, yj, zj)
                    else:
                        self.points.addpoint(color, xj, yj)

            if self.z_col != "":
                self.ax.scatter(self.points.getx(), self.points.gety(), self.points.getz(),
                                color=self.points.getcolors(), picker=True)
            else:
                self.ax.scatter(self.points.getx(), self.points.gety(), color=self.points.getcolors(), picker=True)

        if initialPlot:
            x0, x1, y0, y1 = self.ax.get_xlim()[0], self.ax.get_xlim()[1], self.ax.get_ylim()[0], self.ax.get_ylim()[1]
            self.defaultDims = [[x0, x1], [y0, y1]]
            self.defaultDimsfordelete = [[x0, x1], [y0, y1]]

            self.plotDims = self.defaultDims
            x_range = self.plotDims[0][1] - self.plotDims[0][0]
            y_range = self.plotDims[1][1] - self.plotDims[1][0]
            if self.z_col == "":
                self.ax.set_aspect(1)

        if initialPlot == False and zoomed:
            self.ax.set_xlim(self.plotDims[0][0], self.plotDims[0][1])
            self.ax.set_ylim(self.plotDims[1][0], self.plotDims[1][1])

        if self.image_name != '' and self.z_col == '':
            self.ax.imshow(self.img, extent=[self.ax.get_xlim()[0], self.ax.get_xlim()[1], self.ax.get_ylim()[0],
                                             self.ax.get_ylim()[1]])
        self.canvas.draw()

    def get_min(self, arr):
        """
        Get the minimum value of array
        """
        min_val = arr[0]
        for x in arr:
            if x < min_val:
                min_val = x
        return min_val

    def get_max(self, arr):
        """
        Get the maximum value of array
        """
        max_val = arr[0]
        for x in arr:
            if x > max_val:
                max_val = x
        return max_val

    def filter_names_from_user_options(self, names, options):
        """
        Filter which names are included in the data based on user input
        """
        if options['names_list'] != '':
            names_input = HeatMapPage.process_string_input(options['names_list'])
            for i in range(len(names)):
                if not isinstance(names[i], str):
                    names[i] = None
                elif HeatMapPage.standardize_string(names[i]) not in names_input:
                    names[i] = None

    @staticmethod
    def process_string_input(str_input):
        """
        Tokenizes string list input into a list of strings that are standardized
        """
        if ',' in str_input:
            str_input = str_input.split(',')
        elif ';' in str_input:
            str_input = str_input.split(';')
        else:
            str_input = shlex.split(str_input)
        str_input = [HeatMapPage.standardize_string(token) for token in str_input]
        return str_input

    @staticmethod
    def standardize_string(str_input):
        """
        Standardizes string, removes outer whitespace and sets to lower-case
        """
        return str_input.strip().lower()

    def get_columns_from_options(self, options):
        """
        Get the x, y, and z columns from the user options
        """
        return options['x_column'], options['y_column'], options['z_column']

    def get_calibration_ratio(self, data_frame, options):
        """
        Get the calibration ratio from user input. If calibration points are not included, default value is 1.

        """
        i1 = options['begin_calibration_index']
        i2 = options['end_calibration_index']
        if i1 == '' or i2 == '' or options['known_distance'] == '':
            return 1
        x1 = data_frame[options['x_column']][int(i1)]
        y1 = data_frame[options['y_column']][int(i1)]
        x2 = data_frame[options['x_column']][int(i2)]
        y2 = data_frame[options['y_column']][int(i2)]

        return float(options['known_distance']) / np.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))


# used to be in zoo.py
class ZooMapperToolbar(NavigationToolbar2Tk):
    """
    Class to handle options on graph
    """
    toolitems = (
        ('Home', 'Reset original view', 'home', 'home'),
        ('Back', 'Back to  previous view', 'back', 'back'),
        ('Forward', 'Forward to next view', 'forward', 'forward'),
        (None, None, None, None),
        ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
        ('Zoom', 'Zoom to rectangle\nRight click to reset zoom', 'zoom_to_rect', 'zoom'),
        ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
        (None, None, None, None),
        ('Save', 'Save the figure', 'filesave', 'save_figure'),
    )

    def __init__(self, *args, **kwargs):
        super(ZooMapperToolbar, self).__init__(*args, **kwargs)


# used to be in zoo.py
class Dataset(object):
    """
    Custom class to handle a data set. Can add points to the data and retrieve values.
    """

    def __init__(self):
        self.x = []
        self.y = []
        self.z = []
        self.names = []
        self.colors = []

    def addx(self, x):
        self.x.append(x)

    def addy(self, y):
        self.y.append(y)

    def addz(self, z):
        self.z.append(z)

    def delx(self, x):
        self.x.pop(x)

    def dely(self, y):
        self.y.pop(y)

    def delz(self, z):
        self.z.pop(z)

    def addname(self, name):
        self.names.append(str(name))

    def addcolor(self, color):
        self.colors.append(color)
  
    def delcolor(self, color):
        self.colors.pop(color)

    def addpoint(self, color, x, y, z=None, name=None):
        self.addx(x)
        self.addy(y)
        if z != None:
            self.addz(z)
        if name != None:
            self.addname(name)
        self.addcolor(color)

    def delpoint(self, points, z=None, name=None):
        # print(len(self.x))
        for p in points:
            # print(p)
            self.delx(p)
            self.dely(p)
            if z != None:
                self.delz(p)
            # if name != None:
            #     self.addname(name)
            self.delcolor(p)
        # print(len(self.x))
        
    def getx(self):
        return self.x

    def gety(self):
        return self.y

    def getz(self):
        return self.z

    def getnames(self):
        return self.names

    def getcolors(self):
        return self.colors

    def modcolor(self, i, c):
        self.colors[i] = c


class StartPage(tk.Frame):
    """
    Class for home page of the application.
    """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="Zoo Mapper", font=LARGE_FONT, bg=BACKGROUND_COLOR)
        # label.pack(pady=10, padx=10)

        # self.grid(in_ = parent, row = 0, column = 0, columnspan = 3, rowspan = 3, sticky = NSEW)

        style = Style()
        style.configure('TButton', font=BUTTON_FONT,
                        borderwidth='4')
        style.map('TButton', foreground=[('active', '!disabled', 'green')],
                  background=[('active', 'black')])

        button1 = ttk.Button(self, text="New Import", style="TButton",
                             command=lambda: controller.get_spreadsheet())
        button1.grid(row=1, column=0, sticky=S)

        button2 = ttk.Button(self, text="Load Import", style="TButton",
                             command=lambda: controller.load_import(self))
        button2.grid(row=2, column=0)

        button3 = ttk.Button(self, text="Graph",
                             command=lambda: controller.show_frame(HeatMapPage))
        button3.grid(row=3, column=0, sticky=N)

        button4 = ttk.Button(self, text="Calculate Extent Polygon",
                             command=lambda: self.handle_button4_click())
        button4.grid(row=4, column=0, sticky=N)

        button5 = ttk.Button(self, text="Calculate Kernel Density", command=lambda: self.handle_button5_click())
        button5.grid(row=5, column=0, sticky=N)

        buttons = {button1, button2, button3, button4, button5}

        canvas = Canvas(self, width=800, height=507)  # width and height of the logo.jpg image

        windowWidth = parent.winfo_screenwidth()
        windowHeight = parent.winfo_screenheight()

        canvas.grid(row=0, column=1, rowspan=6)

        cols, rows = self.grid_size()

        enclosure_image = Label(image="")
        enclosure_image.pack()

        def changeScale(event):
            """
            Handles scaling of application as window is resized
            """
            pageWidth = event.width
            pageHeight = event.height
            # print(str(pageWidth)+", "+str(pageHeight))

            label.config(wraplength=math.floor(pageWidth / 2))
            label.grid(row=0, column=0, sticky=S)

            self.grid_rowconfigure(0, pad=pageHeight / 4)

            for r in range(1, rows):
                self.grid_rowconfigure(r, minsize=math.floor(pageHeight / 8))
            for c in range(0, cols):
                self.grid_columnconfigure(c, minsize=math.floor(pageWidth / 2))

            image = PIL.Image.open('resources/Logo.jpg')

            if pageHeight < 507 and pageWidth / 2 < 800:
                canvas.grid_forget()
                self.grid_columnconfigure(0, minsize=pageWidth)
                self.grid_rowconfigure(0, pad=0)
                label.config(wraplength=math.floor(pageWidth * (4 / 5)))
            elif pageHeight < 507:
                imgW, imgH = math.floor(800 * (pageHeight / 507)), pageHeight
                image = image.resize((imgW, imgH))
                canvas.config(width=imgW, height=imgH)
            elif pageWidth / 2 < 800:
                imgW, imgH = math.floor(pageWidth / 2), math.floor(507 * (pageWidth / 1600))
                image = image.resize((imgW, imgH))
                canvas.config(width=imgW, height=imgH)
                if pageWidth < 800:
                    self.grid_columnconfigure(0, minsize=pageWidth)
                    canvas.grid(row=5, column=0, sticky=N)
                    self.grid_rowconfigure(0, pad=0)
                    label.config(wraplength=math.floor(pageWidth * (4 / 5)))
                else:
                    canvas.grid(row=0, column=1, rowspan=6, sticky="")

            if pageHeight >= 507 and pageWidth / 2 >= 800:
                imgW, imgH = 800, 507
                image = image.resize((imgW, imgH))
                canvas.config(width=imgW, height=imgH)

            image = ImageTk.PhotoImage(image)
            canvas.background = image
            bg = canvas.create_image(0, 0, anchor=tk.NW, image=image)

        parent.bind('<Configure>', changeScale)

    def handle_button4_click(self):
        win32api.ShellExecute(0, 'open', 'C:\\Program Files (x86)\\ArcGIS\\ArcGIS10.2\\python.exe',
                              'D:\\zoo-mapper\\src\\main\\miniboundary.py', '', 1)
    def handle_button5_click(self):
            win32api.ShellExecute(0, 'open', 'C:\\Program Files (x86)\\ArcGIS\\ArcGIS10.2\\python.exe',
                                  'D:\\zoo-mapper\\src\\main\\kerneldensity.py', '', 1)
