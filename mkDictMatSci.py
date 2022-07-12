# 機関名辞書作成用
# 作成：2022年7月13日
# 目的：著者所属機関データから、著者名と住所部分を削除して、機関名のみのデータセットを作成
# 　　　機関名の揺れを考慮して、データを抽出することができるようにする。
# 作成者：湯本道明
from researchcapability import WoS
import pandas as pd
import os, pathlib, re
import datetime

dt_now = datetime.date.today().strftime('%Y%m%d')

# ホームディレクトリのpathを設定
home = os.environ["HOME"]

#######################
# 書誌情報データの読み込み
#######################
wos = WoS()

# wosのデータディレクトリのpathを設定
data = "/googleMyDrive/data/wos/JPMatSci20220708/"
df_wos = wos.mkDataFrame(home + data)
df_wos = df_wos.astype({'Addresses': 'str'})

df_wos.pivot_table(
    values="UT (Unique WOS ID)",
    columns=["Document Type"],
    index=["Publication Year"],
    aggfunc=len,
)

# 研究機関を分析する
## [著者名] 所属機関名の形に整理する
names0 = []
for address in df_wos['Addresses']:
    ##address = str(address)
    if "; [" in address:
        address = address.replace("; [","; [[")
        pass
        elms = address.split("; [")
        for j in elms:
            names0.append(j)
    elif "nan" in address:
        pass
    else:
        names0.append(address)
names0 = sorted(set(names0))
len(names0)

kikanmeiJusyo0 = []
for i in names0:
    if "] " in i:
        pass
        elms = i.split('] ')
        if len(elms) > 2:
            print(elms)
        else:
            #print(elms[1])
            kikanmeiJusyo0.append(elms[1])
        #print(i)
    else:
        pass
        #print(i)
        kikanmeiJusyo0.append(i)

kikanmeiJusyo0 = sorted(set(kikanmeiJusyo0))

kikanmeiJusyo = []
for i in kikanmeiJusyo0:
    if '; ' in i:
        pass
        elms = i.split('; ')
        for j in elms:
            kikanmeiJusyo.append(j)
    else:
        kikanmeiJusyo.append(i)
kikanmeiJusyo = sorted(set(kikanmeiJusyo))


# すでに判っている住所部分データの読み込み
with open(home+'/googleMyDrive/data/MatSci/jusyo_20220711.txt','r') as f:
    jusyo = f.readlines()


def cleanchimei(text,jlist):
    '''
    住所部分のデータを削除する関数
    '''
    jlist = jlist
    text = re.sub(', Japan$', ',', text)
    for i in jlist:
        i = re.sub('\n',',',i)
        i = ',\s*'+i
        #print(i)
        #i = ',\s*'+i
        text = re.sub(i+'$',',',text)
    return text


for n in range(len(kikanmeiJusyo)):
    if n == 0:
        japan = []
        overseas = []
    i = kikanmeiJusyo[n]
    #print(i)
    if ', Japan' in i:
        #print(i)
        i = cleanchimei(i,jusyo)
        i = cleanchimei(i,jusyo)
        i = cleanchimei(i,jusyo)
        i = cleanchimei(i,jusyo)
        japan.append(i)
    else:
        overseas.append(i)
    if n>100 and n%500==1:
        print(n)
print('処理終了')

# 国内機関名辞書の出力
japan = sorted(set(japan))
with open(home+'/googleMyDrive/data/MatSci/kikanmeiKokunai_'+dt_now+'.txt','w') as f:
    for i in japan:
        i=i+'\n'
        f.write(i)
f.close()

# 海外機関データの出力
len(overseas)
oversear = sorted(set(overseas))
with open(home+'/googleMyDrive/data/MatSci/kikanmeiKaigai_'+dt_now+'.txt','w') as f:
    for i in overseas:
        i=i+'\n'
        f.write(i)
f.close()

# Addressが空白となっているもの
df_chk = df_wos[df_wos['Addresses'].isin(['nan'])]
df_chk.to_exel(home+'/googleMyDrive/data/MatSci/chkAddNan'+dt_now+'.xlsx')
