# -*- coding: utf-8 -*-
"""
Created on Sat Apr 26 16:39:02 2025

@author: ssj34
"""

import pandas as pd
import json

def checknan(value):
    if (value=="nan"):
        value=""
    return value
    
df = pd.read_csv("tax_incentives_benchmark_input.csv")
final_json = {}
policy_json={}
cols = list(df.columns)
for idx, row in df.iterrows():
    field_name=str(row['field_name'])
    print(field_name)
    item = {}
    year_item = str(int(row['Year']))
    item[year_item] = [(row['value'])]    
    policy_json[field_name] = item
    
final_json["policy"]=policy_json

with open('tax_incentives_benchmark_pit_kenya.json', 'w') as f:
    json.dump(final_json, f, indent=4)
    
print(f"JSON successfully written {final_json}")

