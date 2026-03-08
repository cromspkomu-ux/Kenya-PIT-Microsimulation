# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 20:56:40 2022

@author: wb305167
"""
import json
from tkinter import *
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from tkinter.messagebox import showinfo
from tkinter import filedialog

from threading import Thread

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
from super_combo import super_combo
#from taxcalc import *

from PIL import Image,ImageTk
   
def tab2(self, tax_type):
    self.year_value_pairs_policy_dict = 1
    self.vars[tax_type + '_display_revenue_table'] = 1
    self.save_inputs()

    # --- super_combo section first ---
    self.tab_generate_revenue_policy = super_combo(
        self.TAB2, self.current_law_policy,
        'row_label', 'value', 0.01, 0.20,
        editable_field_year=1, num_combos=1
    )
    (self.button_generate_revenue_policy, self.block_widget_dict) = self.tab_generate_revenue_policy.display_widgets(self.TAB2)
    self.button_generate_revenue_policy.configure(command=self.clicked_generate_policy_revenues)

    # --- Spacer ---
    spacer = tk.Frame(self.TAB2, height=10)
    spacer.pack()

    # --- Reform file input + button section ---
    bottom_frame = tk.Frame(self.TAB2)
    bottom_frame.pack(fill='x', anchor='nw', pady=(20, 10))  # Top padding of 20px

    tk.Label(bottom_frame, text="Input Reform File:").pack(side=tk.LEFT, padx=(10, 2))

    self.input_file_var = tk.StringVar(value="reform_input.csv")
    entry_file = tk.Entry(bottom_frame, textvariable=self.input_file_var, width=40)
    entry_file.pack(side=tk.LEFT, padx=5)

    def select_file():
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.input_file_var.set(filename)

    btn_browse = tk.Button(bottom_frame, text="Browse", command=select_file)
    btn_browse.pack(side=tk.LEFT)

    # Add a separate row for the generate button
    reform_button_frame = tk.Frame(self.TAB2)
    reform_button_frame.pack(anchor='w', padx=20, pady=(5, 10))
    
    btn_generate_from_file = tk.Button(
        reform_button_frame,
        text="Generate Policy Revenue from Reform File",
        command=lambda: self.clicked_generate_policy_revenues_from_reform_file(self.input_file_var.get())
    )
    btn_generate_from_file.pack()

    return
