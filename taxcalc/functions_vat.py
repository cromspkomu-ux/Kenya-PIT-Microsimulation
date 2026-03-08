
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
def cal_CONS_Non_Food(CONS_Clothing_Footwear,	CONS_Housing, 
                      CONS_Hhold_Goods_Services, CONS_Health, CONS_Transport, 
                      CONS_Communication, CONS_Recreation_Culture, CONS_Education, 
                      CONS_Restaurants_Hotels,	 CONS_Miscellaneous, CONS_Non_Food):
    """
    """
    CONS_Non_Food = (CONS_Clothing_Footwear + CONS_Housing + 
                  CONS_Hhold_Goods_Services + CONS_Health + CONS_Transport + 
                  CONS_Communication + CONS_Recreation_Culture + CONS_Education + 
                  CONS_Restaurants_Hotels + CONS_Miscellaneous)    
    return CONS_Non_Food

@iterate_jit(nopython=True)
def cal_CONS_Other(CONS_Clothing_Footwear,	CONS_Housing, 
                   CONS_Hhold_Goods_Services, CONS_Health, CONS_Transport, 
                   CONS_Communication, CONS_Recreation_Culture, CONS_Education, 
                   CONS_Restaurants_Hotels,	 CONS_Miscellaneous, CONS_Other):
    """
    """
    CONS_Other = (CONS_Clothing_Footwear + CONS_Housing + 
                  CONS_Hhold_Goods_Services + CONS_Health + CONS_Transport + 
                  CONS_Communication + CONS_Recreation_Culture + CONS_Education + 
                  CONS_Restaurants_Hotels + CONS_Miscellaneous)
    return CONS_Other

@iterate_jit(nopython=True)
def cal_CONS_Total(CONS_Food, CONS_Other, CONS_Total):
    """
    """
    CONS_Total = CONS_Food + CONS_Other
    return CONS_Total

@iterate_jit(nopython=True)
def cal_Applicable_Elasticity_Food(elasticity_consumption_food_threshold, elasticity_consumption_food_value, CONS_Total, applicable_elasticity_food):
    """
    Compute consumption after adjusting for behavior.
    """
    elasticity_consumption_threshold0 = elasticity_consumption_food_threshold[0]
    elasticity_consumption_threshold1 = elasticity_consumption_food_threshold[1]
    #elasticity_consumption_threshold2 = elasticity_pit_taxable_income_threshold[2]
    elasticity_consumption_value0=elasticity_consumption_food_value[0]
    elasticity_consumption_value1=elasticity_consumption_food_value[1]
    elasticity_consumption_value2=elasticity_consumption_food_value[2]
    if CONS_Total<=0:
        applicable_elasticity_food=0
    elif CONS_Total<elasticity_consumption_threshold0:
        applicable_elasticity_food=elasticity_consumption_value0
    elif CONS_Total<elasticity_consumption_threshold1:
        applicable_elasticity_food=elasticity_consumption_value1
    else:
        applicable_elasticity_food=elasticity_consumption_value2
    return applicable_elasticity_food

@iterate_jit(nopython=True)
def cal_Applicable_Elasticity_Non_Food(elasticity_consumption_non_food_threshold, elasticity_consumption_non_food_value, CONS_Total, applicable_elasticity_non_food):
    """
    Compute consumption after adjusting for behavior.
    """
    elasticity_consumption_threshold0 = elasticity_consumption_non_food_threshold[0]
    elasticity_consumption_threshold1 = elasticity_consumption_non_food_threshold[1]
    #elasticity_consumption_threshold2 = elasticity_pit_taxable_income_threshold[2]
    elasticity_consumption_value0=elasticity_consumption_non_food_value[0]
    elasticity_consumption_value1=elasticity_consumption_non_food_value[1]
    elasticity_consumption_value2=elasticity_consumption_non_food_value[2]
    if CONS_Total<=0:
        applicable_elasticity_non_food=0
    elif CONS_Total<elasticity_consumption_threshold0:
        applicable_elasticity_non_food=elasticity_consumption_value0
    elif CONS_Total<elasticity_consumption_threshold1:
        applicable_elasticity_non_food=elasticity_consumption_value1
    else:
        applicable_elasticity_non_food=elasticity_consumption_value2
    return applicable_elasticity_non_food

@iterate_jit(nopython=True)
def cal_CONS_Food_behavior_and_vat(rate_Food, rate_Food_curr_law, applicable_elasticity_food, CONS_Food, vat_Food):
    """
    Compute consumption after adjusting for behavior.
    """
    rate=rate_Food
    rate_curr_law=rate_Food_curr_law
    # Compute the fractional change of VAT rate safely
    frac_change_of_vat_rate = (rate - rate_curr_law) / (1+rate_curr_law)
    frac_change_of_consumption = applicable_elasticity_food*frac_change_of_vat_rate
    CONS_Food_behavior = CONS_Food*(1+frac_change_of_consumption)
    vat_Food = rate_Food*CONS_Food_behavior
    return vat_Food

@iterate_jit(nopython=True)
def cal_CONS_Non_Food_behavior_and_vat(rate_Alcohol_Tobacco, rate_Alcohol_Tobacco_curr_law,
                                      rate_Clothing_Footwear,	rate_Clothing_Footwear_curr_law,
                                      rate_Housing,	rate_Housing_curr_law,
                                      rate_Hhold_Goods_Services,	rate_Hhold_Goods_Services_curr_law,
                                      rate_Health,	rate_Health_curr_law,
                                      rate_Transport,	rate_Transport_curr_law,
                                      rate_Communication,	rate_Communication_curr_law,
                                      rate_Recreation_Culture,	rate_Recreation_Culture_curr_law,
                                      rate_Education,	rate_Education_curr_law,
                                      rate_Restaurants_Hotels,	rate_Restaurants_Hotels_curr_law,
                                      rate_Miscellaneous,	rate_Miscellaneous_curr_law,	CONS_Alcohol_Tobacco, 
                                      CONS_Clothing_Footwear, CONS_Housing, CONS_Hhold_Goods_Services, 
                                      CONS_Health, CONS_Transport, CONS_Communication, CONS_Recreation_Culture, 
                                      CONS_Education, CONS_Restaurants_Hotels, CONS_Miscellaneous,                                   
                                      applicable_elasticity_non_food, vat_Non_Food):
    """
    Compute consumption after adjusting for behavior.
    """ 
    
    frac_change_of_consumption_Alcohol_Tobacco = applicable_elasticity_non_food*((rate_Alcohol_Tobacco - rate_Alcohol_Tobacco_curr_law) / (1+rate_Alcohol_Tobacco_curr_law))
    frac_change_of_consumption_Clothing_Footwear = applicable_elasticity_non_food*((rate_Clothing_Footwear - rate_Clothing_Footwear_curr_law) / (1+rate_Clothing_Footwear_curr_law))
    frac_change_of_consumption_Housing = applicable_elasticity_non_food*((rate_Housing - rate_Housing_curr_law) / (1+rate_Housing_curr_law))
    frac_change_of_consumption_Hhold_Goods_Services = applicable_elasticity_non_food*((rate_Hhold_Goods_Services - rate_Hhold_Goods_Services_curr_law) / (1+rate_Hhold_Goods_Services_curr_law))
    frac_change_of_consumption_Health = applicable_elasticity_non_food*((rate_Health - rate_Health_curr_law) / (1+rate_Health_curr_law))
    frac_change_of_consumption_Transport = applicable_elasticity_non_food*((rate_Transport - rate_Transport_curr_law) / (1+rate_Transport_curr_law))
    frac_change_of_consumption_Communication = applicable_elasticity_non_food*((rate_Communication - rate_Communication_curr_law) / (1+rate_Communication_curr_law))
    frac_change_of_consumption_Recreation_Culture = applicable_elasticity_non_food*((rate_Recreation_Culture - rate_Recreation_Culture_curr_law) / (1+rate_Recreation_Culture_curr_law))
    frac_change_of_consumption_Education = applicable_elasticity_non_food*((rate_Education - rate_Education_curr_law) / (1+rate_Education_curr_law))
    frac_change_of_consumption_Restaurants_Hotels = applicable_elasticity_non_food*((rate_Restaurants_Hotels - rate_Restaurants_Hotels_curr_law) / (1+rate_Restaurants_Hotels_curr_law))
    frac_change_of_consumption_Miscellaneous = applicable_elasticity_non_food*((rate_Miscellaneous - rate_Miscellaneous_curr_law) / (1+rate_Miscellaneous_curr_law))

    CONS_Alcohol_Tobacco_behavior = CONS_Alcohol_Tobacco*(1+frac_change_of_consumption_Alcohol_Tobacco)
    CONS_Clothing_Footwear_behavior = CONS_Clothing_Footwear*(1+frac_change_of_consumption_Clothing_Footwear)
    CONS_Housing_behavior = CONS_Housing*(1+frac_change_of_consumption_Housing)
    CONS_Hhold_Goods_Services_behavior = CONS_Hhold_Goods_Services*(1+frac_change_of_consumption_Hhold_Goods_Services)
    CONS_Health_behavior = CONS_Health*(1+frac_change_of_consumption_Health)
    CONS_Transport_behavior = CONS_Transport*(1+frac_change_of_consumption_Transport)
    CONS_Communication_behavior = CONS_Communication*(1+frac_change_of_consumption_Communication)
    CONS_Recreation_Culture_behavior = CONS_Recreation_Culture*(1+frac_change_of_consumption_Recreation_Culture)
    CONS_Education_behavior = CONS_Education*(1+frac_change_of_consumption_Education)
    CONS_Restaurants_Hotels_behavior = CONS_Restaurants_Hotels*(1+frac_change_of_consumption_Restaurants_Hotels)
    CONS_Miscellaneous_behavior = CONS_Miscellaneous*(1+frac_change_of_consumption_Miscellaneous)

    vat_Alcohol_Tobacco = rate_Alcohol_Tobacco*CONS_Alcohol_Tobacco_behavior
    vat_Clothing_Footwear = rate_Clothing_Footwear*CONS_Clothing_Footwear_behavior
    vat_Housing = rate_Housing*CONS_Housing_behavior
    vat_Hhold_Goods_Services = rate_Hhold_Goods_Services*CONS_Hhold_Goods_Services_behavior
    vat_Health = rate_Health*CONS_Health_behavior
    vat_Transport = rate_Transport*CONS_Transport_behavior
    vat_Communication = rate_Communication*CONS_Communication_behavior
    vat_Recreation_Culture = rate_Recreation_Culture*CONS_Recreation_Culture_behavior
    vat_Education = rate_Education*CONS_Education_behavior
    vat_Restaurants_Hotels = rate_Restaurants_Hotels*CONS_Restaurants_Hotels_behavior
    vat_Miscellaneous = rate_Miscellaneous*CONS_Miscellaneous_behavior


    vat_Non_Food = (vat_Alcohol_Tobacco + vat_Clothing_Footwear + vat_Housing +
                    vat_Hhold_Goods_Services + vat_Health + vat_Transport +
                    vat_Communication + vat_Recreation_Culture + vat_Education +
                    vat_Restaurants_Hotels + vat_Miscellaneous)
   
    return vat_Non_Food

@iterate_jit(nopython=True)
def cal_vat(vat_Food, vat_Non_Food, vatax):
    vatax = vat_Food + vat_Non_Food
    return vatax
