import numpy as np
from math import sqrt
import statsmodels.formula.api as smf
from sklearn.metrics import r2_score,mean_squared_error
#===========================MODEL=============================
def Model(data_promo1,hier,chann_list):
    non_promo_col=np.array(['Price','PCV'])
    chann=np.array(chann_list)
# =============================================================================
#     #Model 1 with nad curve and log log model 
#     Model.driver1 = [str("ad_stock_nad_")+i for i in chann.astype('object')+ "_log"]+[j for j in non_promo_col.astype('object') + "_log"]
#     eqn1=' ~ '+' + '.join([i for i in Model.driver1])
#     md1=smf.mixedlm('Sales_log' + eqn1,data = data_promo1,groups=data_promo1[hier],re_formula=eqn1)
#     Model.mdf1=md1.fit(method='lbfgs') 
# =============================================================================
    
    Model.driver1 = [str("ad_stock_nad_")+i for i in chann.astype('object')]+[j for j in non_promo_col.astype('object') ]
    eqn1=' ~ '+' + '.join([i for i in Model.driver1])
    md1=smf.mixedlm('Sales' + eqn1,data = data_promo1,groups=data_promo1[hier],re_formula=eqn1)
    Model.mdf1=md1.fit(method='lbfgs')
    #mdf= Model.mdf1
    print(Model.mdf1.summary())

    #MODEL WITH SEASONALITY 
    try :
        Model.driver1_sea = [str("ad_stock_nad_")+i for i in chann.astype('object')]+[j for j in non_promo_col.astype('object')]+[str('season_')+str(i) for i in range(2)] #CHANGE THE VALUE OF 2 TO 4 IN CASE OF 4 SEASONS 
        eqn1_sea=' ~ '+' + '.join([i for i in Model.driver1_sea])
        md1_sea=smf.mixedlm('Sales' + eqn1_sea,data = data_promo1,groups=data_promo1[hier],re_formula=eqn1_sea)
        #PENALISE THE MODEL IF THE MODEL GIVES SINGULAR MATRIX
    
        #md1_sea.fit_regularized(alpha=1) 
        Model.mdf1_sea=md1_sea.fit()
        print(Model.mdf1_sea.summary())
    except Exception as e:
        raise Exception("Model with seasons failed to get trained due to "+str(e))
    #mdf1_sea = Model.mdf1_sea 
    
# =============================================================================
#     #Model 2 with S curve 
#     Model.driver2 = [str("ad_stock_s_")+i for i in chann.astype('object')+ "_log"]+[j for j in non_promo_col.astype('object') + "_log"]
#     eqn2=' ~ '+' + '.join([i for i in Model.driver2])
#     md2=smf.mixedlm('Sales_log' + eqn2,data = data_promo1,groups=data_promo1[hier],re_formula=eqn2)
#     Model.mdf2=md2.fit(method='cg')
# =============================================================================
    
    Model.acc1 = r2_score(data_promo1['Sales'],Model.mdf1.fittedvalues)
    Model.acc2 = r2_score(data_promo1['Sales'],Model.mdf1_sea.fittedvalues)
    r2_2= r2_score(data_promo1['Sales'],Model.mdf1_sea.fittedvalues)
    adj_r = 1-((1-r2_2)*(len(data_promo1)-1)/(len(data_promo1)-1-8))
# =============================================================================
#     IN CASE OF CHOOSING A MODEL WITH BEST ACCURACY
#     acc1 = r2_score(data_promo1['Sales'],Model.mdf1.fittedvalues)
#     acc1 = r2_score(data_promo1['Sales_log'],Model.mdf1_sea.fittedvalues)
#     #if time (choose the best model)
#     
#     if acc1>acc2:
#         Model.mdf=Model.mdf1
#         Model.driver=Model.driver1
#     else:
#         Model.mdf=Model.mdf2
#         Model.driver=Model.driver2
# =============================================================================

#==================================================================

