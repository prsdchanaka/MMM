import pandas as pd
import numpy as np


import numpy as np
import re 
from collections import deque
from mmm_pre_zone import *
from mmm_pre_all import *

#ALL INDIA LEVEL ADSTOCK
def ad_stock_s_curve_u_all(data,var,hier,spc_hier,lr_list,decay_list):
    ad_stock_list=[]
    ad_stock_list2=[]
    
    lr_rate=float((lr_list[var]))
    decay=float(decay_list[var])
    
    ad_stock_value=0
    ad_stock_value2=0
    
    for index,row in data[data[hier]==spc_hier].iterrows():
        t=row[str(var)]
        #print(row['month'],row['Brand'],var)
        ad_stock_value=(1/(1+np.exp(-lr_rate*t)))+ad_stock_value*decay
        ad_stock_value2=1- np.exp(-lr_rate*t)+ad_stock_value2*decay
        ad_stock_list.append(ad_stock_value)
        ad_stock_list2.append(ad_stock_value2)
        data.loc[index,'ad_stock_s_'+str(var)] =ad_stock_value
        data.loc[index,'ad_stock_nad_'+str(var)] =ad_stock_value2
        
#function to make the dict with the channel_values 
def str_fin_ad_log(string):
    if bool(re.search('ad_stock_nad_(\w+)_log',string)):
        return re.findall('ad_stock_nad_(\w+)_log',string)[0]
    elif bool(re.search('(\w+)_log',string)):
        return re.findall('(\w+)_log',string)[0]

def str_fin_ad(string):
    if bool(re.search('ad_stock_nad_(\w+)',string)):
        return re.findall('ad_stock_nad_(\w+)',string)[0]
    elif bool(re.search('(\w+)',string)):
        return re.findall('(\w+)',string)[0]
    
#create a for loop to get the dictionary for the variables and then transfom them into adstock and log 
def new_map_dict(corr):
    map_dict = {}
    for i in range(len(corr.columns)-1):
        string = list(corr.columns)[i]
        map_dict[str_fin_ad(string)]=string
        
    return {y:x for x,y in map_dict.items()}

#CREATE A FUCNTION BY TAKING THE VALUES OF THE DICT RETURN BY THE CORRELATION AND ADD THOSE PURE VALUES, 
#LATER TRNASFORM THEM AND REPEAT UNTIL WE FIND NO CORRELATION

def corr_find(data_promo1,channel_list,cor_coef_ad,cor_coef_else):
    non_promo_col=np.array(['Price','PCV'])
    chann=np.array(channel_list)
    #driver = [str("ad_stock_nad_")+i for i in chann.astype('object')+ "_log"]+[j for j in non_promo_col.astype('object') + "_log"]+ list(range(4))
    driver = [str("ad_stock_nad_")+i for i in chann.astype('object')]+[j for j in non_promo_col.astype('object')] 

    #lis1=driver+['Sales_log']
    lis1=driver+['Sales']
    corr1= data_promo1[lis1].corr()
    corr_find.corr = corr1.copy()
    cor1_dict={}
    #creating a dictionary mapping elements with correlation 
    for i in range(len(corr1)-1):
        if i<len(chann):
            for j in range(len(corr1)-1):        
                if ((corr1[lis1[i]].iloc[j])>cor_coef_ad and i>j):
                    #print(f'For NAD ad stock ','Correlation is >{cor_coef_ad} between',lis1[i],'and',corr1[lis1[i]].index[j])
                    cor1_dict[f'{lis1[i]}']=f'{corr1[lis1[i]].index[j]}'
        else:
            for j in range(len(corr1)-1):        
                if ((corr1[lis1[i]].iloc[j])>cor_coef_else and i>j):
                    #print(f'For NAD ad stock ','Correlation is >{cor_coef_ad} between',lis1[i],'and',corr1[lis1[i]].index[j])
                    cor1_dict[f'{lis1[i]}']=f'{corr1[lis1[i]].index[j]}'
                    raise ValueError("Correlation found! Model discarded")
    return cor1_dict

#creating a function for merging the colms in the correlated values 
#new map dict  
#CHANNEL_LIST IS SUBJECTED TO CHANGE 
#CHANGE lr to lr_list and same for decay

def corr_merge_all(added_col1,added_col2,data_promo1,hier,spc_hier,channel_list,spc_hier_list,mapped,cor1_dict,cor_coef_ad,cor_coef_else,lr,decay):
    
    if cor1_dict: 
        #print(cor1_dict)
        item_1= mapped[list(cor1_dict.keys())[0]]
        item_2 = mapped[list(cor1_dict.values())[0]]
        added_col1.append(item_1)
        added_col2.append(item_2)
        data_promo1[item_1]=data_promo1[item_1]+data_promo1[item_2]
        #data_promo1.drop(columns=[list(cor1_dict.keys())[0],list(cor1_dict.values())[0],f'ad_stock_s_{item_2}_log',f'ad_stock_s_{item_1}_log'],inplace=True)
        data_promo1.drop(columns=[list(cor1_dict.keys())[0],list(cor1_dict.values())[0],f'ad_stock_s_{item_2}',f'ad_stock_s_{item_1}'],inplace=True)

        #print(item_1)  data,data_promo,var,hier,spc_hier,zone_reg_col,lr_list,decay_list 
        for j in spc_hier_list: 
            ad_stock_s_curve_u_all(data_promo1,item_1,hier,j,lr,decay)
# =============================================================================
#             log_var_crores(data_promo1,str('ad_stock_nad_')+item_1)
#             log_var_crores(data_promo1,str('ad_stock_s_')+item_1)
# =============================================================================
        cor1_dict.pop(list(cor1_dict.keys())[0]) 
        channel_list = list(set(channel_list)- set([item_2]))
        print(item_2)
        print(channel_list)
        cor1_dict = corr_find(data_promo1,channel_list,cor_coef_ad,cor_coef_else)
        print('CORRRELATION DICT',cor1_dict)
        return corr_merge_all(added_col1,added_col2,data_promo1,hier,spc_hier,channel_list,spc_hier_list,mapped,cor1_dict,cor_coef_ad,cor_coef_else,lr,decay)
    else : 
        return data_promo1,channel_list,added_col1,added_col2
    
#For making similar changes in the user input as we did in correlation df 
def post_col_chg(user_input,added_col1,added_col2):
    if added_col1:
        #add dict col
        item_1= added_col1.popleft()
        item_2 = added_col2.popleft()
        user_input[item_1]=user_input[item_1]+user_input[item_2]
        #delete item_2(value of that dict)
        user_input.drop(columns=[item_2])
        return post_col_chg(user_input,added_col1,added_col2)
    else:
        return user_input
        

