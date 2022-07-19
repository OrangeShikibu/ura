from researchcapability import WoS
from researchcapability import TU
import pandas as pd
import os, pathlib, re
import datetime

# ホームディレクトリのpathを設定
home = os.environ["HOME"]

#######################
# 書誌情報データの読み込み
#######################
wos = WoS()
tu = TU()

def mkKensakuShiki(l):
    rlist = []
    for i in l:
        # 正規表現に用いる記号を処理し、
        # ', 'を先頭に付ける。
        i = i.replace("(", "\(")
        i = i.replace(")", "\)")
        i = i.replace("-", "\-")
        i = i.replace(".", "\.")
        i1 = "," + i
        i2 = "]" + i
        rlist.append(i1)
        rlist.append(i2)
    rlist=sorted(set(rlist))
    return "|".join(rlist)


# wosのデータディレクトリのpathを設定
data = "/googleMyDrive/data/wos/JPMatSci20220708/"
df_wos = wos.mkDataFrame(home + data)
df_wos["doi"] = df_wos["DOI"].str.lower()
df_wos = df_wos.astype({'Addresses': 'str'})
df_wos['add'] = df_wos["Addresses"].str.lower()
df_wos['add'] = df_wos['add'].str.replace(' ','')

df_p = df_wos.pivot_table(
    values="UT (Unique WOS ID)",
    columns=["Document Type"],
    index=["Publication Year"],
    aggfunc=len,
)
df_p.to_excel(home + "/result/JPMatSci_JP_pivot_20220708.xlsx")

##########################
# 部局名辞書ファイルの読み込み
##########################
# 現在の部局名辞書ファイル
dict = "/googleMyDrive/data/dict/current/dict_TU_Orgs_Name_20220719.xlsx"
df_dics = pd.read_excel(home + dict)
df_dics['orgsnamee'] = df_dics['OrgsNameE'].str.lower()
df_dics['orgsnamee'] = df_dics['orgsnamee'].str.replace(' ','')

# 部局を確認できている部局名辞書のデータフレームを作成する
abbrevia = []
for i in df_dics["Abbrevia"]:
    abbrevia.append(i)

abbrevia = set(abbrevia)

## 部局の確認を終えていないものなどを削除
#abbrevia.remove("unknown")
abbrevia.remove("notTU")
df_dics_tu = df_dics[df_dics["Abbrevia"].isin(abbrevia)]

tulist = []
for i in df_dics_tu["orgsnamee"]:
    tulist.append(i)
tulist = sorted(set(tulist))
tulist.append('tohokuuniv,')
tunames = mkKensakuShiki(tulist)

df_wos_tu = df_wos[df_wos['add'].str.contains(tunames)]
df_wos_tu.pivot_table(
    values="UT (Unique WOS ID)",
    columns=["Document Type"],
    index=["Publication Year"],
    aggfunc=len,
)

########################
# 機関名辞書で検索してみる
########################
df_dics2 = pd.read_excel(home + "/googleMyDrive/data/MatSci/kikanmeiKokunai0712.xlsx")
df_dics2['orgsnamee'] = df_dics2['OrgsNameE'].str.lower()
df_dics2['orgsnamee'] = df_dics2['orgsnamee'].str.replace(' ','')
df_dics2_tu = df_dics2[df_dics2["機関名"].isin(['東北大学'])]

tulist2 = []
tulist3 = []
for i in df_dics2_tu["orgsnamee"]:
    if re.search('^tohokuuniv,$',i):
        tulist2.append(i)
    else:
        tulist2.append(i)
        tulist3.append(i)
tulist2=sorted(set(tulist2))
tulist3=sorted(set(tulist3))

# 'Tohoku Univ,'を含む
tunames2=mkKensakuShiki(tulist2)
df_wos_tu2 = df_wos[df_wos['add'].str.contains(tunames2)]
df_p = df_wos_tu2.pivot_table(
    values="UT (Unique WOS ID)",
    columns=["Document Type"],
    index=["Publication Year"],
    aggfunc=len,
)
df_p.to_excel(home + "/result/JPMatSci_TU_pivot_20220708.xlsx")
# 'Tohoku Univ,'を含まない、部局名のみ
tunames3=mkKensakuShiki(tulist3)
df_wos_tu3 = df_wos[df_wos['add'].str.contains(tunames3)]
# 部局名が判明していない論文のデータフレーム
df_wos_tu4 = df_wos_tu2[~df_wos_tu2["UT (Unique WOS ID)"].isin(df_wos_tu3["UT (Unique WOS ID)"])]


###########################
# IMR研究者データの読み込み
###########################
# 金研研究者のデータファイル
imrresearchers = "/googleMyDrive/data/IMR/IMR_Researchers/IMR_researchers_20220415.xlsx"
df_imr_researcher = pd.read_excel(home + imrresearchers)
# 金研研究者のResearcherID
imr_researcherIDs = df_imr_researcher["ResearcherID"].values.tolist()
# 金研研究者の名前
imr_name = df_imr_researcher["English Name"].values.tolist()


##############################
# 部局分析の準備
##############################
bukyokumei = ["IMR"]
df_dics_bukyoku = df_dics[df_dics["Abbrevia"].isin(bukyokumei)]
#df_dics_bukyoku2 = df_dics2[df_dics2["Abbrevia"].isin(bukyokumei)]

##############################
# 部局WoSデータセットの作成
## 部局名文字列作成
bukyokulist = []
for i in df_dics_bukyoku["orgsnamee"]:
    bukyokulist.append(i)
len(bukyokulist)
bukyokulist = sorted(set(bukyokulist))
len(bukyokulist)

# 部局名辞書の表記を文字列化
bukyokunames = mkKensakuShiki(bukyokulist)

# 部局名辞書により抽出したscopusデータセット
# 列「著者＋所属機関」に部局名表記を含むものを抽出
df_wos_bukyoku = df_wos[df_wos["add"].str.contains(bukyokunames, na=False)]
# 部局名辞書で抽出された論文データフレーム（念のため重複を削除しておく）
df_wos_bukyoku = df_wos_bukyoku.drop_duplicates()

# なお、金研を対象とするWoSの文献データフレームには、所属機関名が金研であっても、著者が金研に所属していない研究者ではない場合がありました。その文献書誌情報を見ると所属機関名の表記の区切り方が間違えていることを確認しています。そのような文献書誌情報を金研の文献データフレームから削除する必要があることから以下の操作を行っています。
# 金研ではない所属機関情報のものを除く
if bukyokumei == "IMR":
    notIMR = [
        "Tohoku Univ, Inst Mat Res, Inst Fluid Sci & Adv, Sendai, Miyagi 9808577, Japan"
    ]
    df_wos_bukyoku = df_wos_bukyoku[
        ~df_wos_bukyoku["Addresses"].str.contains(notIMR[0])
    ]

# 金研以外の論文
#df_wos_other = df_wos[~df_wos['UT (Unique WOS ID)'].isin(df_wos_bukyoku['UT (Unique WOS ID)'])]
df_wos_other_tu = df_wos_tu2[~df_wos_tu2['UT (Unique WOS ID)'].isin(df_wos_bukyoku['UT (Unique WOS ID)'])]

# 部局不明論文データフレーム から金研論文をResearcherIDを使って抽出
imr_researcherIDs = sorted(set(imr_researcherIDs))
imr_researcherIDs.remove("unknown")
imrresearcherids = "|".join(imr_researcherIDs)
# ResearcherIDで抽出
df_wos_imr2 = df_wos_tu4[df_wos_tu4["Researcher Ids"].str.contains(imrresearcherids, na=False)]

# 著者名で抽出
# 名前の大文字・小文字調整
namelist = []

for i in imr_name:
    for j in tu.mknamelistWoS(i):
        namelist.append(j)

namelist2 = []
for i in namelist:
    i = i + "[^a-z]"
    namelist2.append(i)
researchernames = "|".join(namelist2)

df_wos_other2 = df_wos_tu4[~df_wos_tu4["UT (Unique WOS ID)"].isin(df_wos_imr2["UT (Unique WOS ID)"])]
df_wos_imr3tmp = df_wos_other2[df_wos_other2["Author Full Names"].str.contains(researchernames, na=False)]
researchernames2 = "Niinomi, Mitsuo|Sugiyama, Kazumasa|Nakajima, Kazuo|Shimada, Yusuke|Yoshikawa, Akira|Semboshi, Satoshi"
df_wos_imr3 = df_wos_imr3tmp[df_wos_imr3tmp["Author Full Names"].str.contains(researchernames2, na=False)]

df_wos_bukyoku.to_excel(home + "/result/wos_imr1.xlsx")
df_wos_imr2.to_excel(home + "/result/wos_imr2.xlsx")
df_wos_imr3.to_excel(home + "/result/wos_imr3.xlsx")
# ### WoSデータフレーム の統合
df_wos_imr = pd.concat([df_wos_bukyoku, df_wos_imr2, df_wos_imr3])
df_wos_imr = df_wos_imr.drop_duplicates()

df_p=df_wos_imr.pivot_table(
    values="UT (Unique WOS ID)",
    columns=["Document Type"],
    index=["Publication Year"],
    aggfunc=len,
)
df_p
# エクセルで出力する場合
df_wos_imr.to_excel(home + "/result/JPMatSci_imr_20220708.xlsx")
df_p.to_excel(home + "/result/JPMatSci_imr_pivot_20220708.xlsx")



# 分析
# 著者分析
rlist = []
for i in df_wos_imr["Addresses"]:
    i = str(i)
    i = re.sub('; \[','; [[',i)
    if re.search('; \[',i):
        elms = re.split('; \[',i)
        for elm in elms:
            rlist.append(elm)
    else:
        #print(i)
        rlist.append(i)
        pass
rlist = sorted(rlist)
len(rlist)
with open(home+'/result/imrPaperResearchers.txt','w') as f:
    for i in rlist:
        f.write(i+'\n')
