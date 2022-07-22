import pandas as pd
import os
from pybliometrics.scopus import AuthorRetrieval

home = os.environ['HOME']
home
df = pd.read_excel(home+'/data/IMR/IMR_Researchers/お知らせサービステンプレート20220329.xlsx')
df.columns
for i,j in zip(df['Scopus著者ID'],df['漢字氏名']):
    print('=================')
    print(j)
    print('-----------------')
    if len(str(i)) > 4:
        print(str(int(i)))
        au = AuthorRetrieval(int(i))
        au.affiliation_current
        print(au)
    else:
        print('Scopus著者ID未設定')
