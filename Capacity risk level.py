# The following script uses the full database of power units containing all hazard levels and a modifiable vulnerability matrix
# in order to calculate a capacity risk measure for a selected country

import pandas as pd
import numpy as np

database = pd.read_csv('Full Database.csv')  # Full database containing all units and all hazard levels for each unit
vuln_matrix = pd.read_csv('Vulnerability Matrix.csv',index_col=0)  # Vulnerability matrix
risk_level = {'HIG':3,'MED':2,'LOW':1,'VLO':0,'-':0}  # Risk Level attribution

hazards = ['EQ', 'LS', 'FL', 'TS', 'DG', 'CY', 'VA']  # Coastal Flood does not appear as we will merge it with the Flood risk

print(vuln_matrix)  # Always useful to have and see

def get_capacity(country):
    
    # The following calculates for a specific country the exposed capacity for each hazard
    
    results = {}
    df = pd.DataFrame()
    
    country_base = database.ix[database['COUNTRY']==country]
    country_base = country_base.replace(risk_level)  # We replace the level HIG MED LOW and VLO by the values we chose
    country_base['FL'] = np.maximum(country_base['FL'],country_base['CF'])  # We get rid of Coastal Flood by taking the highest risk between coastal flood and usual flood
    tot_capacity = sum(country_base['MW'])
    
    for i in hazards:
        
        for j in country_base.index:
            country_base.loc[j,i+'_BIS'] = country_base.loc[j,i]*vuln_matrix.loc[country_base.loc[j,'WB_Fuel'],i]
        
        results[i] = sum(np.multiply(country_base['MW'],country_base[i+'_BIS']))/(vuln_matrix.values.max()*max(risk_level.values()))
        df[i] = [results[i],results[i]/tot_capacity]
    
    df['TOTAL'] = [tot_capacity,1]
    df.index = ['Exposed capacity in MW','Exposed part of capacity']
    
    return df