import pandas as pd
import numpy as np

database = pd.read_csv('')
vuln_matrix = pd.read_csv('')
risk_level = {'HIG':3,'MED':2,'LOW':1,'VLO':0,'-':0}

hazards = ['EQ', 'LS', 'FL', 'TS', 'DG', 'CY', 'VA']

print(vuln_matrix)

def get_capacity(country):
    
    results = {}
    df = pd.DataFrame()
    
    country_base = database.ix[database['COUNTRY']==country]
    country_base[hazards].replace(risk_level)
    country_base['FL'] = max(country_base['FL'],country_base['CF'])
    tot_capacity = sum(country_base['MW'])
    
    for i in hazards:
        country_base[i+'_BIS'] = country_base[i]*vuln_matrix.loc[i,'fuel']
        results[i] = sum(np.multiply(country_base['MW'],country_base[i+'_BIS']))/(max(vuln_matrix)*max(risk_level.values))
        df[i] = [results[i],results[i]/tot_capacity]
    
    df['TOTAL'] = [tot_capacity,1]
    
    df.to_csv('_'+country+'.csv')
        
    
    
    
        
        
