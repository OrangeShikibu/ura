from researchcapability import WoS
from researchcapability import Scopus
from researchcapability import SciVal
from researchcapability import TU
import pandas as pd
import os, pathlib, re
import datetime

# ホームディレクトリのpathを設定
home = os.environ["HOME"]

#######################
# 書誌情報データの読み込み
#######################
# scopusとwosのデータディレクトリのpathを設定
datas = "/data/scopus/20220627/"
dataw = "/data/wos/20220627/"
datav = "/data/scival/20220630/"
svfile = "Publications_in_IMR_2021_2019_to_2021.csv"
scps = Scopus()
wos = WoS()
scival = SciVal()
tu = TU()

# scopusとwosデータの読み込み
df_scps = scps.mkDataFrame(home + datas)
df_scps["doi"] = df_scps["DOI"].str.lower()
df_wos = wos.mkDataFrame(home + dataw)
df_wos["doi"] = df_wos["DOI"].str.lower()
df_scival = scival.mkDataFrame(home + datav + svfile)
df_tudb = pd.read_excel(home + '/data/IMR/2022/論文総説解説記事.xlsx')
df_tudb["doi"] = df_tudb["DOI"].str.lower()
# 論文数確認
df_scps.pivot_table(values="EID", columns=["文献タイプ"], index=["出版年"], aggfunc=len)
df_wos.pivot_table(
    values="UT (Unique WOS ID)",
    columns=["Document Type"],
    index=["Publication Year"],
    aggfunc=len,
)

##########################
# 部局名辞書ファイルの読み込み
##########################
# 現在の部局名辞書ファイル
dict = "/data/dict/current/dict_TU_Orgs_Name_20220627.xlsx"
df_dics = pd.read_excel(home + dict)
# 部局を確認できている部局名辞書のデータフレームを作成する
abbrevia = []
for i in df_dics["Abbrevia"]:
    abbrevia.append(i)

abbrevia = set(abbrevia)
## 部局の確認を終えていないものなどを削除
abbrevia.remove("unknown")
abbrevia.remove("notTU")
df_dics_tu = df_dics[df_dics["Abbrevia"].isin(abbrevia)]
tulist = []
for i in df_dics_tu["OrgsNameE"]:
    # 正規表現に用いる記号を処理し、
    # ', 'を先頭に付ける。
    i = i.replace("(", "\(")
    i = i.replace(")", "\)")
    i = i.replace("-", "\-")
    i = i.replace(".", "\.")
    i = ", " + i
    tulist.append(i)

# 分析対象部局の組織名英語表記OrgsNameEを文字列
tunames = "|".join(tulist)

###########################
# IMR研究者データの読み込み
###########################
# 金研研究者のデータファイル
imrresearchers = "/data/IMR/IMR_Researchers/IMR_researchers_20220415.xlsx"
df_imr_researcher = pd.read_excel(home + imrresearchers)
# 金研研究者のResearcherID
imr_researcherIDs = df_imr_researcher["ResearcherID"].values.tolist()
# 金研研究者の名前
imr_name = df_imr_researcher["English Name"].values.tolist()
# 金研研究者のScopus著者ID
imr_scopusIDs = df_imr_researcher["Scopus_AuthorID"].values.tolist()

##############################
# 部局分析の準備
##############################
bukyokumei = ["IMR"]
df_dics_bukyoku = df_dics[df_dics["Abbrevia"].isin(bukyokumei)]

##############################
# 部局Scopusデータセットの作成
## 部局名文字列作成
bukyokulist = []
for i in df_dics_bukyoku["OrgsNameE"]:
    # 正規表現に用いる記号を処理し、
    # ', 'を先頭に付ける。
    i = i.replace("(", "\(")
    i = i.replace(")", "\)")
    i = i.replace("-", "\-")
    i = i.replace(".", "\.")
    i = ", " + i
    bukyokulist.append(i)
bukyokunames = "|".join(bukyokulist)
## Scopus Author ID列の作成
scpsid = []
for i in df_imr_researcher["Scopus_AuthorID"]:
    i = str(i)
    if i != "unkown":
        i = ";" + i + ";"
        scpsid.append(i)
scpsids = "|".join(scpsid)

# 部局名辞書により抽出したscopusデータセット
# 列「著者＋所属機関」に部局名表記を含むものを抽出
df_tmp = df_scps[df_scps["著者 + 所属機関"].str.contains(bukyokunames, na=False)]
# 部局名辞書で抽出された論文データフレーム（念のため重複を削除しておく）
df_scps_bukyoku = df_tmp.drop_duplicates()

# 部局未判明論文
df_scps_chk = df_scps[~df_scps["著者 + 所属機関"].str.contains(tunames, na=False)]
plusstr = lambda i: ";" + i
df_scps_chk["chk"] = df_scps_chk["著者ID"].apply(plusstr)

df_scps_researcher = df_scps_chk[df_scps_chk["chk"].str.contains(scpsids)]
del df_scps_researcher["chk"]
# 一旦統合
df_scps_imr = pd.concat([df_scps_bukyoku, df_scps_researcher])
notIMR = []
for i in df_scps_imr["EID"][df_scps_imr["著者 + 所属機関"].str.contains("Advanced, Institute")]:
    notIMR.append(i)
# 　面倒なものを除いて、データフレームをもう一度作り直す。
df_scps_imr = df_scps_imr[~df_scps_imr["EID"].isin(notIMR)]
df_scps_imr = df_scps_imr.drop_duplicates()

##############################
# 部局WoSデータセットの作成
## 部局名文字列作成
bukyokulist = []
for i in df_dics_bukyoku["OrgsNameE"]:
    # 正規表現に用いる記号を処理し、
    # ', 'を先頭に付ける。
    i = i.replace("(", "\(")
    i = i.replace(")", "\)")
    i = i.replace("-", "\-")
    i = i.replace(".", "\.")
    # imrlist2.append(i)
    i1 = ", " + i
    i2 = "] " + i
    bukyokulist.append(i1)
    bukyokulist.append(i2)
# 部局名辞書の表記を文字列化
bukyokunames = "|".join(bukyokulist)
# 部局名辞書により抽出したscopusデータセット
# 列「著者＋所属機関」に部局名表記を含むものを抽出
df_tmp = df_wos[df_wos["Addresses"].str.contains(bukyokunames, na=False)]
# 部局名辞書で抽出された論文データフレーム（念のため重複を削除しておく）
df_wos_bukyoku = df_tmp.drop_duplicates()
# なお、金研を対象とするWoSの文献データフレームには、所属機関名が金研であっても、著者が金研に所属していない研究者ではない場合がありました。その文献書誌情報を見ると所属機関名の表記の区切り方が間違えていることを確認しています。そのような文献書誌情報を金研の文献データフレームから削除する必要があることから以下の操作を行っています。
# 金研ではない所属機関情報のものを除く
if bukyokumei == "IMR":
    notIMR = [
        "Tohoku Univ, Inst Mat Res, Inst Fluid Sci & Adv, Sendai, Miyagi 9808577, Japan"
    ]
    df_wos_bukyoku = df_wos_bukyoku[
        ~df_wos_bukyoku["Addresses"].str.contains(notIMR[0])
    ]

# ### 部局名辞書を使って、部局不明の論文データフレーム を作成
tulist = []
for i in df_dics_tu["OrgsNameE"]:
    i = i.replace("(", "\(")
    i = i.replace(")", "\)")
    i = i.replace("-", "\-")
    i = i.replace(".", "\.")
    # i = ', '+i
    tulist.append(i)
tunames = "|".join(tulist)

## 部局が判明していないもののデータフレームを作成
df_tmp = df_wos[~df_wos["Addresses"].str.contains(tunames, na=False)]
df_wos_other = df_tmp.drop_duplicates()
# 部局不明論文データフレーム から金研論文をResearcherIDを使って抽出
imr_researcherIDs = sorted(set(imr_researcherIDs))
imr_researcherIDs.remove("unknown")
imrresearcherids = "|".join(imr_researcherIDs)
# ResearcherIDで抽出
df_wos_imr2 = df_wos_other[df_wos_other["Researcher Ids"].str.contains(imrresearcherids, na=False)]
# 著者名で抽出
# 名前の大文字・小文字調整
namelist = []
for i in imr_name:
    print(i)
    for j in tu.mknamelistWoS(i):
        namelist.append(j)
# %% codecell
namelist2 = []
for i in namelist:
    i = i + "[^a-z]"
    namelist2.append(i)
researchernames = "|".join(namelist2)
df_wos_other2 = df_wos_other[~df_wos_other["UT (Unique WOS ID)"].isin(df_wos_imr2["UT (Unique WOS ID)"])]
df_wos_imr3tmp = df_wos_other2[df_wos_other2["Author Full Names"].str.contains(researchernames, na=False)]
researchernames2 = "Niinomi, Mitsuo|Sugiyama, Kazumasa|Nakajima, Kazuo|Shimada, Yusuke|Yoshikawa, Akira|Semboshi, Satoshi"
df_wos_imr3 = df_wos_imr3tmp[df_wos_imr3tmp["Author Full Names"].str.contains(researchernames2, na=False)]
df_wos_imr3.to_excel("/Users/yumoto/Desktop/wos_著者名抽出.xlsx")
# ### WoSデータフレーム の統合
df_wos_imr = pd.concat([df_wos_bukyoku, df_wos_imr2, df_wos_imr3])
df_wos_imr = df_wos_imr.drop_duplicates()

###################
# 確認
df_scps_imr.pivot_table(values="EID", columns=["文献タイプ"], index=["出版年"], aggfunc=len)
df_wos_imr.pivot_table(
    values="UT (Unique WOS ID)",
    columns=["Document Type"],
    index=["Publication Year"],
    aggfunc=len,
)
df_scps_imr.to_excel(home + "/result/scps_imr_20220629.xlsx")
df_wos_imr.to_excel(home + "/result/wos_imr_20220629.xlsx")

# 金属材料研究所論文
# scopusに掲載されていて、SciValに掲載されていない論文（同じ時期で調べないと意味がない）
df_chk = df_scps_imr[~df_scps_imr["EID"].isin(df_scival["EID"])]
df_chk.to_excel(home + "/result/chkList.xlsx")
df_chk2021 = df_chk[df_chk["出版年"] == 2021]
# 著者所属機関表記の確認
names = []
for i in df_chk2021["著者 + 所属機関"]:
    if "; " in i:
        elms = i.split("; ")
        for j in elms:
            names.append(j)
    else:
        names.append(i)
names = sorted(set(names))
df_chkname = pd.DataFrame(names)
df_chkname.to_excel(home + "/result/chkname_20220630.xlsx")

# 金属材料研究所2021年論文
df_scps2021 = df_scps_imr[df_scps_imr["出版年"] == 2021]
df_wos2021 = df_wos_imr[df_wos_imr["Publication Year"] == 2021]
df_scps2021.to_excel(home + "/result/scps2021.xlsx")
scpsdoi = []
for i in df_scps2021["doi"]:
    i = str(i)
    if len(i) > 3:
        scpsdoi.append(i)
len(scpsdoi)
wosdoi = []
for i in df_wos2021["doi"]:
    i = str(i)
    if len(i) > 3:
        wosdoi.append(i)
    else:
        #print(">>", i, "<<")
        pass
len(wosdoi)

# 重複、非重複の状況把握
df_scpsWos2021 = df_scps2021[df_scps2021["doi"].isin(wosdoi)]
df_wosScp2021 = df_wos2021[df_wos2021["doi"].isin(scpsdoi)]
df_scpsNotWos2021 = df_scps2021[~df_scps2021["doi"].isin(wosdoi)]
df_wosNotScp2021 = df_wos2021[~df_wos2021["doi"].isin(scpsdoi)]
df_scpsWos2021.to_excel(home + "/result/scpsWos2021.xlsx")
df_wosScp2021.to_excel(home + "/result/wosScps2021.xlsx")
df_scpsNotWos2021.to_excel(home + "/result/scpsNotWos2021.xlsx")
df_wosNotScp2021.to_excel(home + "/result/wosNotScps2021.xlsx")

len(df_scpsWos2021)
len(df_wosScp2021)

######################
# 東北大学DBデータの処理
# ScopusやWoSに登録されていない情報を抽出する
df_tudb_c = df_tudb[~df_tudb["doi"].isin(scpsdoi)]
df_tudb_c2 = df_tudb_c[~df_tudb_c["doi"].isin(wosdoi)]
len(df_tudb_c)
len(df_tudb_c2)
df_tudb_c2.to_excel(home + "/result/東北大DBデータ確認用.xlsx")
