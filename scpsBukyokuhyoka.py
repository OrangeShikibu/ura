# 東北大学部局評価用　Scopus文献リスト作成
import pandas as pd
import os

from researchcapability import Scopus

# ホームディレクトリのpathを設定
home = os.environ["HOME"]
# データディレクトリのpathを設定
data = "/data/scopus/20220627/"

scps = Scopus()

# scopusデータの読み込み
df = scps.mkDataFrame(home + data)

# ===============================================================
# 部局名辞書の読み込み
dict1 = "/data/dict/current/dict_TU_Orgs_Name_20220627.xlsx"
df_dics = pd.read_excel(home + dict1)
## 金属材料研究所
bukyokumei = ["IMR"]
df_dics_bukyoku = df_dics[df_dics["Abbrevia"].isin(bukyokumei)]
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

##
bukyokumei2 = ["unknown"]
df_dics_tu = df_dics[~df_dics["Abbrevia"].isin(bukyokumei2)]
df_dics_tu.head()
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

# ==============================================================
# 金属材料研究所研究者のデータファイル
imrresearchers = home + "/data/IMR/IMR_Researchers/IMR_researchers_20220415.xlsx"
df_imr_researcher = pd.read_excel(imrresearchers)

scpsid = []
for i in df_imr_researcher["Scopus_AuthorID"]:
    i = str(i)
    if i != "unkown":
        i = ";" + i + ";"
        scpsid.append(i)

scpsids = "|".join(scpsid)

# 金属材料研究所　部局名辞書より抽出
df_imr1 = df[df["著者 + 所属機関"].str.contains(bukyokunames, na=False)]

# 部局未判明論文
df_chk = df[~df["著者 + 所属機関"].str.contains(tunames, na=False)]
plusstr = lambda i: ";" + i

df_chk.columns
df_chk["chk"] = df_chk["著者ID"].apply(plusstr)
df_imr2 = df_chk[df_chk["chk"].str.contains(scpsids)]
del df_imr2["chk"]

df_imr2
df_imr = pd.concat([df_imr1, df_imr2])
df_imr = df_imr.drop_duplicates()
df_imr.to_excel(home + "/result/scps_imr_20220627.xlsx")
df_imr2.to_excel(home + "/result/scps_imr2_20220627.xlsx")

df_imr.pivot_table(values="EID", columns=["文献タイプ"], index=["出版年"], aggfunc=len)

# 以下は辞書更新作業用エクセルファイル作成
"""
df_chk.to_excel(home + "/result/scps_chk_20220627.xlsx")
chks = []
for i in df_chk["著者 + 所属機関"]:
    if ";" in i:
        elms = i.split("; ")
        for j in elms:
            chks.append(j)
    else:
        # print(i)
        chks.append(i)
chks = sorted(set(chks))

chks1 = []
for i in chks:
    if "Tohoku" in i:
        elms = i.split("., ")
        for j in elms:
            chks1.append(j)
chks1 = sorted(set(chks1))

chks2 = []
for i in chks1:
    if ", Japan," in i:
        elms = i.split(", Japan, ")
        for j in elms:
            if "Tohoku" in j:
                chks2.append(j)
    else:
        if "Tohoku" in i:
            chks2.append(i)
chks2 = sorted(set(chks2))
dft = pd.DataFrame(chks2)
dft.to_excel(home + "/Desktop/chk.xlsx")
"""
