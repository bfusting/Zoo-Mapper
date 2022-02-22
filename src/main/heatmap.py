#!/usr/bin/python
# -*- coding: utf-8 -*-
import tkinter
from tkinter.ttk import Style
from tkinter import *

import pandas
from PIL import ImageTk, Image

import json
import os
import re


class HeatMapOptionsBox(tkinter.Toplevel):

    """
    Class that handles import configuration for a spreadsheet.
    Creats a tkinter Toplevel window for selecting columns from the spreadsheet to fill different fields for analysis
    """

    def __init__(
        self,
        startpage,
        data_frame,
        out_dict,
        spreadsheet_path,
        sheet_name=None,
        width=800,
        height=800,
        saved_defaults=None,
        ):
        tkinter.Toplevel.__init__(self)
        self.attributes('-topmost', 'true')
        self.startpage = startpage
        self.spreadsheet_path = spreadsheet_path
        self.x_column_var = tkinter.StringVar()
        self.y_column_var = tkinter.StringVar()
        self.z_column_var = tkinter.StringVar()
        self.name_column_var = tkinter.StringVar()
        self.sheet_name_var = tkinter.StringVar()

        self.filter_entry_dict = {}
        self.entry_dict_ind = 0
        self.filter_entries_list = []

        self.habitat_image = ''

        self.columns_list = data_frame.columns

        self.calibration_points = False

        self.column_types_dict = data_frame.dtypes.to_dict()

        if sheet_name is not None:
            self.sheet_name_var.set(sheet_name)

        # self.top = tkinter.Toplevel(None)

        frm = tkinter.Frame(self, width=width, height=height,
                            borderwidth=4, relief='ridge')
        self.frame = frm
        self.frame.config(bg='white')

        # frm.pack_propagate(0)

        frm.pack(fill='both', expand=True)

        # left column of frm

        leftfrm = tkinter.Frame(
            frm,
            width=600,
            height=600,
            bg='white',
            pady=50,
            padx=70,
            )
        leftfrm.grid(row=0, column=0, padx=10, pady=2)
        self.leftframe = leftfrm

        # right column of frm

        rightfrm = tkinter.Frame(
            frm,
            width=600,
            height=600,
            bg='white',
            pady=50,
            padx=70,
            )
        rightfrm.grid(row=0, column=1, padx=10, pady=2)
        self.rightframe = rightfrm

        # additional rightmost column in case of adding filters

        rightmostfrm = tkinter.Frame(
            frm,
            width=0,
            height=0,
            bg='white',
            pady=50,
            padx=70,
            )
        rightmostfrm.grid(row=0, column=3, padx=10, pady=2)
        self.rightmostframe = rightmostfrm

        # Add Ratio's for different Axes

        self.x_ratio_label = tkinter.Label(leftfrm,
                text='X Distance Ratio', bg='white')
        self.x_ratio_label.pack(padx=4, pady=4)

        self.x_ratio_entry = tkinter.Entry(leftfrm)
        if saved_defaults != None:
            self.x_ratio_entry.insert(0, saved_defaults['x_ratio'])
        self.x_ratio_entry.pack(padx=4, pady=4)

        self.y_ratio_label = tkinter.Label(leftfrm,
                text='Y Distance Ratio', bg='white')
        self.y_ratio_label.pack(padx=4, pady=4)

        self.y_ratio_entry = tkinter.Entry(leftfrm)
        if saved_defaults != None:
            self.y_ratio_entry.insert(0, saved_defaults['y_ratio'])
        self.y_ratio_entry.pack(padx=4, pady=4)

        self.z_ratio_label = tkinter.Label(leftfrm,
                text='Z Distance Ratio', bg='white')
        self.z_ratio_label.pack(padx=4, pady=4)

        self.z_ratio_entry = tkinter.Entry(leftfrm)
        if saved_defaults != None:
            self.z_ratio_entry.insert(0, saved_defaults['z_ratio'])
        self.z_ratio_entry.pack(padx=4, pady=4)

        # unit type label (left side)

        self.unit_type_label = tkinter.Label(leftfrm, text='Units',
                bg='white')
        self.unit_type_label.pack(pady=4)

        self.unit_type_entry = tkinter.Entry(leftfrm)
        if saved_defaults != None:
            self.unit_type_entry.insert(0, saved_defaults['unit_type'])
        self.unit_type_entry.pack(pady=4)

        # begin ind label (left side)

        self.begin_ind_label = tkinter.Label(leftfrm, text='First Row',
                bg='white')
        self.begin_ind_label.pack(padx=4, pady=4)

        self.begin_ind_entry = tkinter.Entry(leftfrm)
        if saved_defaults != None:
            self.begin_ind_entry.insert(0, saved_defaults['begin_index'
                    ])
        else:
            self.begin_ind_entry.insert(0, '2')
        self.begin_ind_entry.pack(pady=4)

        # end ind label (left side)

        self.end_ind_label = tkinter.Label(leftfrm, text='Last Row',
                bg='white')
        self.end_ind_label.pack(padx=4, pady=4)

        self.end_ind_entry = tkinter.Entry(leftfrm)
        if saved_defaults != None:
            self.end_ind_entry.insert(0, saved_defaults['end_index'])
        else:
            self.end_ind_entry.insert(0, str(data_frame.index.stop + 1))
        self.end_ind_entry.pack(pady=4)

        # name column label (left side)

        self.name_column_label = tkinter.Label(leftfrm,
                text='Name Column', bg='white')
        self.name_column_label.pack(pady=4)

        self.name_column_dropdown = tkinter.OptionMenu(leftfrm,
                self.name_column_var, *self.filterOptions([['Name'],
                ['Focal']], self.columns_list))
        if saved_defaults != None:
            self.name_column_var.set(saved_defaults['name_column'])
        self.name_column_dropdown.pack(pady=4)

        # names list label (left side)

        self.names_list_label = tkinter.Label(leftfrm,
                text='List Selected Names', bg='white')
        self.names_list_label.pack(pady=4)

        self.names_list_entry = tkinter.Entry(leftfrm)
        if saved_defaults != None:
            self.names_list_entry.insert(0, saved_defaults['names_list'
                    ])
        self.names_list_entry.pack(pady=4)

        # x column label (right side)

        self.x_column_label = tkinter.Label(rightfrm, text='X Column',
                bg='white')
        self.x_column_label.pack(pady=4)

        self.x_column_dropdown = tkinter.OptionMenu(rightfrm,
                self.x_column_var, *self.filterOptions([['X'], ['Long'
                ]], self.columns_list))
        if saved_defaults != None:
            self.x_column_var.set(saved_defaults['x_column'])
        self.x_column_dropdown.pack(pady=4)

        # y column label (right side)

        self.y_column_label = tkinter.Label(rightfrm, text='Y Column',
                bg='white')
        self.y_column_label.pack(pady=4)

        self.y_column_dropdown = tkinter.OptionMenu(rightfrm,
                self.y_column_var, *self.filterOptions([['Y'], ['Lat'
                ]], self.columns_list))
        if saved_defaults != None:
            self.y_column_var.set(saved_defaults['y_column'])
        self.y_column_dropdown.pack(pady=4)

        # z column label (right side)

        self.z_column_label = tkinter.Label(rightfrm, text='Z Column',
                bg='white')
        self.z_column_label.pack(pady=4)

        self.z_column_dropdown = tkinter.OptionMenu(rightfrm,
                self.z_column_var, *self.filterOptions([['Z'], ['Depth'
                ], ['Height']], self.columns_list))
        if saved_defaults != None:
            self.z_column_var.set(saved_defaults['z_column'])
        self.z_column_dropdown.pack(pady=4)

        # submit (right side)

        b_submit = tkinter.Button(rightfrm, text='Submit')
        b_submit['command'] = lambda : \
            self.send_options_to_dict(out_dict, data_frame)
        b_submit.pack(padx=4, pady=4)

        b_save = tkinter.Button(rightfrm, text='Save Import')
        b_save['command'] = lambda : self.save_import(out_dict)
        b_save.pack(padx=4, pady=4)

        # cancel (right side)

        b_cancel = tkinter.Button(rightfrm, text='Cancel')
        b_cancel['command'] = self.destroy
        b_cancel.pack(padx=4, pady=4)

        # add new filter (right side)

        b_add_new_filter = tkinter.Button(rightfrm, text='Add Filter')
        b_add_new_filter['command'] = lambda : self.add_filter_entry()
        b_add_new_filter.pack()

        if saved_defaults != None:
            saved_filters = saved_defaults['filters']
            for (column, entry) in saved_filters.items():
                self.add_filter_entry(column, entry)
        b_add_calibration = tkinter.Button(rightfrm,
                text='Add Calibration Points')
        b_add_calibration['command'] = lambda : \
            self.add_calibration_entry()
        b_add_calibration.pack(padx=4, pady=4)

        b_add_new_filter = tkinter.Button(rightfrm, text='Add Habitat')
        b_add_new_filter['command'] = lambda : self.get_image()
        b_add_new_filter.pack(pady=4)

        self.image_column_label = tkinter.Label(rightfrm,
                text=self.habitat_image)
        if saved_defaults != None:
            self.habitat_image = saved_defaults['habitat_image']
            self.image_column_label.config(text=self.habitat_image)
        self.image_column_label.pack()

        if saved_defaults != None \
            and (saved_defaults['begin_calibration_index'] != ''
                 or saved_defaults['end_calibration_index'] != ''
                 or saved_defaults['known_distance'] != ''):
            self.add_calibration_entry()
            self.begin_ind_calibration_entry.insert(0,
                    saved_defaults['begin_calibration_index'])
            self.end_ind_calibration_entry.insert(0,
                    saved_defaults['end_calibration_index'])
            self.known_distance_entry.insert(0,
                    saved_defaults['known_distance'])

    # Function to get image for enclosure

    def get_image(self):
        """
        Opens file selection window to choose an image. Stores the path to this image.
        """

        self.attributes('-topmost', 'false')
        self.image_column_label.destroy()
        imagename = tkinter.filedialog.askopenfilename(initialdir='',
                title='Select a File', filetypes=(('Image files',
                '*.png*'), ('Image files', '*.jpg'), ('Image files',
                '*.jpeg'), ('all files', '*.*')))
        if imagename:
            img = ImageTk.PhotoImage(Image.open(imagename))
            self.habitat_image = imagename

        self.image_column_label = tkinter.Label(self.rightframe,
                text=self.habitat_image)
        self.image_column_label.pack()

        self.attributes('-topmost', 'true')

    def add_calibration_entry(self):
        """
        Adds calibration point fields to the import window.
        """

        self.calibration_points = True
        self.begin_ind_calibration = tkinter.Label(self.rightmostframe,
                text='Calibration Point 1 Row', bg='white')
        self.begin_ind_calibration.pack(pady=4)

        self.begin_ind_calibration_entry = \
            tkinter.Entry(self.rightmostframe)
        self.begin_ind_calibration_entry.pack(pady=4)

        # end ind calibration (left side)

        self.end_ind_calibration = tkinter.Label(self.rightmostframe,
                text='Calibration Point 2 Row', bg='white')
        self.end_ind_calibration.pack(pady=4)

        self.end_ind_calibration_entry = \
            tkinter.Entry(self.rightmostframe)
        self.end_ind_calibration_entry.pack(pady=4)

        # known distance label (left side)

        self.known_distance_label = tkinter.Label(self.rightmostframe,
                text='Known Calibration Distance', bg='white')
        self.known_distance_label.pack(pady=4)

        self.known_distance_entry = tkinter.Entry(self.rightmostframe)
        self.known_distance_entry.pack(pady=4)

    #

    def add_filter_entry(self, filter_column=None, filter_entry=None):
        """
        Adds filter field to import window. Allows user to specify another column in the data to filter the data by.
        """

        new_filter_label = tkinter.Label(self.rightmostframe,
                text='Custom Column Filter:')
        new_filter_label.pack(pady=4)

        my_str = tkinter.StringVar()

        new_filter_columns = tkinter.OptionMenu(self.rightmostframe,
                my_str, *self.columns_list)
        if filter_column != None:
            my_str.set(filter_column)
        new_filter_columns.pack(pady=4)

        new_filter_entry = tkinter.Entry(self.rightmostframe)
        if filter_entry != None:
            new_filter_entry.insert(0, filter_entry)
        new_filter_entry.pack(pady=4)

        self.filter_entries_list.append((new_filter_entry, my_str))

    def filterOptions(self, phrases, columnlist):
        """
        Filters a list of columns by a set of keywords.

        How it works:
        Phrases is a two-tier list consisting of phrases that each consist of words.
        The filter allows columns that contain at least one phrase, and to contain a phrase all of its words must be present.
        Ex. If phrases = [['Space','Z'],['Height']] then the column must contain ('Space' AND 'Z') OR 'Height' (not case-sensitive) 
        """

        filtered = []
        for col in columnlist:
            outerFlag = False
            for phrase in phrases:
                innerFlag = True
                for word in phrase:
                    if word.lower() not in col.lower():  # Requires all words of phrase to be in col
                        innerFlag = False
                if innerFlag:  # Requires at least one phrase to be in col
                    outerFlag = True
            if outerFlag:
                filtered.append(col)
        if not filtered:
            filtered = ['']
        return filtered

    def create_options(self, saving=False):
        """
        Takes vaues from input fields and creates a dict of them
        """

        self.get_filters(saving)

        options = {}
        if self.calibration_points:
            options['begin_calibration_index'] = \
                self.begin_ind_calibration_entry.get()
            options['end_calibration_index'] = \
                self.end_ind_calibration_entry.get()
            options['known_distance'] = self.known_distance_entry.get()
        else:
            options['begin_calibration_index'] = ''
            options['end_calibration_index'] = ''
            options['known_distance'] = ''
        options['unit_type'] = re.sub(r'[^A-Za-z0-9_]', '',
                self.unit_type_entry.get()).capitalize()
        options['begin_index'] = self.begin_ind_entry.get()
        options['end_index'] = self.end_ind_entry.get()
        options['names_list'] = self.names_list_entry.get()
        options['name_column'] = self.name_column_var.get()
        options['x_column'] = self.x_column_var.get()
        options['y_column'] = self.y_column_var.get()
        options['z_column'] = self.z_column_var.get()
        options['filters'] = self.filter_entry_dict
        options['habitat_image'] = self.habitat_image
        options['x_ratio'] = self.x_ratio_entry.get()
        options['y_ratio'] = self.y_ratio_entry.get()
        options['z_ratio'] = self.z_ratio_entry.get()
        options['sheet_name'] = self.sheet_name_var.get()

        return options

    def get_filters(self, saving):
        """
        Retrieves values from filter fields and creates entries in a filter dict
        """

        self.filter_entry_dict.clear()

        for (entry, var) in self.filter_entries_list:
            if entry.get() != '' and var.get() != '' and not saving:
                self.filter_entry_dict[var.get()] = entry.get()
            elif saving and var.get() != '':
                self.filter_entry_dict[var.get()] = entry.get()

    def adjust_options(self, options):
        """
        Adjusts the values of index fields by a factor of 2 to be handled by backend.
        The reason for this is the pandas dataframe starts from index 0 while the imported data starts from row 2.
        """

        if options['begin_calibration_index']:
            options['begin_calibration_index'] = \
                str(int(options['begin_calibration_index']) - 2)
        if options['end_calibration_index']:
            options['end_calibration_index'] = \
                str(int(options['end_calibration_index']) - 2)
        options['begin_index'] = str(int(options['begin_index']) - 2)
        options['end_index'] = str(int(options['end_index']) - 2)
        return options

    def check_options(self, options, data_frame):
        """
        Checks for any empty required fields, invalid entries, and other errors in the import configuration.
        """

        isValid = True
        errCode = []
        indexStart = 2
        indexEnd = data_frame.index.stop + 1
        if not options['x_column']:
            isValid = False
            errCode.append('A')
        elif self.column_types_dict[options['x_column']] \
            not in ['float64', 'int64']:
            isValid = False
            errCode.append('B')
        if not options['y_column']:
            isValid = False
            errCode.append('C')
        elif self.column_types_dict[options['y_column']] \
            not in ['float64', 'int64']:
            isValid = False
            errCode.append('D')
        if options['z_column'] != '' \
            and self.column_types_dict[options['z_column']] \
            not in ['float64', 'int64']:
            isValid = False
            errCode.append('E')
        if options['begin_calibration_index'] \
            and (int(options['begin_calibration_index']) < indexStart
                 or int(options['begin_calibration_index']) > indexEnd):
            isValid = False
            errCode.append('F')
        if options['end_calibration_index'] \
            and (int(options['end_calibration_index']) < indexStart
                 or int(options['end_calibration_index']) > indexEnd):
            isValid = False
            errCode.append('G')
        if not options['begin_index']:
            isValid = False
            errCode.append('H')
        if not options['end_index']:
            isValid = False
            errCode.append('I')
        if options['begin_index'] and (int(options['begin_index'])
                < indexStart or int(options['begin_index']) > indexEnd):
            isValid = False
            errCode.append('J')
        if options['end_index'] and (int(options['end_index'])
                < indexStart or int(options['end_index']) > indexEnd):
            isValid = False
            errCode.append('K')
        if 'H' not in errCode and 'I' not in errCode \
            and int(options['begin_index']) > int(options['end_index']):
            isValid = False
            errCode.append('L')
        return (isValid, errCode)

    def input_error(self, errCode):
        """
        Creates error messages depending on which errors were found in the import.
        """

        errMsg = ''
        if 'A' in errCode:
            errMsg = errMsg + 'X column is not specified.\n'
        if 'B' in errCode:
            errMsg = errMsg + 'X Column is not numeric.\n'
        if 'C' in errCode:
            errMsg = errMsg + 'Y column is not specified.\n'
        if 'D' in errCode:
            errMsg = errMsg + 'Y Column is not numeric.\n'
        if 'E' in errCode:
            errMsg = errMsg + 'Z Column is not numeric.\n'
        if 'F' in errCode:
            errMsg = errMsg \
                + 'Calibration point 1 row is out of range.\n'
        if 'G' in errCode:
            errMsg = errMsg \
                + 'Calibration point 2 row is out of range.\n'
        if 'H' in errCode:
            errMsg = errMsg + 'First row is not specified.\n'
        if 'I' in errCode:
            errMsg = errMsg + 'Last row is not specified.\n'
        if 'J' in errCode:
            errMsg = errMsg + 'First row is out of range.\n'
        if 'K' in errCode:
            errMsg = errMsg + 'Last row is out of range.\n'
        if 'L' in errCode:
            errMsg = errMsg \
                + 'First and last rows are not compatible.\n'
        self.wait_window(InputError(self, errMsg.rstrip('\n')))

    def send_options_to_dict(self, out_dict, data_frame):
        """
        Creates return dict of import options to be used by main program. If there are errors, will instead call error handling method.
        """

        options = self.create_options()
        (flag, errCode) = self.check_options(options, data_frame)
        if flag:
            options = self.adjust_options(options)
            (d, key) = out_dict
            d[key] = options
            self.destroy()
        else:
            self.attributes('-topmost', 'false')
            self.input_error(errCode)
            self.attributes('-topmost', 'true')

    def save_import(self, out_dict):
        """
        Opens up save window to save the current import
        """

        self.attributes('-topmost', 'false')
        options = self.create_options(saving=True)
        options['spreadsheet_path'] = self.spreadsheet_path
        self.wait_window(SavePage(self, options))
        self.attributes('-topmost', 'true')


class SavePage(tkinter.Toplevel):

    """
    A Toplevel window that allows the user to save the current import configuration.
    Handles overwriting existing save files and errors in the file name.
    """

    def __init__(self, parent, options):
        tkinter.Toplevel.__init__(self, parent)
        self.options = options
        self.title('Save Import')

        tkinter.Toplevel.wm_geometry(self, '300x120')

        frm = tkinter.Frame(self, width=300, height=100, borderwidth=4,
                            relief='raised')
        self.frame = frm
        self.frame.config(bg='white')
        frm.pack(fill='both', expand=True)

        self.enter_text = tkinter.Label(frm,
                text='Enter name for import')
        self.enter_text.pack(pady=10)

        self.save_name_entry = tkinter.Entry(frm, width=30)
        self.save_name_entry.pack(pady=4)

        b_cancel = tkinter.Button(frm, text='Cancel')
        b_cancel['command'] = lambda : self.destroy()
        b_cancel.pack(side=tkinter.RIGHT, padx=4, pady=4)

        b_save = tkinter.Button(frm, text='Save')
        b_save['command'] = lambda : \
            self.save(self.save_name_entry.get())
        b_save.pack(side=tkinter.RIGHT, padx=4, pady=4)

    def save(self, file_name):
        """
        Handles saving of the import with the specified name
        Includes error checking for invalid characters, empty name, and file already existing
        """

        invalid_characters = [
            '#',
            '%',
            '&',
            '{',
            '}',
            '\\',
            '<',
            '>',
            '*',
            '?',
            '/',
            '^',
            '$',
            '!',
            '\'',
            '"',
            ':',
            '@',
            '+',
            '`',
            '|',
            '=',
            '~',
            ]
        if len(file_name) == 0:
            message = 'The import name cannot be empty'
            SaveError(self, message)
        elif any(invalid_char in file_name for invalid_char in
                 invalid_characters):
            used_invalid_chars = [invalid_char for invalid_char in
                                  invalid_characters if invalid_char
                                  in file_name]
            display_text = ','.join(used_invalid_chars)
            message = \
                'The import name cannot contain the character(s) \n ' \
                + display_text
            SaveError(self, message)
        else:
            if self.file_exists(file_name):
                SaveOverwrite(self, file_name)
            else:
                self.create_json_file(file_name)
                self.destroy()

    def create_json_file(self, file_name):
        """
        Creates json file and writes given dict to it
        """

        with open('saves/' + file_name + '.json', 'w') as fp:
            json.dump(self.options, fp, indent=4)

    def file_exists(self, file_name):
        """
        Returns a bool representing whether a saved import already exists with a given name
        """

        already_exists = False
        for file in os.listdir('saves'):
            if file.endswith('.json'):
                if file[:-5] == file_name:
                    return True
        return False


class SaveError(tkinter.Toplevel):

    """
    Creates a new window that displays a message when there is an error when trying to save an import
    """

    def __init__(self, parent, message):
        tkinter.Toplevel.__init__(self, parent)

        self.title('Issue Saving')

        tkinter.Toplevel.wm_geometry(self, '300x100')

        frm = tkinter.Frame(self, borderwidth=4, relief='raised')
        self.frame = frm
        self.frame.config(bg='white')
        frm.pack(fill='both', expand=True)

        self.enter_text = tkinter.Label(frm, text=message)
        self.enter_text.pack(pady=10)

        b_ok = tkinter.Button(frm, text='OK')
        b_ok['command'] = lambda : self.destroy()
        b_ok.pack(side=tkinter.RIGHT, padx=4, pady=4)


class InputError(tkinter.Toplevel):

    """
    Creates a new window that displays a message when there is an error when trying to submit an import
    """

    def __init__(self, parent, message):
        tkinter.Toplevel.__init__(self, parent)
        self.title('Errors')
        height = 20 * message.count('.') + 80
        tkinter.Toplevel.wm_geometry(self, '320x' + str(height))
        frm = tkinter.Frame(self, borderwidth=4, relief='raised')
        self.frame = frm
        self.frame.config(bg='white')
        frm.pack(fill='both', expand=True)
        self.enter_text = tkinter.Label(frm, text=message)
        self.enter_text.pack(pady=10)

        b_ok = tkinter.Button(frm, text='OK')
        b_ok['command'] = lambda : self.destroy()
        b_ok.pack(side=tkinter.RIGHT, padx=4, pady=4)


class SaveOverwrite(tkinter.Toplevel):

    """
    Creates a new window that tells the user the import name is already saved and asks if they want to overwrite it
    """

    def __init__(self, parent, file_name):
        self.parent = parent
        tkinter.Toplevel.__init__(self, self.parent)

        self.title('Import Already Exists')

        tkinter.Toplevel.wm_geometry(self, '350x100')

        frm = tkinter.Frame(self, borderwidth=4, relief='raised')
        self.frame = frm
        self.frame.config(bg='white')
        frm.pack(fill='both', expand=True)

        self.enter_text = tkinter.Label(frm,
                text='There is already an import with the name "'
                + file_name
                + '" \n Would you like to overwrite the current saved import?'
                )
        self.enter_text.pack(pady=10)

        b_no = tkinter.Button(frm, text='NO')
        b_no['command'] = lambda : self.destroy()
        b_no.pack(side=tkinter.RIGHT, padx=4, pady=4)

        b_yes = tkinter.Button(frm, text='YES')
        b_yes['command'] = lambda : self.overwrite(file_name)
        b_yes.pack(side=tkinter.RIGHT, padx=4, pady=4)

    def overwrite(self, file_name):
        """
        Handles the saving of the file to overwrite
        """

        self.parent.create_json_file(file_name)
        self.parent.destroy()
