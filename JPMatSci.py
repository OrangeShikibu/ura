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


youso = []
for i in names1:
    if re.search(', Japan',i):
        elms = re.split(',',i)
        for j in elms:
            j=j.strip()
            youso.append(j)
        #print(i)
youso = sorted(set(youso))

chkyouso = []
jusyo = []
with open(home+'/Desktop/chk.txt','w') as f:
    chkyouso = []
    for i in youso:
        ii = i.lower()
        if re.search('^japan', ii) or re.search('^nippon',ii) or re.search('^nihon',ii):
            pass
            chkyouso.append(i)
        elif re.search(' univ$',ii) or re.search('^univ ',ii) or re.search(' univ ',ii):
            pass
            chkyouso.append(i)
        elif re.search('^adv ', ii) or re.search('^dept ', ii) or re.search(' dept$',ii):
            pass
            chkyouso.append(i)
        elif re.search(' labs*$', ii) or re.search(' inst$', ii) or re.search(' sci$', ii):
            pass
            chkyouso.append(i)
        elif re.search(' ltd$',ii) or re.search(' inc$', ii) or re.search(' kk$',ii) or re.search('cor*p*', ii):
            pass
            chkyouso.append(i)
        elif re.search('^AIST ',i) or re.search('^acad ',ii) or re.search(' ctr*$',ii):
            pass
            chkyouso.append(i)
        elif re.search('project$', ii) or re.search('hosp$', ii) or re.search('technol$',ii):
            pass
            chkyouso.append(i)
        elif re.search('^appl', ii) or re.search(' engn$', ii) or re.search(' grp$',ii) or re.search(' div$',ii):
            pass
            chkyouso.append(i)
        elif re.search('^ctr [a-z]',ii) or re.search('^div ', ii) or re.search('^fac',ii):
            pass
            chkyouso.append(i)
        elif re.search('^elect', ii) or re.search('^element', ii) or re.search('^frontiers*',ii):
            pass
            chkyouso.append(i)
        elif re.search('team$',ii) or re.search('unit$',ii) or re.search('^global',ii):
            pass
            chkyouso.append(i)
        elif re.search('^grad ',ii) or re.search('^scha',ii) or re.search(' sch$',ii) :
            pass
            chkyouso.append(i)
        elif re.search('^high',ii) or re.search('res ctr',ii) or re.search('program(me)*$',ii):
            pass
            chkyouso.append(i)
        elif re.search('^ind ',ii) or re.search('^informat',ii) or re.search('^innovat',ii):
            pass
            chkyouso.append(i)
        elif re.search('^inst\w* ',ii) or re.search('^int\w* ',ii) or re.search(' res$',ii):
            pass
            chkyouso.append(i)
        elif re.search('daigaku',ii) or re.search('inst tech',ii) or re.search('^lab',ii):
            pass
            chkyouso.append(i)
        elif re.search('^mat ',ii) or re.search('^math\w* ',ii) or re.search('^micro\w* ',ii):
            pass
            chkyouso.append(i)
        elif re.search(' dent ',ii) or re.search('^minist',ii) or re.search('ind sci res',ii):
            pass
            chkyouso.append(i)
        elif re.search('res inst ',ii) or re.search('^nano(\s|m)* ',ii) or re.search('^natl*',ii):
            pass
            chkyouso.append(i)
        elif re.search('^new\w* ',ii) or re.search('^nucl',ii) or re.search('^open',ii):
            pass
            chkyouso.append(i)
        elif re.search('^or(al|g) ',ii) or re.search('sect$',ii) or re.search('pit$',ii):
            pass
            chkyouso.append(i)
        elif re.search('field$',ii) or re.search('headquar*ters*$',ii) or re.search('^res & (dev|educ|serv)',ii):
            pass
            chkyouso.append(i)
        elif re.search('^sc[hi] ',ii) or re.search('^sect\w* ',ii) or re.search('^tech ',ii):
            chkyouso.append(i)
        elif re.search('^technol', ii) or re.search('^unit\w* ',ii) or re.search('^wpi\w* ',ii):
            chkyouso.append(i)
        elif re.search('^world',ii) or re.search('PRESTO',i) or re.search(' JST',i) or re.search('agcy$',ii):
            chkyouso.append(i)
        elif re.search('Environm(\s|$)',i) or re.search('Hub$',i) or re.search('^alliance',ii):
            chkyouso.append(i)
        elif re.search('^assoc', ii) or re.search(' chem$',ii) or re.search(' med$', ii):
            chkyouso.append(i)
        elif re.search(' best$',ii) or re.search('^biomed',ii) or re.search('Bioengi*n ', i):
            chkyouso.append(i)
        elif re.search('NIMS', i) or re.search('^[A-Z]+$', i) or re.search(' dent$', ii):
            chkyouso.append(i)
        elif re.search('cent\w* [a-z]+', ii) or re.search('^(ceram|chem) ',ii) or re.search('inst sci',ii):
            chkyouso.append(i)
        elif re.search(' (elect|power|refinery|works)$',ii) or re.search(' mat$',ii) or re.search('^clin',ii):
            chkyouso.append(i)
        elif re.search(' AIST(\s|$)',i) or re.search(' dev$',ii) or re.search('^dev',ii) or re.search('^dent',ii):
            chkyouso.append(i)
        elif re.search('kaisha',ii) or re.search(' japan$',ii) or re.search(' clin$',ii):
            chkyouso.append(i)
        elif re.search('ERATO',i) or re.search('elytmax',ii) or re.search('management$',ii):
            chkyouso.append(i)
        elif re.search('^(educ|energy)',ii) or re.search('fac$',ii) or re.search('^environm',ii):
            chkyouso.append(i)
        elif re.search('^field',ii) or re.search(' (org|off|stn|syst)$',ii) or re.search('^fdn',ii):
            chkyouso.append(i)
        elif re.search(' acad$',ii) or re.search(' ind acad ',ii) or re.search('ctr organ',ii):
            chkyouso.append(i)
        elif re.search('renewable',ii) or re.search('^(funct|fus) ',ii) or re.search(' soc$',ii):
            chkyouso.append(i)
        elif re.search('GaN ',i) or re.search('G(REEN|reen)',i) or re.search(' assoc$',ii) or re.search('gerodontol',ii):
            chkyouso.append(i)
        elif re.search('gen educ',ii) or re.search('^grp',ii) or re.search('interdisciplinary',ii):
            chkyouso.append(i)
        elif re.search(' net$',ii) or re.search('^head ',ii) or re.search('radiat ctr',ii):
            chkyouso.append(i)
        elif re.search(' ge$',ii) or re.search(' (energy|solut|met)$',ii) or re.search('^human',ii):
            chkyouso.append(i)
        elif re.search('hydrogen',ii) or re.search('technol ctr',ii) or re.search('JAXA',i):
            chkyouso.append(i)
        elif re.search('IRIDeS',i) or re.search('icc ',ii) or re.search('wpi$',ii):
            chkyouso.append(i)
        elif re.search('plant$',ii) or re.search('govt$',ii) or re.search(' bur$',ii):
            chkyouso.append(i)
        elif re.search('imaging',ii) or re.search('impact',ii) or re.search('nursing',ii):
            chkyouso.append(i)
        elif re.search(' (phys|firm)$',ii) or re.search(' PARC',i) or re.search('spring\s*8',ii):
            chkyouso.append(i)
        elif re.search('JA*M*STE*C*',i) or re.search('steel$',ii) or re.search('JSPS',i):
            chkyouso.append(i)
        elif re.search('joining',ii) or re.search('(branch|gakuin|design)$',ii):
            chkyouso.append(i)
        elif re.search('r&d$',ii) or re.search('CMRC$',i) or re.search('mem lab',ii):
            chkyouso.append(i)
        elif re.search('inst ind',ii) or re.search('indistrial tech',ii) or re.search('KPSI',i):
            chkyouso.append(i)
        elif re.search('forum$',ii) or re.search('ind ltd',ii) or re.search('open innovat',ii):
            chkyouso.append(i)
        elif re.search('appl sci',ii) or re.search('forestry off',ii) or re.search('pharmaceut',ii):
            chkyouso.append(i)
        elif re.search('museum$',ii) or re.search('educ$',ii) or re.search('org educ',ii) or re.search('observ',ii):
            chkyouso.append(i)
        elif re.search('inst photo',ii) or re.search('(phoen|tec)$',ii) or re.search('(associates|depot)$',ii):
            chkyouso.append(i)
        elif re.search(' hosp ',ii) or re.search(' hq$',ii) or re.search('^L[Ii](A|MMS) ',i):
            chkyouso.append(i)
        elif re.search('^liberal arts',ii) or re.search('life ',ii) or re.search('^lise',ii):
            chkyouso.append(i)
        elif re.search('MaD[Ii]S',i) or re.search('MANA',i) or re.search('Mech',i):
            chkyouso.append(i)
        elif re.search('surg$',ii) or re.search('^med ',ii) or re.search('inst adv',ii):
            chkyouso.append(i)
        elif re.search('^mfg ',ii) or re.search(' mat ',ii) or re.search('^mol ',ii) or re.search('nanomat ',ii):
            chkyouso.append(i)
        elif re.search('platform$',ii) or re.search('NAMA',i) or re.search('nanoquine',ii):
            chkyouso.append(i)
        elif re.search('nanosci',ii) or re.search('^(network|neutron|next)',ii) or re.search('res lab',ii):
            chkyouso.append(i)
        elif re.search(' (ind|batteri|equipment)$',ii) or re.search('riken ',ii) or re.search('oil$',ii):
            chkyouso.append(i)
        elif re.search('^off ',ii) or re.search('creat$',ii) or re.search('factory$',ii):
            chkyouso.append(i)
        elif re.search(' fdn$',ii) or re.search('^opt',ii) or re.search('^ortho',ii) or re.search('periodont',ii):
            chkyouso.append(i)
        elif re.search('^photon',ii) or re.search('program',ii) or re.search('project',ii) or re.search('Dept \d+$',i):
            chkyouso.append(i)
        elif re.search('^(qst|quantum) ',ii) or re.search('qbic$',ii) or re.search('^res ',ii):
            chkyouso.append(i)
        elif re.search('promot$',ii) or re.search('res\w*\sctr',ii) or re.search('prosthodont',ii):
            chkyouso.append(i)
        elif re.search(' (gk|applicat|operat|fupet|giro|gijuts*u)$',ii) or re.search('RIKEN$',i):
            chkyouso.append(i)
        elif re.search('^soken\s*dai',ii) or re.search('^S[PR]ring',i) or re.search('cens*ter',ii):
            chkyouso.append(i)
        elif re.search('source$',ii) or re.search('llc$',ii) or re.search('r&d inst',ii) or re.search('polytech$',ii):
            chkyouso.append(i)
        elif re.search('prison$',ii) or re.search('^secretariat',ii) or re.search(' med ctr ',ii):
            chkyouso.append(i)
        elif re.search('enterprise$',ii) or re.search('PT Kanefusa',i) or re.search('Panasonic',i):
            chkyouso.append(i)
        elif re.search('(giken|serv)$',ii) or re.search('Ub*i*n*vers',i) or re.search('techn$',ii):
            chkyouso.append(i)
        elif re.search('shop$',ii) or re.search('vehicles$',ii) or re.search('^polytech',ii):
            chkyouso.append(i)
        elif re.search('business$',ii) or re.search('^(portfolio|presto|prior org|profitet)',ii):
            chkyouso.append(i)
        elif re.search('endodont$',ii) or re.search(' nat$',ii) or re.search('mission',ii):
            chkyouso.append(i)
        elif re.search('engn lab',ii) or re.search('^solar frontier',ii) or re.search('(innovat|design) ctr',ii):
            chkyouso.append(i)
        elif re.search('strategy$',ii) or re.search('(TEL|tagen|TOTO|House|TAISEI)',i):
            chkyouso.append(i)
        elif re.search('capacitor',ii) or re.search('k\s*k$',ii) or re.search(' (ink|kogyo|sanso)$',ii):
            chkyouso.append(i)
        elif re.search(' team(\s|$)',ii) or re.search('agr forest',ii) or re.search('^tokyo tech',ii):
            chkyouso.append(i)
        elif re.search('therapy$',ii) or re.search('alliance$',ii) or re.search('UTokyo',i):
            chkyouso.append(i)
        elif re.search('UEC',i) or re.search(' Inc ',i) or re.search('UVSOR',i) or re.search('UnivToyama',i):
            chkyouso.append(i)
        elif re.search('^Univ$',i) or re.search('CNER$',i) or re.search('(WOW|WPP)',i):
            chkyouso.append(i)
        elif re.search('West Japan',i) or re.search('Logist$',i) or re.search(' Works ',i):
            chkyouso.append(i)
        elif re.search('inst earth sci',ii) or re.search('lodge$',ii) or re.search('sangyosya$',ii):
            chkyouso.append(i)
        elif re.search('builder$',ii) or re.search('glass$',ii) or re.search('AISTU',i):
            chkyouso.append(i)
        #elif re.search('^B',i) or re.search('^\d',i) or re.search('^shakai fukushi',ii):
            #pass
        else:
            f.write(i+'\n')
            jusyo.append(i)
f.close()

jusyo = sorted(set(jusyo))
chkyouso = sorted(set(chkyouso))
with open(home+'/Desktop/chk2.txt','w') as f:
    for i in chkyouso:
        f.write(i+'\n')
f.close()
