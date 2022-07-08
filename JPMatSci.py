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
# wosのデータディレクトリのpathを設定
data = "/googleMyDrive/data/wos/JPMatSci20220708/"
df_wos = wos.mkDataFrame(home + data)
df_wos["doi"] = df_wos["DOI"].str.lower()
df_wos = df_wos.astype({'Addresses': 'str'})

df_wos.pivot_table(
    values="UT (Unique WOS ID)",
    columns=["Document Type"],
    index=["Publication Year"],
    aggfunc=len,
)

df_wos['Addresses']
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
    for j in tu.mknamelistWoS(i):
        namelist.append(j)

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

df_p=df_wos_imr.pivot_table(
    values="UT (Unique WOS ID)",
    columns=["Document Type"],
    index=["Publication Year"],
    aggfunc=len,
)
df_p
# エクセルで出力する場合
#df_wos_imr.to_excel(home + "/result/JPMatSci_imr_20220708.xlsx")
#df_p.to_excel(home + "/result/JPMatSci_imr_pivot_20220708.xlsx")

# 研究機関を分析する
df_wos.columns
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

names = []
for i in names0:
    if "] " in i:
        pass
        elms = i.split('] ')
        if len(elms) > 2:
            print(elms)
        else:
            #print(elms[1])
            names.append(elms[1])
        #print(i)
    else:
        pass
        #print(i)
        names.append(i)

names = sorted(set(names))
len(names)

names1 = []
for i in names:
    if '; ' in i:
        pass
        elms = i.split('; ')
        for j in elms:
            names1.append(j)
    else:
        names1.append(i)
names1 = sorted(set(names1))
def cleanchimei(text):
    text = re.sub(', Japan$', ',', text)
    text = re.sub(', \d+,$',',',text)
    text = re.sub(', \w* \d*,$', ',', text)
    text = re.sub(', [A-Z][a-z]+,$',',',text)
    text = re.sub(',\s*\d+\s+[A-Z][a-z]+,$',',',text)
    text = re.sub(',\s*\d+\-\d+\s+[A-Z][a-z]+,$',',',text)
    text = re.sub(',\s*\d+\-\d+\-\d+\s+[A-Z][a-z]+,$',',',text)
    text = re.sub(',\s*\d+\s+[A-Z][a-z]+\sCho,$',',',text)
    text = re.sub(',\s*\d+\-\d+\s+[A-Z][a-z]+\sCho,$',',',text)
    text = re.sub(',\s*\d+\-\d+\-\d+\s+[A-Z][a-z]+\sCho,$',',',text)
    text = re.sub(',\s+[A-Z][a-z]+\s\d+,$',',',text)
    text = re.sub(',\s+[A-Z][a-z]+\s\d+\-\d+,$',',',text)
    text = re.sub(',\s+[A-Z][a-z]+\s\d+\-\d+\-\d+,$',',',text)
    text = re.sub(',\s*[A-Z]\w* [Kk]u,$',',',text)
    text = re.sub(',\s*\d+\-\d+\s+[A-Z][a-z]+\s[A-Z][a-z]+,$',',',text)
    text = re.sub(',\s*\d+\-\d+\-\d+\s+[A-Z][a-z]+\s[A-Z][a-z]+,$',',',text)

    text = re.sub(',\s+Aizu Wakamatsu,$',',',text)
    text = re.sub(',\s+[A-Z][a-z]+\sCho,$',',',text)
    text = re.sub(', I\-1\-1 Umezono,$',',',text)
    text = re.sub(', 1919\-1 Tancha, Onna Son,$',',',text)
    text = re.sub(', 1\-1 Marunouchi 3 Chorne,$',',',text)
    text = re.sub(', 1\-1 Rokkodai Cho,$',',',text)
    text = re.sub(', 1\-17\-134 Omachi,$',',',text)
    text = re.sub(', 1\-2\-1 Izumi Cho,$',',',text)
    text = re.sub(', 1\-297 Wakiyama,$',',',text)
    text = re.sub(', 1\-32 Machikaneyama,$',',',text)
    text = re.sub(', 1\-32\-1 Nishifu Machi,$',',',text)
    text = re.sub(', 1\-7\-1 Hanabatake,$',',',text)
    text = re.sub(', 11\-1 Mihogaoka,$',',',text)
    text = re.sub(', 116\-2 Kamedanakanocho,$',',',text)
    text = re.sub(', 1200 Matsumoto Cho,$',',',text)
    text = re.sub(', 165 Koen Cho,$',',',text)
    text = re.sub(', 165 Koencho,$',',',text)
    text = re.sub(', 2\-1 Hirosawa,$',',',text)
    text = re.sub(', 2\-1\-1 Katahira,$',',',text)
    text = re.sub(', 2\-1\-52\-202 Wakaehigashimachi,$',',',text)
    text = re.sub(', 2\-12\-1 Hisakata,$',',',text)
    text = re.sub(', 2\-12\-1 Ookayama,$',',',text)
    text = re.sub(', 2\-15\-11 Serigaya Chou,$',',',text)
    text = re.sub(', 2\-2 Yamadaoka,$',',',text)
    text = re.sub(', 2\-20\-9 Tomatsucho,$',',',text)
    text = re.sub(', 2\-39\-1 Kurokami,$',',',text)
    text = re.sub(', 2\-6\-1 Nagasaka,$',',',text)
    text = re.sub(', 2\-610 Uedayama,Tenpaku,$',',',text)
    text = re.sub(', 205 Kyushu Univ, Int Res Ctr Hydrogen Energy,$',',',text)
    text = re.sub(', 22\-19 Murakumo Cho,$',',',text)
    text = re.sub(', 2217\-20 Hayashi Cho,$',',',text)
    text = re.sub(', 228\-7399 Nakagawa,Hosoe Cho,$',',',text)
    text = re.sub(', 250 Ryusen Cho,$',',',text)
    text = re.sub(', 255 Shimo Okubo,$',',',text)
    text = re.sub(', 27\-1 Rokkakubashi,$',',',text)
    text = re.sub(', 3\-1 Shinchi,Fuchu Cho,$',',',text)
    text = re.sub(', 3\-1\-1 Yoshinodai,$',',',text)
    text = re.sub(', 3\-24\-24 Nakahara,$',',',text)
    text = re.sub(', 31\-20,$',',',text)
    text = re.sub(', 3975\-18 Haijima Cho,$',',',text)
    text = re.sub(', 3D Printing Corp,$',',',text)
    text = re.sub(', 3DOM Inc,$',',',text)
    text = re.sub(', 4D Sensor Inc,$',',',text)
    text = re.sub(', 5\-3\-1 Kojimachi,$',',',text)
    text = re.sub(', 5000 Hirakuchi,$',',',text)
    text = re.sub(', 53 Kawahara Cho,Shogoin Sakyo Ku,$',',',text)
    text = re.sub(', 6 Ehime Univ, Geodynam Res Ctr,$',',',text)
    text = re.sub(', 6\-6 Aramaki,$',',',text)
    text = re.sub(', 6\-6\-02 Aramaki Aza Aoba,$',',',text)
    text = re.sub(', 6\-6\-02Aramaki Aza Aoba,$',',',text)
    text = re.sub(', 650 Mitsuzawa,Hosaka Cho, Nirasaki City,$',',',text)
    text = re.sub(', 7\-3\-1 Hongo,$',',',text)
    text = re.sub(', 713 Shake Aza,$',',',text)
    text = re.sub(', 744 Motooka,$',',',text)
    text = re.sub(', 8 Ichiban Cho,$',',',text)
    text = re.sub(', 8\-3\-5 Nagaura Ekimae Sodegaura,$',',',text)
    text = re.sub(', 8020 Promot Fdn,$',',',text)
    text = re.sub(', 866 Nakane,$',',',text)
    text = re.sub(', 970 Shimoise,Hayashida Cho,$',',',text)
    text = re.sub(', 1\-36\-2\-3F Shinjuku,$',',',text)
    text = re.sub(', 1\-1 Gakuen Kibanadai Nishi,$',',',text)
    text = re.sub(', 1247 Yachigusa,\s*Yakusa Cho,$',',',text)

    return text

japan = []
overseas = []
for i in names1:
    if ', Japan' in i:
        i = cleanchimei(i)
        i = cleanchimei(i)
        japan.append(i)
    else:
        overseas.append(i)
japan = sorted(set(japan))
len(japan)
with open(home+'/Desktop/chk.txt','w') as f:
    for i in japan:
        print(i)
        i=i+'\n'
        f.write(i)
f.close()

df_chk = df_wos[df_wos['Addresses'].isin(['nan'])]
df_chk
