import pandas as pd
import numpy as np
import json
import re
from mmm_post_pro import *
#======================POST_PROCESSSING============================w
#Now some values can contain 0 values for log function hence finding index of them and replacing them with the second
#min value
def col_drop(hier,hier_list):
    col_2_drop=[]
    j=0
    for i in hier_list:
        j+=1
        if (i==hier):
            col_2_drop=hier_list[j:]
    return col_2_drop

#get those two dictionary make a function with var as a variable to apply for loop over this function and 
#output should be the roi value and make a dictionary with roi values and integrate it with the final output.
#====================================================
#SAME ROI FOR THE COLUMNS MULTIPLIED (MAYBE) 
#====================================================

def roi_var_type(last,user_input,vol_dist_sam,hier,spc_hier,var):
    last_var_inp = last[f'ad_stock_nad_{var}'][last.index[0]]
    last[f'ad_stock_nad_{var}'][last.index[0]]= user_input[f'ad_stock_nad_{var}']  # the change in a single var keeping rezt as constant 
    last_sales= last['Sales'].sum()*(last['Price'].sum() ) 
    roi=(last_sales*vol_dist_sam[var]-last_var_inp.sum())/100/(last_var_inp.sum()) #DIVIDED BY 100 BECAUSE WE HAD DATA IN CRORES AND THIS IS PERCENT
    #SO  WE ARE LEFT WITH 5 ZEROES NOW THE PRICE IS ACTUALLY IN 000 SO THREE MORE DOWN THERE- FINALLY WE ARE LEFT WITH 2 ZEROES 
    return roi

def rounding_off(data):
    data={x:round(y,2) for x,y in data.items() }
    return data
def rep_zero(data,var):
    zeroes=data.index[data[var]==0].tolist()
    value=data[var].sort_values().tolist()[len(zeroes)]
    data.loc[zeroes,var]=value/100
    
def log_var_crores(data,var):
    data[var+str('_log')]=np.log(data[var])
def log_var(data,var):
    if data[var].min()==0:
        #function for that value take that index and put second min value 
        rep_zero(data,var)
        data[var+str('_log')]=np.log(data[var])
    else:
        data[var+str('_log')]=np.log(data[var])

def zeroes_finder(data):
    index=data.min().index
    values=data.min().values
    for i in range(len(index)):
        if ((index[i]=='Zone') or (index[i]=='Region')):
            pass
        if (values[i]==0):
            rep_zero(data,index[i])
          
#WITH GIVEN BUDGET, WE APPX PARAMETERS FOR MAX SALE BY SCALING DOWN RECOMMENDED VALUES IN SPENDS              
def pred_bugdet(budget,rec_values):
    rec_sum=0 
    
    rec_values.pop('PCV') 
    rec_values.pop('Price')
    for values in list(rec_values.values()):
        rec_sum+=values
    for key in list(rec_values.keys()):
        value = rec_values[key]
        value = value*budget/rec_sum
        rec_values[key]=value
    return rec_values
            
#getting coeficients for each brand     #data_promo1
#creating a dataframe for the coef.    
def coeff123(data_promo1,hier,spc_hier,Model):
    brands=data_promo1[hier].unique()
    ind=np.where(brands==spc_hier)
    a=Model.random_effects[brands[ind][0]].iloc[1:]+Model.fe_params.iloc[1:]
    a[hier]=brands[ind][0]
    a['Intercept']=Model.fe_params[0]
    a=a.to_frame().transpose()
    return a    

def p_chg_sales_log(test,last):
    change=(np.exp(test)-np.exp(last))*100/np.exp(last)
    p_changes={'per_sales':change,'appx_sales':np.exp(test)}
    #json_p_changes=json.dumps(p_changes)
    return p_changes

def p_chg_sales(test,last):
    change=(test-last)*100/last
    p_changes={'per_sales':change,'appx_sales':test}
    #json_p_changes=json.dumps(p_changes)
    return p_changes

def p_chg_sales_recom_log(test,last):
    change=(np.exp(test)-np.exp(last))*100/np.exp(last)
    p_changes={'recommended_per_sales':change,'recommended_appx_sales':np.exp(test)}
    return p_changes

def p_chg_sales_recom(test,last):
    change=(test-last)*100/last
    p_changes={'recommended_per_sales':change,'recommended_appx_sales':test}
    return p_changes 

#variable for transformation is var lr rate is 0.1 decay is 0.69315 and defualt value for ar_coeff is 0.3
        
def ad_stock_s_curve_user(data,prev_data,var,lr_list,decay_list):
    ad_stock_list=[]
    ad_stock_list2=[]
#
    lr_rate=float(lr_list[var])
    decay=float(decay_list[var])
    
    ad_stock_value=prev_data[var].sum()
    ad_stock_value2=prev_data[var].sum()
    for index,row in data.iterrows():
        t=row[str(var)]
        ad_stock_value=(1/(1+np.exp(-lr_rate*t)))+ad_stock_value*decay
        ad_stock_value2=1- np.exp(-lr_rate*t)+ad_stock_value2*decay
        ad_stock_list.append(ad_stock_value)
        ad_stock_list2.append(ad_stock_value2) 
        
    data['ad_stock_s_'+str(var)]=ad_stock_list
    data['ad_stock_nad_'+str(var)]=ad_stock_list2
    
def user_inp_2_test(user_input,last_val,channel_list,lr,decay,driver):
    df_u=pd.DataFrame.from_dict(user_input,orient='index')
    df_u=df_u.T
    user_inp_2_test.user_val=df_u
    for i in range(len(channel_list)):
        ad_stock_s_curve_user(df_u,last_val,channel_list[i],lr,decay)
# =============================================================================
#             log_var_crores(df_u,str('ad_stock_nad_')+channel_list[i])
#             log_var_crores(df_u,str('ad_stock_s_')+channel_list[i])
# =============================================================================
# =============================================================================
#     log_var(df_u,'PCV')
#     log_var(df_u,'Price')
# =============================================================================
    #keeping the desired variables
    df_u=df_u[driver]
    
    return df_u 

#function for adjusting the varibles those were highly correlated in the data
def user_cor_adj(user_inp,added_col1, added_col2):
    for i in range(len(added_col1)):
        user_inp[added_col1[i]] = user_inp[added_col1[i]]+user_inp[added_col2[i]]
        user_inp.pop(added_col2[i])
    return user_inp
   
def vol_combo(added_col1,added_col2,chann_list):
    local_var  = {} 
    left = list(set(chann_list)-set(added_col1+added_col2))
    for i in left:
        local_var[i]=str(i) #FOR ELEMENTS THOSE HAD CORRELATION LESS THAN 0.8 THEY ARE USED AS IT AS
    for i in range(len(added_col1)):
        if added_col1[i] in local_var:
            if added_col2[i] in local_var:
                local_var[added_col1[i]] = str(local_var[added_col1[i]]) + str('*') + str(local_var[added_col2[i]])
                local_var.pop(added_col2[i])
            else :
                local_var[added_col1[i]] = str(local_var[added_col1[i]]) + str('*') + str(added_col2[i])
        elif added_col2[i] in local_var:
            local_var[added_col1[i]] = str(added_col1[i])+str('*')+ str(local_var[added_col2[i]])
        else :
            local_var[added_col1[i]] = str(added_col1[i])+str('*')+ str(added_col2[i])
    return local_var
#TO ADDED SEASONS IN OUR USER'S INPUTS 
# =============================================================================
# def create_cson(data_promo1,hier,spc_hier,date_promo,target_inp):
#     #check the lasat season of the data_promo and if the last 3 values of that season are same 
#     # then put next season
#     last_sea = data_promo1[data_promo1[hier]==spc_hier].tail(1)[date_promo].values[0]
#     #val= data_promo1[data_promo1[hier]==spc_hier][last_sea].tail(3).sum().astype('int') #CHANGE THE TAIL TO 3 FOR 4 SEASONS YW 
#     sea = re.findall('\d',last_sea[0]) #VALUE OF LAST SEASON ex. 0 or 1
#     for i in range(2):
#         target_inp[f'season_{i}']=0 #CHANGE ALL THE SEASONS TO 0 AT FIRST THEN MAKE THE NEXT SEASON 1
#         
#     new_cson = (int(sea[0])+1)%2 #TO GET NEXT SEASON 
#     target_inp[f'season_{new_cson}']=1
#     
#     # IF WE HAVE MORE THAN 2 SEASONS USE THIS CODE FOR GETTING NEXT SEASON WITHOUT ANY HASSLE YW
# # =============================================================================
# #     for i in range(4): #CHANGE THE RANGE TO 4 FOR 4S 
# #         target_inp[f'season_{i}']=0
# #     if val.values[0]==3: 
# #         new_cson = (int(sea[0])+1)%4 #TO GET NEXT SEASON 
# #         target_inp[f'season_{new_cson}']=1
# #     else : 
# #         target_inp[last_sea[0]]=1
# # =============================================================================
#     return target_inp
# =============================================================================

def user_input_part2(data_promo1,hier,spc_hier,added_col1,added_col2,channel_list,chann_list,driver1,mdf1,lr,decay,config_All_india_promo,data_json,mod):
    
    date_promo=[] 
    for i in range(int(config_All_india_promo[config_All_india_promo['derived_dimension']=='date_var']['num_rav_var'].values[0])):
        date_promo.append(config_All_india_promo[config_All_india_promo['derived_dimension']=='date_var']['rv'+str(i+1)].values[0])
    
    last=data_promo1[data_promo1[hier]==spc_hier].tail(1)
    last =user_cor_adj(last,added_col1,added_col2)
    rem_col=list(set(list(last.columns))-set([hier]+date_promo +['Sales', 'PCV', 'Price']+chann_list))#+ [str('season_')+str(i) for i in range(2)])) #CHANGE THE VALUE OF 2 TO 4 IN CASE OF 4 SEASONS
    
    last_val=last.drop(columns=rem_col)
    last_val_dict= last_val.reindex().to_dict('records')
    user_inp={}
    user_inp['PCV']=float(data_json['PCV'])
    user_inp['Price']=float(data_json['Price'])
    
    for i in range(len(channel_list)):
        user_inp[channel_list[i]]=float(data_json[channel_list[i]])
    #keeping specified cols 
    #create_cson(data_promo1,hier,spc_hier,date_promo,user_inp)
    
    user_inp=user_cor_adj(user_inp, added_col1,added_col2)
    #user_inp_copy= user_inp.copy() 
    
    test=user_inp_2_test(user_inp,last_val,chann_list,lr,decay,driver1) 
    coeff_1=coeff123(data_promo1,hier,spc_hier,mdf1)
    coeff1=coeff_1.copy() 
    coeff1.drop(columns=[hier],inplace=True)
    coeff1.reset_index(inplace=True,drop=True)
    test['Intercept']=1 
    #test=test.append([test]*(len(data_promo1[hier].unique())-1),ignore_index=True)
    test=test[coeff1.columns]
    #combining both list 
    result=dict(zip((coeff_1[hier]),(coeff1*test).sum(axis=1)))
    #last.Sales.values[0]=last.Sales.values[0].to_dict('index')
    #print('Last month sales: ',last.Sales.values[0])
    
    #p_sales=p_chg_sales(result.get(spc_hier),last['Sales'+str('_log')].sum())
    p_sales=p_chg_sales(result.get(spc_hier),last['Sales'].sum())
    #creating a json output
    #creating a dict for best possible value 
    
    #this dict contains all the imoprtant variables like channel_list and PCV and Price with their corresponding names of variables like ad_stock and log values
    one_one_dict={} 
    for i in range(len(chann_list)):
        one_one_dict[chann_list[i]]=coeff_1.columns[i]
        one_one_dict['Price']='Price'
        one_one_dict['PCV']='PCV' 
# =============================================================================
#     one_one_dict['Price']='Price_log'
#     one_one_dict['PCV']='PCV_log'
# =============================================================================
    one_one_dict={y:x for x,y in one_one_dict.items()}
    keep_col=list(set(data_promo1.columns)-set(rem_col))  
    
    last=data_promo1[keep_col].tail(len((data_promo1[hier]).unique()))
    last =user_cor_adj(last,added_col1,added_col2)
    last=last[list(one_one_dict.values())]
    
    coeff_1_copy=coeff_1[list(one_one_dict.keys())]
    #FINDING THE BEST VALUES
    best_values={}
    for key in one_one_dict:
        if coeff_1_copy[key][0]>=0:
            best_values[one_one_dict[key]]=last[one_one_dict[key]].max()
        if coeff_1_copy[key][0]<0:
            best_values[one_one_dict[key]]=last[one_one_dict[key]].min()
    
    #SALES of recommended values
    #THIS CHANGES IT TO ADSTOCK AND LOG TRANSFORMATION 
    test1=user_inp_2_test(best_values,last_val,chann_list,lr,decay,driver1)

    #Create New season for the user based on the last few seasons
    #create_cson(data_promo1,hier,spc_hier,date_promo,test1)

    test1['Intercept']=1 
    #test=test.append([test]*(len(data_promo1[hier].unique())-1),ignore_index=True)
    test1=test1[coeff1.columns]      
    #test1.drop(columns=[hier])
    #combining both list with names and values
    result1=dict(zip((coeff_1[hier]),(coeff1*test1).sum(axis=1)))
    #p_sales_recom=p_chg_sales_recom(result1.get(spc_hier),last['Sales'+str('_log')].sum())
    p_sales_recom=p_chg_sales_recom(result1.get(spc_hier),last_val['Sales'].sum())
    #budget = float(data_json['Budget'])
    #budget_params = pred_bugdet(budget,best_values.copy()) 
    rounding_off(p_sales) 
    rounding_off(best_values)
    rounding_off(p_sales_recom)
    print(rounding_off(best_values))
    
    #LAST VALUE WITH ADSTOCK AND SALES VAR
    last_val_roi = data_promo1[[f'ad_stock_nad_{channel}' for channel in chann_list]+['Sales','PCV','Price']+[hier]]#+[f'season_{i}' for i in range(2)]] #CHANGE THE VALUE OF 2 to 4 IN CASE OF 4 SEASONS 
    last_val_roi = last_val_roi[last_val_roi[hier]==spc_hier].tail(1)
    vol_local= vol_combo(added_col1,added_col2,chann_list)
    #function for roi values with for loop in new channel_list 
    roi_dict_2={}
    for channel in chann_list: 
        roi_dict_2[channel] = roi_var_type(last_val_roi.copy(),test,user_input.vol_dist_sam,hier,spc_hier,channel) 
    for i in chann_list:
        if (vol_local):
            roi_dict_2[vol_local[i]]=roi_dict_2.pop(i)
    for i in chann_list:
        if (vol_local):
            best_values[vol_local[i]]=best_values.pop(i)
    output2={'PERCENTAGE CHANGES IN SALES':rounding_off(p_sales),"RECOMMENDATIONS":rounding_off(best_values),"RECOMMENDED SALES AND PERCENTAGE CHANGES":rounding_off(p_sales_recom), "ROI OF SPENDS":rounding_off(roi_dict_2)}
    return output2 
    
    


