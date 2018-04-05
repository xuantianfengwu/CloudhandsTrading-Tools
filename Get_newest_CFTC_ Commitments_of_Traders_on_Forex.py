import pandas as pd
import requests
from bs4 import BeautifulSoup


web = 'https://www.cftc.gov/dea/options/financial_lof.htm'
req = requests.get(web)

data = req.text.split('\n-----------------------------------------------------------------------------------------------------------------------------------------------------------\n              ')
date = data[0].split('Combined Positions as of ')[-1]
data = data[1:]
cats = [['Dealer Intermidiate']*3 + ['Institutional']*3+['Leveraged Funds']*3+['Other Reportable']*3 + ['Nonreportable']*2 ,
    ['Long','Short','Spreading']*4+['Long','Short']]
multi_cols = pd.MultiIndex.from_arrays(cats,names=('category','position'))

def trans_str_to_float(x):
    x = x.replace(',','')
    if x=='.':
        return 0
    else:
        return float(x)

panel_data = {}
for d in data:
    temp = d.split('\n')
    final = [[trans_str_to_float(x) for x in temp[7].split(' ') if len(x)>0] ,[trans_str_to_float(x) for x in temp[10].split(' ') if len(x)>0]]
    final = pd.DataFrame(final,index=['this week','change from last week'])
    final.columns = multi_cols
    cat_name = temp[4].split(' -')[0]
    panel_data[cat_name] = final
    
currency_dict = {'欧元':'EURO FX',
                 '日元':'JAPANESE YEN', 
                 '英镑':'BRITISH POUND STERLING',
                 '澳元' :'AUSTRALIAN DOLLAR',
                 '加元':'CANADIAN DOLLAR',
                 '瑞士法郎':'SWISS FRANC',
                 '纽元':'NEW ZEALAND DOLLAR',
                 '墨西哥比索':'MEXICAN PESO',
                 '巴西雷亚尔':'BRAZILIAN REAL'
                 }
indexes = ['欧元','日元','英镑','澳元','加元','瑞士法郎','纽元','墨西哥比索','巴西雷亚尔']
to_df = pd.DataFrame(index = indexes,columns=['上周净持仓','本周净持仓','delta净持仓'])
for cc in currency_dict.keys():
    c = currency_dict[cc]
    temp = panel_data[c]
    total_long = 0
    total_short = 0
    total_change = 0
    for tc in ['Dealer Intermidiate','Institutional','Leveraged Funds','Other Reportable']:
        total_long += temp[tc]['Long']['this week']+temp[tc]['Spreading']['this week']
        total_short += temp[tc]['Short']['this week']+temp[tc]['Spreading']['this week']
        total_change += temp[tc]['Long']['change from last week'] - temp[tc]['Short']['change from last week']
    net_position = total_long - total_short
    to_df['上周净持仓'][cc] = net_position-total_change
    to_df['本周净持仓'][cc] = net_position
    to_df['delta净持仓'][cc] = total_change
to_df['date'] = date
to_df.to_csv('cftc_net_position.csv',encoding='utf-8-sig')
