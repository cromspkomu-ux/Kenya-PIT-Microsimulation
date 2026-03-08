# -*- coding: utf-8 -*-
"""
Created on Sat Apr 26 16:39:02 2025

@author: ssj34
"""

import pandas as pd
import json


df = pd.read_csv("record_variables_input.csv")
final_json = {'read': {}, 'calc': {}}
cols = list(df.columns)
for idx, row in df.iterrows():
    print(row['field_category'])
    field_name=row['field_name']
    item = {}
    item['required'] = str(row['required'])
    item['type'] = str(row['type'])
    item['desc'] = str(row['desc'])
    print(row['2015'])
    form = {}
    form[str('2015')] = str(row['2015'])
    item['form']=form
    if (row['field_category']=='read'):
        item['cross_year'] = str(row['cross_year'])
        item['attribute'] = str(row['attribute'])
    final_json[row['field_category']][field_name]=item

with open('record_variables_botswana.json', 'w') as f:
    json.dump(final_json, f, indent=4)
    
print(final_json)



output_json = 'record_variables_botswana.json'
with open(output_json, 'w') as f:
    json.dump(final_json, f, indent=4)

print(f"JSON successfully written to {output_json}")

