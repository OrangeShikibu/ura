import pandas as pd
import os

from researchcapability import Scopus

# ホームディレクトリのpathを設定
home = os.environ["HOME"]
# データディレクトリのpathを設定
data = "/data/scopus/20220608/"

scps = Scopus()

# scopusデータの読み込み
df = scps.mkDataFrame(home + data)

## 以下は、GIMRT年次報告書作成時に設定したもの。
## IMR分析の際は、コメントしたまま
# data1 = "/data/scopus/20220608/2021"
# data2 = "/data/scopus/20220608/2022"
# df1 = scps.mkDataFrame(home + data1)
# df2 = scps.mkDataFrame(home + data2)
# df = pd.concat([df1, df2])

# ===============================================================
# 部局名辞書の読み込み
dict1 = "/data/dict/current/dict_TU_Orgs_Name_20211203.xlsx"
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

df_imr
df_imr.to_excel(home + "/Desktop/imr20162022.xlsx")

df_imr.pivot_table(values="EID", columns=["文献タイプ"], index=["出版年"], aggfunc=len)
