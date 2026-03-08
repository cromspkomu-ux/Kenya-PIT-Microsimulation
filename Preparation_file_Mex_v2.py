# -*- coding: utf-8 -*-

import pandas as pd

#Dataset for incomes
# Loading the dataset
file_path = r'C:\Users\Sayra Martínez\OneDrive\Documents\MIDP\4S\MP\Income.csv'
df2 = pd.read_csv(file_path)

df2['id_n'] = df2['folioviv'].astype('str')+'_'+df2['foliohog'].astype('str')+'_'+df2['numren'].astype('str')

df2['yearly_income'] =df2['ing_tri']*4
df2 = df2.rename(columns={'clave': 'income_group'})

# Pivot the data
pivoted_df2 = df2.pivot_table(index=['id_n','folioviv', 'foliohog', 'numren', 'entidad', 'est_dis', 'upm', 'factor'], 
                            columns='income_group', 
                            values='yearly_income', 
                            aggfunc='sum',
                            fill_value=0).reset_index()

# Define the dictionary with old column names as keys and new names as values
column_name_mapping = {
    'P001': 'wage_w_pr',
    'P002': 'piecework_w_pr',
    'P003': 'comissions_w_pr',
    'P004': 'overtime_w_pr',
    'P005': 'rewards_w_pr',
    'P006': 'bonus_w_pr',
    'P007': 'vacation_w_pr',
    'P008': 'profit_sharing_w_pr',
    'P009': 'christmas_bonus_w_pr',
    'P011': 'wage_b_pr',
    'P012': 'profit_b_pr',
    'P013': 'other_b_pr',
    'P014': 'wage_w_se',
    'P015': 'profit_sharing_w_se',
    'P016': 'christmas_bonus_w_se',
    'P018': 'wage_b_se',
    'P019': 'profit_b_se',
    'P020': 'other_b_se',
    'P021': 'other_other_lastmonth',
    'P022': 'other_other_prev5',
    'P023': 'rent_land',
    'P024': 'rent_building_mx',
    'P025': 'rent_building_abroad',
    'P026': 'interest_inv',
    'P027': 'interest_savings',
    'P028': 'interest_loans',
    'P029': 'interest_bonds',
    'P030': 'rent_intangibles',
    'P031': 'rent_other',
    'P032': 'transfers_pension_mx',
    'P033': 'transfers_pension_abroad',
    'P034': 'transfers_compensation_insurance',
    'P035': 'transfers_compensation_workaccident',
    'P036': 'transfers_compensation_layoff',
    'P037': 'transfers_scholarship_nongov',
    'P038': 'transfers_scholarship_gov',
    'P039': 'transfers_donation_nongov',
    'P040': 'transfers_donation_otherHH',
    'P041': 'transfers_othercountries',
    'P043': 'welfare_procampo',
    'P045': 'welfare_elders',
    'P048': 'welfare_other_social_benefits',
    'P049': 'welfare_other_nonreported',
    'P050': 'dividends',
    'P051': 'investment_withdrawal',
    'P052': 'payments_loan_otherHH',
    'P053': 'loan_except_mortgage',
    'P054': 'capital_jewelryorart',
    'P055': 'capital_bonds',
    'P056': 'capital_intangibles',
    'P057': 'inheritances',
    'P058': 'lotteries',
    'P059': 'capital_realproperty',
    'P060': 'capital_land',
    'P061': 'capital_m&e',
    'P062': 'capital_vehicles',
    'P063': 'capital_hhitems',
    'P064': 'loan_mortgage',
    'P065': 'life_insurance',
    'P066': 'other_financial_capital',
    'P067': 'income_member_under12',
    'P068': 'business_pr_industrial',
    'P069': 'business_pr_commercial',
    'P070': 'business_pr_services',
    'P071': 'business_pr_agriculture',
    'P072': 'business_pr_breeding',
    'P073': 'business_pr_reforestation',
    'P074': 'business_pr_fishing',
    'P075': 'business_se_industrial',
    'P076': 'business_se_commercial',
    'P077': 'business_se_services',
    'P078': 'business_se_agriculture',
    'P079': 'business_se_breeding',
    'P080': 'business_se_reforestation',
    'P081': 'business_se_fishing',
    'P101': 'welfare_scholarship_PROSPERA',
    'P102': 'welfare_scholarship_BJ',
    'P103': 'welfare_scholarship_JEF',
    'P104': 'welfare_older',
    'P105': 'welfare_disabilities',
    'P106': 'welfare_children_workingmothers',
    'P107': 'life_insurance_headshh',
    'P108': 'welfare_JCF'
}

pivoted_df2 = pivoted_df2.rename(columns=column_name_mapping)

pivoted_df2['total_residents'] = pivoted_df2.groupby('folioviv')['numren'].transform('sum')
pivoted_df2['weight'] = pivoted_df2['factor'] / pivoted_df2['total_residents']

# Calculate exempt incomes
pivoted_df2['exempt_total_income'] = pivoted_df2[[
    'transfers_scholarship_nongov', 'transfers_scholarship_gov', 'life_insurance_headshh',
    'welfare_procampo','welfare_elders', 'welfare_other_social_benefits', 'welfare_other_nonreported',
    'inheritances', 'welfare_scholarship_PROSPERA', 'welfare_scholarship_BJ', 'welfare_scholarship_JEF',
    'welfare_older', 'welfare_disabilities', 'welfare_children_workingmothers', 'welfare_JCF', 'transfers_compensation_insurance', 'transfers_compensation_workaccident']].sum(axis=1)

# Calculate taxable incomes fro bonus and overtime (93, section I)
pivoted_df2['overtime_bonus_w_t'] = pivoted_df2.apply(
    lambda row: max(
        (row['overtime_w_pr'] + row['rewards_w_pr'] + row['bonus_w_pr']) * 0.5,
        (row['overtime_w_pr'] + row['rewards_w_pr'] + row['bonus_w_pr']) - 25017.20) 
    if (row['wage_w_pr'] + row['wage_b_pr'] + row['wage_w_se'] + row['wage_b_se']) > 34639.2 
    else 0, axis=1)

# Calculate vacation_taxable (93, XIV)
pivoted_df2['vacation_t'] = pivoted_df2['vacation_w_pr'].apply(lambda x: max(x - 1443.30, 0))

# Calculate profit_sharing_taxable (93, XIV)
pivoted_df2['profit_sharing_t'] = (
    pivoted_df2['profit_sharing_w_pr'] + pivoted_df2['profit_sharing_w_se']
).apply(lambda total: max(total - 1443.30, 0))

# Calculate christmas_bonus_taxable (93, XIV)
pivoted_df2['christmas_bonus_t'] = (
   pivoted_df2['christmas_bonus_w_pr'] + pivoted_df2['christmas_bonus_w_se']
).apply(lambda total: max(total - 2886.60, 0))

# Calculate wage income from businesses (94, II and VI)
pivoted_df2['wage_bu_t'] = pivoted_df2.apply(
    lambda row: (row['wage_b_pr'] + row['profit_b_pr'] + row['other_b_pr'] +
                 row['wage_b_se'] + row['profit_b_se'] + row['other_b_se'])
    if (row['wage_b_pr'] + row['wage_b_se']) < 75000000 else 0,
    axis=1
)

# Layoff incomes: If total amount is greater than one month wage, separate the last month wage and accumulate 
pivoted_df2['layoff_w_t'] = pivoted_df2.apply(
    lambda row: 
    (row['wage_w_pr'] + row['wage_w_se']) / 2 / 12
    if row['transfers_compensation_layoff'] <= (row['wage_w_pr'] + row['wage_w_se']) / 2 / 12 
    else row['transfers_compensation_layoff'],
    axis=1
)

# Layoff incomes: If total amount is greater than one month wage, we have to apply the corresponding tax rate to the rest     
pivoted_df2['layoff_pending'] = pivoted_df2.apply(
    lambda row: 
    row['transfers_compensation_layoff'] - ((row['wage_w_pr'] + row['wage_w_se']) / 2 / 12) 
    if row['transfers_compensation_layoff'] > ((row['wage_w_pr'] + row['wage_w_se']) / 2 / 12)
    else 0,
    axis=1
)    

#calculate taxable income from pensions
pivoted_df2['pensions_w_t'] = pivoted_df2.apply(
    lambda row: max((row['transfers_pension_mx'] + row['transfers_pension_abroad']) - 519588, 0),
    axis=1
)
    
columns_wages = [
    'wage_w_pr', 'piecework_w_pr', 'comissions_w_pr', 'overtime_bonus_w_t', 
    'vacation_t', 'profit_sharing_t', 'christmas_bonus_t', 
    'wage_bu_t', 'wage_w_se', 'other_other_lastmonth', 'other_other_prev5', 
    'pensions_w_t', 'layoff_w_t'
]

# Estimate income from all incomes treated as wages
pivoted_df2['income_wages_t'] = pivoted_df2[columns_wages].sum(axis=1)

# Estimate income_rent_t as the sum of building, land, intangibles, and other
pivoted_df2['income_rent_t'] = (
    0.65 * (pivoted_df2['rent_building_abroad'] + pivoted_df2['rent_building_mx'] + pivoted_df2['rent_land']) 
    + pivoted_df2['rent_intangibles'] + pivoted_df2['rent_other']
)

# Estimate the taxable amount for land and real property and divide by 20 as is allowed for those assets
pivoted_df2['income_capital_t'] = (
    pivoted_df2['capital_jewelryorart'] +
    pivoted_df2['capital_intangibles'] +
    (pivoted_df2['capital_realproperty'] - 5882244.2).apply(lambda x: max(x, 0)) / 20 +  # Apply condition for capital_realproperty and divide by 20
    (pivoted_df2['capital_land'] - 105303.24).apply(lambda x: max(x, 0)) / 20 +  # Apply condition for capital_land and divide by 20
    pivoted_df2['capital_m&e'] +
    pivoted_df2['capital_vehicles'] +
    pivoted_df2['capital_hhitems']
)

# Compute the pending_capital_t as per your formula
pivoted_df2['pending_capital_t'] = (
    (pivoted_df2['capital_realproperty'] - ((pivoted_df2['capital_realproperty'] - 5882244.2).apply(lambda x: max(x, 0)) / 20)) + 
    (pivoted_df2['capital_land'] - ((pivoted_df2['capital_land'] - 105303.24).apply(lambda x: max(x, 0)) / 20))
)

pivoted_df2['income_dividend_t'] = pivoted_df2['dividends']

pivoted_df2['income_interest_t'] = pivoted_df2[['interest_inv', 'interest_savings', 'interest_loans',
    'interest_bonds', 'investment_withdrawal', 'payments_loan_otherHH', 'life_insurance'
    ]].sum(axis=1)

pivoted_df2['income_other_t'] = pivoted_df2['other_financial_capital'] + pivoted_df2['transfers_othercountries']

pivoted_df2['income_donations_t'] = pivoted_df2.apply(
    lambda row: max((row['transfers_donation_nongov'] + row['transfers_donation_otherHH']) - 105303.24, 0),
    axis=1
)

# Calculate taxable business incomes. I am assuming that all those with business incomes below 3,500,000, pay in the simplifie regime.
# List of columns involved in the sum for business_general_t (combining all relevant columns)
columns_for_general_t = [
    'business_pr_agriculture', 'business_pr_breeding', 'business_pr_reforestation',
    'business_pr_fishing', 'business_se_agriculture', 'business_se_breeding',
    'business_se_reforestation', 'business_se_fishing', 'business_pr_industrial',
    'business_pr_commercial', 'business_pr_services', 'business_se_industrial',
    'business_se_commercial', 'business_se_services'
]

# List of columns involved in the sum for agapes_b_t calculation (agriculture, breeding, reforestation, fishing only)
columns_for_agapes_b_t = [
    'business_pr_agriculture', 'business_pr_breeding', 'business_pr_reforestation',
    'business_pr_fishing', 'business_se_agriculture', 'business_se_breeding',
    'business_se_reforestation', 'business_se_fishing'
]

# List of columns involved in the sum for business_simp_t calculation (industrial, commercial, services)
columns_for_simp_t = [
    'business_pr_industrial', 'business_pr_commercial', 'business_pr_services',
    'business_se_industrial', 'business_se_commercial', 'business_se_services'
]

# Calculate the sum for business_general_t (combining all columns)
pivoted_df2['business_general_t_sum'] = pivoted_df2[columns_for_general_t].sum(axis=1)

# Calculate the sum for agapes_b_t (agriculture, breeding, reforestation, fishing)
pivoted_df2['agapes_b_t_sum'] = pivoted_df2[columns_for_agapes_b_t].sum(axis=1)

# Create business_general_t based on the sum condition
pivoted_df2['business_general_t'] = pivoted_df2['business_general_t_sum'].apply(
    lambda x: x if x > 3500000 else 0
)

# Create agapes_b_t based on the sum condition
pivoted_df2['agapes_b_t'] = pivoted_df2['agapes_b_t_sum'].apply(
    lambda x: max(x - 900000, 0) if x <= 3500000 else 0
)

# Create business_simp_t based on the sum condition for business_general_t
pivoted_df2['business_simp_t'] = pivoted_df2.apply(
    lambda row: row[columns_for_simp_t].sum() + row['agapes_b_t'] if row['business_general_t_sum'] <= 3500000 else 0,
    axis=1
)

# Drop the temporary sum columns if not needed
pivoted_df2.drop(columns=['business_general_t_sum', 'agapes_b_t_sum'], inplace=True)

# Define the output path for the new CSV
output_path = r'C:\Users\Sayra Martínez\OneDrive\Documents\MIDP\4S\MP\income_pit_mex.csv'
# Save the pivoted DataFrame to a new CSV
pivoted_df2.to_csv(output_path, index=False)

print(f"File saved to: {output_path}")

# Load the dataset for personal expenses
file_path = r'C:\Users\Sayra Martínez\OneDrive\Documents\MIDP\4S\MP\conjunto_de_datos_gastospersona_enigh2022_ns.csv'
df3 = pd.read_csv(file_path)

df3['id_n'] = df3['folioviv'].astype('str')+'_'+df3['foliohog'].astype('str')+'_'+df3['numren'].astype('str')

df3['gasto_tri'] = pd.to_numeric(df3['gasto_tri'], errors='coerce')
df3['yearly_expenses'] = df3['gasto_tri'] * 4
df3 = df3.rename(columns={'clave': 'expenses'})

# I have defined a specific list of expense codes to focus on, as the raw data contains over 700 codes.
# By filtering for only those that are related to deductions, I can create a more manageable and focused dataset for analysis.
gasto_codes = {
    'E002': 'Elementary_school',
    'E003': 'Secondary_school',
    'E004': 'Highschool',
    'E013': 'School_transport',
    'J001': 'Medical_services_childbirth',
    'J002': 'Hospitalization_childbirth',
    'J003': 'Clinical_tests_childbirth',
    'J004': 'Prescribed_medications_childbirth',
    'J007': 'Medical_consultations_preg',
    'J008': 'Dental_consultations_preg',
    'J009': 'Prescribed_medications_preg',
    'J011': 'Clinical_tests_preg',
    'J012': 'Hospitalization_preg',
    'J015': 'Other_services_preg',
    'J016': 'General_medical_consultations',
    'J017': 'Specialist_medical_consultations',
    'J018': 'Dental_consultations',
    'J019': 'Clinical_tests',
    'J039': 'Professional_services_other',
    'J040': 'Hospitalization_other',
    'J041': 'Clinical_tests_other',
    'J042': 'Prescribed_medications_other',
    'J043': 'Services_ambulance_other',
    'J065': 'Glasses',
    'J066': 'Hearing_aids',
    'J067': 'Orthopedic_therapy_devices',
    'J068': 'Orthopedic_device_or_repairs',
    'J069': 'Other_services',
    'J070': 'Hospital_clinic_fees',
    'J071': 'Insurance_medical_fees',
    'N002': 'Funerals',
    'N014': 'Charity_contributions',
    'T916': 'Financial_capital_expenditures'
}

# Filter the dataset to include only the rows for the selected gasto codes
df3_filtered = df3[df3['expenses'].isin(gasto_codes.keys())]

# Pivot the dataset by type of expense
df3_pivot = df3_filtered.pivot_table(
    index=['id_n','folioviv', 'foliohog', 'numren'
],
    columns='expenses',
    values=['yearly_expenses'],
    aggfunc='sum',
    fill_value=0
)

df3_pivot = df3_pivot.rename(columns=gasto_codes)

# Flatten the multi-level columns created by the pivot and rename them as the last level (gasto code names)(if I delete this, I get a row with all columns call "yearly_expenses" and a second row with the names in gasto_code)
df3_pivot.columns = [
    f'{col[1]}' for col in df3_pivot.columns
]

# Check which columns from gasto_codes exist in the pivoted DataFrame
expense_columns = [col for col in df3_pivot.columns if col not in ['id_n', 'folioviv', 'foliohog', 'numren']]

df3_pivot['deductible_expenses'] = df3_pivot[expense_columns].sum(axis=1)

# Display the updated DataFrame
#print(df3_pivot[['deductible_expenses']].head())

#df3_pivot = df3_pivot.apply(pd.to_numeric, errors='coerce')

# Reset the index to make the DataFrame clean
df3_pivot.reset_index(inplace=True)

# Define the full path to save the output CSV
output_path2 = r'C:\Users\Sayra Martínez\OneDrive\Documents\MIDP\4S\MP\gasto_pivoted.csv'

# Save the resulting dataset to the new CSV file in the specified folder
df3_pivot.to_csv(output_path2, index=False)


#CREATE A MERGED DATABASE 
merged_df = pd.merge(pivoted_df2, df3_pivot, on=['id_n', 'folioviv', 'foliohog', 'numren'], how='left')

merged_df['Year']=2022
#merged_df['id_n'] = merged_df['folioviv'].astype('str')+'_'+merged_df['foliohog'].astype('str')+'_'+merged_df['numren'].astype('str')

# Check the first few rows to verify
print(merged_df[['id_n','folioviv', 'foliohog', 'numren']].head())

# Arranging
desired_column_order = [
    'id_n', 'folioviv', 'foliohog', 'numren', 'entidad', 'est_dis', 'upm', 'factor', 'total_residents', 'weight','Year',
    'income_wages_t', 'deductible_expenses', 'income_rent_t', 'income_capital_t', 'income_dividend_t', 'income_interest_t',
    'income_other_t', 'income_donations_t', 'exempt_total_income'
] + [col for col in merged_df.columns if col not in [
    'id_n', 'folioviv', 'foliohog', 'numren', 'entidad', 'est_dis', 'upm', 'factor', 'total_residents', 'weight', 'Year',
    'income_wages_t', 'deductible_expenses', 'income_rent_t', 'income_capital_t', 'income_dividend_t', 'income_interest_t',
    'income_other_t', 'income_donations_t', 'exempt_total_income'
]]
        
# Reorder the columns in the dataframe
merged_df = merged_df[desired_column_order]

# List of columns to exclude from coercion
exclude_columns = ['id_n', 'folioviv', 'foliohog', 'numren', 'entidad', 'est_dis', 'upm', 'factor', 'total_residents', 'weight', 'Year']

# Select the columns to apply coercion on (all columns except the ones in exclude_columns)
cols_to_convert = merged_df.columns.difference(exclude_columns)

# Apply numeric conversion to the selected columns
merged_df[cols_to_convert] = merged_df[cols_to_convert].apply(pd.to_numeric, errors='coerce')

# Fill NaN values with 0 for all columns
merged_df = merged_df.fillna(0)

print(merged_df[['id_n','folioviv', 'foliohog', 'numren']].head())

# Output the first few rows to verify the result
#print(merged_df.head())

# Define the path to save the merged dataset
output_merged_path = r'C:\Users\Sayra Martínez\OneDrive\Documents\MIDP\4S\MP\income_expenses_mex.csv'

# Save the resulting merged dataset to a new CSV file
merged_df.to_csv(output_merged_path, index=False)
