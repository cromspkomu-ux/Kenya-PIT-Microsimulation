import pandas as pd
import numpy as np
from glob import glob

def taxamt(income, rate, bracket):
    """
    Compute tax amount given the specified taxable income
    and the specified progressive tax rate structure.
    """ 
    tax_amount = (
        rate[1] * min(income, bracket[1]) +
        rate[2] * min(bracket[2] - bracket[1], max(0, income - bracket[1])) +
        rate[3] * min(bracket[3] - bracket[2], max(0, income - bracket[2])) +
        rate[4] * min(bracket[4] - bracket[3], max(0, income - bracket[3])) +
        rate[5] * min(bracket[5] - bracket[4], max(0, income - bracket[4]))     
    )
    return tax_amount

def pit(income_array, rate, bracket):
    pitax=np.zeros(len(income_array))
    for i in range(len(income_array)):
        pitax[i]=taxamt(income_array[i], rate, bracket)
    return pitax

PATH = "C:/Users/ssj34/Documents/OneDrive/Other Missions and Projects/IMF Missions/Kenya/Kenya Tax Data/"

# Get files in order (adjust pattern as needed)
#files = sorted(glob(PATH+"PIT2023V5*.csv"))

files =["PIT2023V5.csv", "PIT2023V5_2.csv", "PIT2023V5_2.csv", 
        "PIT2023V5_3.csv", "PIT2023V5_4.csv", "PIT2023V5_5.csv", "PIT2023V5_6.csv"]
# Read the first file with headers
df_list = [pd.read_csv(PATH+files[0])]

# Read the rest WITHOUT headers, but reuse the first file's columns
for f in files[1:]:
    df = pd.read_csv(PATH+f, header=None)
    df.columns = df_list[0].columns
    df_list.append(df)

# Concatenate everything
final_df = pd.concat(df_list, ignore_index=True)

final_df.fillna(0, inplace=True)

final_df['other_income1'] = np.where((final_df['tot_emp_income']==0)&(final_df['total_tax_payable_less_relief']!=0), final_df['total_tax_payable_less_relief']/0.15, 0)
final_df['business_income1'] = 0
final_df['emp_income1'] = final_df['tot_emp_income']
final_df['total_income1'] = (final_df['emp_income1']+ 
                             final_df['other_income1']+ 
                             final_df['business_income1']+
                             final_df['chrg_inc_from_estate'])
final_df['mortgage_deduction1'] = np.where(final_df['mortage_interest']>final_df['home_own_saving_plan_dep'], 
                                           final_df['mortage_interest'],final_df['home_own_saving_plan_dep'])
final_df['tot_deductions1'] = (final_df['pension_contribution'] + 
                               final_df['mortgage_deduction1']+
                               final_df['hosp_tot_deposit_year'])
final_df['net_taxable_income1'] = (final_df['total_income1'] - 
                                   final_df['exemption_amt'] -  
                                   final_df['tot_deductions1'] - 
                                   final_df['other_income1'])
rate1 = [0, 0.1, 0.25, 0.30, 0.325, 0.35]
bracket1 = [0, 288000, 388000, 6000000, 9600000, 9e+99]
rate = [0, 0.1, 0.25, 0.30, 0.30, 0.30]
bracket = [0, 288000, 388000, 1e+99, 2e+99, 9e+99]
final_df['tax_payable1'] = pit(final_df['net_taxable_income1'], rate1, bracket1)
final_df['tax_on_other_income1'] = 0.10*final_df['other_income1']
final_df['total_tax_payable1'] = final_df['tax_payable1']+final_df['tax_on_other_income1']
final_df['total_tax_payable_less_relief1'] = (final_df['total_tax_payable1'] -
                                             final_df['personal_relief']-
                                             final_df['insurance_relief'])
print(final_df['total_tax_payable_less_relief1'].sum()/1e9)
# Optional: save to a new CSV
final_df.to_csv(PATH+"pit_combined.csv", index=False)
final_df_1 = final_df.drop_duplicates(subset=['unique_id', 'total_income1'], keep='last')
final_df_1.to_csv(PATH+"pit_combined_no_dupl.csv", index=False)
print(final_df_1['total_tax_payable_less_relief1'].sum()/1e9)

final_df_1 = pd.read_csv(PATH+"pit_combined_no_dupl.csv")
# Sampling
final_df_1=final_df_1[final_df_1['total_income1']>0]
final_df_1=final_df_1.sort_values(by=['total_income1'])
final_df_1=final_df_1.reset_index()
# allocate the data into bins
final_df_1['bin'] = pd.qcut(final_df_1['total_income1'], 10, labels=False)
final_df_1['weight']=1
# bin_ratio is the fraction of the number of records selected in each bin
# 1/10,...1/5, 1/1
bin_ratio=[40,40,40,40,40,20,20,20,10,1]
frames=[]
df={}
for i in range(len(bin_ratio)):
    # find out the size of each bin
    bin_size=len(final_df_1[final_df_1['bin']==i])//bin_ratio[i]
    # draw a random sample from each bin
    df[i]=final_df_1[final_df_1['bin']==i].sample(n=bin_size)
    df[i]['weight'] = bin_ratio[i]
    frames=frames+[df[i]]

pit_sample= pd.concat(frames)
pit_sample['interest_income1']=pit_sample['other_income1']
pit_sample['is_disabled'] = np.where(pit_sample['exemption_amt']>0,1,0)
pit_sample['has_mortgage'] = np.where((pit_sample['mortage_interest']>0)|(pit_sample['home_own_saving_plan_dep']>0),1,0)

pit_sample.to_csv('pit_kenya_wide.csv')

varlist = ['total_income1', 'total_tax_payable_less_relief1']
total_weight_sample = pit_sample['weight'].sum()
total_weight_population = final_df_1['weight'].sum()
#comparing the statistic of the population and sample
for var in varlist:
    pit_sample['weighted_'+var] = pit_sample[var]*pit_sample['weight']
    sample_sum = pit_sample['weighted_'+var].sum()
    population_sum = final_df_1[var].sum()
    print("            Sample Sum for ", var, " = ", sample_sum)
    print("        Population Sum for ", var, " = ", population_sum)
    print(" Sampling Error for Sum(%) ", var, " = ", "{:.2%}".format((population_sum-sample_sum)/population_sum))
    sample_mean = sample_sum/total_weight_sample
    population_mean = population_sum/total_weight_population
    print("           Sample Mean for ", var, " = ", sample_mean)
    print("       Population Mean for ", var, " = ", population_mean)
    print("Sampling Error for Mean(%) ", var, " = ", "{:.2%}".format((population_mean-sample_mean)/population_mean))    

pit_sample_thin = pit_sample[['unique_id', 'trp_id', 'station_name', 
                              'year_',
            'other_income1', 'interest_income1',
            'business_income1', 'emp_income1',
            'chrg_inc_from_estate',
            'total_income1', 'mortage_interest',
            'has_mortgage',
            'mortgage_deduction1', 
            'home_own_saving_plan_dep',
            'pension_contribution', 
            'hosp_tot_deposit_year',
            'tot_deductions1',
            'net_taxable_income1',
            'tax_payable1', 'tax_on_other_income1',
            'total_tax_payable1',
            'personal_relief',
            'insurance_relief',
            'is_disabled',
            'exemption_amt',
            'total_tax_payable_less_relief1', 'weight',
            'total_tax_payable_less_relief']]


pit_sample_thin = pit_sample_thin.rename(columns=
                    {'unique_id':'id_n',
                     'year_': 'Year',
                     'total_tax_payable_less_relief':'total_tax_payable_less_relief_old',
                     'other_income1':'other_income',
                     'interest_income1': 'interest_income',
                     'business_income1': 'business_income', 
                     'emp_income1': 'emp_income',
                     'mortgage_deduction1': 'mortgage_deduction1'
                     })

pit_sample_thin.to_csv('taxcalc/pit_kenya.csv', index=False)
df_weight = pit_sample_thin[['weight']].copy()

df_weight.columns = ['WT2023']
df_weight['WT2024'] = df_weight['WT2023']
df_weight['WT2025'] = df_weight['WT2023']
df_weight['WT2026'] = df_weight['WT2023']
df_weight['WT2027'] = df_weight['WT2023']
df_weight['WT2028'] = df_weight['WT2023']
df_weight['WT2029'] = df_weight['WT2023']
df_weight['WT2030'] = df_weight['WT2023']
df_weight['WT2031'] = df_weight['WT2023']
df_weight['WT2032'] = df_weight['WT2023']

df_weight.to_csv('taxcalc/pit_weights_kenya.csv', index=False)

#Calibration
# reweight using tax projections calibrated
tax_collection_2023_24_billion = 543.186
# synthetic data has only 100,000 observations
tax_collection_model_billion_2023 = 428.46
multiplicative_factor_2023 = tax_collection_2023_24_billion/tax_collection_model_billion_2023

# reweight using tax projections calibrated
tax_collection_2024_25_billion = 560.945
# synthetic data has only 100,000 observations
tax_collection_model_billion_2024 = 629.68
multiplicative_factor_2024 = tax_collection_2024_25_billion/tax_collection_model_billion_2024


pit_sample_thin = pd.read_csv('taxcalc/pit_kenya.csv')
pit_sample_thin['weight'] = multiplicative_factor_2023*pit_sample_thin['weight']
pit_sample_thin.to_csv('taxcalc/pit_kenya.csv')

df_weight = pd.read_csv('taxcalc/pit_weights_kenya.csv')
                 
df_weight['WT2023'] = multiplicative_factor_2023*df_weight['WT2023']
df_weight['WT2024'] = multiplicative_factor_2024*df_weight['WT2024']
df_weight['WT2025'] = df_weight['WT2024']
df_weight['WT2026'] = df_weight['WT2024']
df_weight['WT2027'] = df_weight['WT2024']
df_weight['WT2028'] = df_weight['WT2024']
df_weight['WT2029'] = df_weight['WT2024']
df_weight['WT2030'] = df_weight['WT2024']
df_weight['WT2031'] = df_weight['WT2024']
df_weight['WT2032'] = df_weight['WT2024']
df_weight.to_csv('taxcalc/pit_weights_kenya.csv')


# 2022-23 tax collection
# PAYE 494.979 bill
# Capital Gains  
# CIT 263.819 bill
# Domestic VAT 272.452 bill
# Domestic Excise 68.124 bill
# Excise on Betting 6.640 bill
# Import Duty 129.987 bill

# 2023-24 tax collection
# PAYE 543.186 bill
# Capital Gains 8.381 bill
# CIT 278.156 bill
# Domestic VAT 314.157 bill
# Domestic Excise 73.624 bill
# Excise on Betting 24.269 bill

# 2023 2022 July- 2022 Dec PAYE 230.875
# 2023 2022 July- 2023 Mar PAYE 352.573
# 2023 2022 July- 2023 June PAYE 494.904
# 2023 = July-Sept PAYE 123.044
# 2023 = July-Dec PAYE 256.302
# 2024 = Jan-Mar PAYE 
# 2023 Jan-Mar =  352.573-230.875 = 121.798
# 2023 Mar-Jun = 494.904 - 352.573 = 142.331
# 2023 July-Sept = 123.044
# 2023 Sept-Dec = 256.302-123.044 = 133.258
# 2023 PAYE = 121.798+142.331+123.044+133.258 = 520.431


#final_df
# CHECK
#'tot_deductions' = 'pension_contribution' + higher('mortage_interest','home_own_saving_plan_dep')
#                    +'hosp_tot_deposit_year'
# 'net_taxable_income' = 'tot_emp_income' + 'chrg_inc_from_estate'
#                        + Line number 9 (consolidated) - 'tot_deductions' - 'exemption_amt'
# 'tax_payable' = 'net_taxable_income' * Applicable Rates
# 'total_tax_payable_less_relief' = 'tax_payable' - 'personal_relief'-'insurance_relief'
# 'tax_credits' = 'tot_paye_deducted' +	'amnt_of_share_income' + 'tot_inst_tax_paid'
#                 + 'amt_tax_witheld' +	'advance_tax_paid' + 'amt_income_tax_paid'
#                 + 'amt_tax_relief' + 'witholding_tax'
#

# CALIBRATE BACKWARDS 
# set 'other_income1' = 0
# set 'other_income_tax_rate'=0.10
# set 'business_income1' = 0
# set 'emp_income1' = 'tot_emp_income'
# first calculate 'total_income1' = 'emp_income1'+ 'other_income1'+ 'business_income1'
# + 'chrg_inc_from_estate'
# 'mortgage_deduction' = max('mortage_interest','home_own_saving_plan_dep')
# then calculate 'tot_deductions1' = 'pension_contribution' + 'mortgage_deduction'
#                    +'hosp_tot_deposit_year'
# then calculate 'net_taxable_income1' = 'total_income1' - 'exemption_amt' -  'tot_deductions1' - 'other_income1'
# then calculate 'tax_payable1' = tax('net_taxable_income1') + tax(other_income1)
# 'total_tax_payable_less_relief1' = 'tax_payable1'- 'personal_relief'-'insurance_relief'

#'tot_emp_income' + 'chrg_inc_from_estate'	exempt_type_description	exemption_amt	net_taxable_income	tot_taxable_income	tax_payable	personal_relief	insurance_relief

#'tot_taxable_income' = 'chargeable_income'+'tot_emp_income'
#'net_taxable_income' = ('tot_taxable_income'-'pension_contribution'
#                       -'mortgage_interest_paid'-'home_own_saving_plan_dep')
#'tax_payable' = tax applied on 'net_taxable_income'
#'total_tax_payable_less_relief'= 'tax_payable'-'personal_relief'-'insurance_relief'
#'tax_rfnd_due' = ('total_tax_payable_less_relief' (self +wife)- 'tot_paye_deducted' 
#                   -'tax_credits')
# 
