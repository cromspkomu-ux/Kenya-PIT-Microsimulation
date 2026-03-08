"""
pitaxcalc-demo functions that calculate personal income tax liability.
"""
# CODING-STYLE CHECKS:
# pycodestyle functions.py
# pylint --disable=locally-disabled functions.py

import math
import copy
import numpy as np
from taxcalc.decorators import iterate_jit

@iterate_jit(nopython=True)
def cal_capital_income(income_dividends_c, income_interest_c,     
                           capital_income):
    """
    Compute total gross income.
    """
    capital_income = (income_dividends_c + income_interest_c)
    return capital_income

@iterate_jit(nopython=True)
def cal_total_gross_income(income_wage_l, income_dividends_c, income_interest_c,     
                           total_gross_income):
    """
    Compute total gross income.
    """
    total_gross_income = (income_wage_l + income_dividends_c + income_interest_c)
    return total_gross_income

@iterate_jit(nopython=True)
def cal_pit_c(capital_income_rate_a, capital_income, pitax_c):
    """
    Compute PIT for Capital Income.
    """
    pitax_c = capital_income_rate_a*capital_income
    return pitax_c

@iterate_jit(nopython=True)
def calc_ti_behavior(rate1, rate2, rate3, rate4, rate5, tbrk1, 
                    tbrk2, tbrk3, tbrk4, tbrk5,
                    rate1_curr_law, rate2_curr_law, rate3_curr_law, 
                    rate4_curr_law, rate5_curr_law, tbrk1_curr_law, tbrk2_curr_law, 
                    tbrk3_curr_law, tbrk4_curr_law, tbrk5_curr_law,
                    elasticity_pit_taxable_income_threshold,
                    elasticity_pit_taxable_income_value, income_wage_l,
                    income_wage_behavior):
    """
    Compute taxable total income after adjusting for behavior.
    """  
    elasticity_taxable_income_threshold0 = elasticity_pit_taxable_income_threshold[0]
    elasticity_taxable_income_threshold1 = elasticity_pit_taxable_income_threshold[1]
    #elasticity_taxable_income_threshold2 = elasticity_pit_taxable_income_threshold[2]
    elasticity_taxable_income_value0=elasticity_pit_taxable_income_value[0]
    elasticity_taxable_income_value1=elasticity_pit_taxable_income_value[1]
    elasticity_taxable_income_value2=elasticity_pit_taxable_income_value[2]
    if income_wage_l<=0:
        elasticity=0
    elif income_wage_l<elasticity_taxable_income_threshold0:
        elasticity=elasticity_taxable_income_value0
    elif income_wage_l<elasticity_taxable_income_threshold1:
        elasticity=elasticity_taxable_income_value1
    else:
        elasticity=elasticity_taxable_income_value2

    if income_wage_l<0:
        marg_rate=0
    elif income_wage_l<=tbrk1:
        marg_rate=rate1
    elif income_wage_l<=tbrk2:
        marg_rate=rate2
    elif income_wage_l<=tbrk3:
        marg_rate=rate3        
    elif income_wage_l<=tbrk4:
        marg_rate=rate4
    else:         
        marg_rate=rate5
        
    if income_wage_l<0:
        marg_rate_curr_law=0
    elif income_wage_l<=tbrk1_curr_law:
        marg_rate_curr_law=rate1_curr_law
    elif income_wage_l<=tbrk2_curr_law:
        marg_rate_curr_law=rate2_curr_law
    elif income_wage_l<=tbrk3_curr_law:
        marg_rate_curr_law=rate3_curr_law
    elif income_wage_l<=tbrk4_curr_law:
        marg_rate_curr_law=rate4_curr_law         
    else:
        marg_rate_curr_law=rate5_curr_law
    
    frac_change_net_of_pit_rate = ((1-marg_rate)-(1-marg_rate_curr_law))/(1-marg_rate_curr_law)
    frac_change_income_wage = elasticity*(frac_change_net_of_pit_rate)  
    income_wage_behavior = income_wage_l*(1+frac_change_income_wage)
    return income_wage_behavior

@iterate_jit(nopython=True)
def cal_pit_w(rate1, rate2, rate3, rate4, rate5, tbrk1, tbrk2, tbrk3, tbrk4, tbrk5, income_wage_behavior, pitax_w):
    """
    Compute PIT.
    """
    inc=income_wage_behavior
    pitax_w = (rate1 * min(inc, tbrk1) +
               rate2 * min(tbrk2 - tbrk1, max(0., inc - tbrk1)) +
               rate3 * min(tbrk3 - tbrk2, max(0., inc - tbrk2)) +
               rate4 * min(tbrk4 - tbrk3, max(0., inc - tbrk3)) +
               rate5 * max(0., inc - tbrk4))
    return pitax_w

@iterate_jit(nopython=True)
def cal_total_pit(pitax_w, pitax_c, pitax):
    """
    Compute Total PIT.
    """
    pitax = pitax_w + pitax_c
    return pitax