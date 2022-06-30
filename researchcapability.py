"""
Created on Wed Jul  8 14:03:06 2020

@author: yumoto
"""

import pandas as pd
import os
import datetime, pathlib


class Scopus:
    def __init__(self):
        print("Scopusを処理できます。")
        pass

    def mkDataFrame(self, directory):
        """

        Parameters
        ----------
        directory : ディレクトリの指定
            Scopusのデータが置かれているディレクトリを指定します。
            データは再帰的に読み込まれます。

        Returns
        -------
        scpsdf : pandasのデータフレーム
            読み込まれたScopuデータをpandasのデータフレーム形式で返します。

        """
        # 指定ディレクトリ内を再帰的に読み込み、ファイルを抽出
        self.directory = directory
        scpsfiles = []
        for curDir, dirs, files in os.walk(directory):
            for file in files:
                if "scopus" in file and ".csv" in file:
                    scpsfiles.append(os.path.join(curDir, file))

        df = []
        for filen in scpsfiles:
            # print(filen)
            tmpdf = pd.read_csv(filen)
            df.append(tmpdf)

        scpsdf = pd.concat(df, ignore_index=True, sort=False)
        return scpsdf

    def c12afad(self, c1):
        self.c1 = c1

        elms = []
        if "; " in c1:
            elms1 = c1.split("; ")
            for i in elms1:
                elms.append(i)
            pass
        else:
            elms.append(c1)

        return elms

    def orgs(self, c1):
        self.c1 = c1
        # print('OK')
        elms = self.c12afad(c1)
        orgs = []
        for elm in elms:
            elms1 = elm.split("., ")
            for i in elms1:
                orgs.append(i)
        orgs = sorted(set(orgs))

        return orgs


class SciVal:
    def __init__(self):
        print("SciValを処理できます。")

    def mkDataFrame(self, file):
        self.file = file

        columdata = []
        insertdata = []
        with open(file, "r", encoding="utf-8") as f:

            chk = 0
            for line in f:
                # エルゼビアがScopusデータを更新した日の取得
                if "Date last updated" in line:
                    tmp, update = line[:-1].split(",")
                    udate = datetime.datetime.strptime(update, "%d %B %Y").strftime(
                        "%Y/%m/%d"
                    )
                    # print(update, udate)

                # ハンゼン先生がScopusデータを入手した日の取得
                if "Date exported" in line:
                    tmp, exdate = line[:-1].split(",")
                    edate = datetime.datetime.strptime(exdate, "%d %B %Y").strftime(
                        "%Y/%m/%d"
                    )
                    # print(exdate, edate)

                # 項目名の行を取得
                if "Scopus Author Ids" in line:
                    line = line[:-1]

                    elms = line.split('","')
                    for elm in elms:
                        elm = elm.replace('"', "")
                        columdata.append(elm)
                    columdata.append("update")
                    columdata.append("exdate")
                    # print(columdata)
                    chk = 1

                # 書誌データの取扱
                if chk == 0:
                    pass
                else:

                    if "Elsevier B.V. All rights reserved." in line:
                        pass
                    elif "2-s2.0" in line:
                        line = line[:-1]
                        print(line)
                        elms = line.split('","')
                        elms[0] = elms[0].replace('"', "")
                        elms[-1] = elms[-1].replace('"', "")

                        for i in range(len(elms)):
                            if elms[i] == "-":
                                elms[i] = ""
                            if "𝔾a" in elms[i]:
                                elms[i] = elms[i].replace("𝔾a", "Ga")
                        elms.append(udate)
                        elms.append(edate)

                        tup = tuple(elms)
                        # insertdata.append(tup)
                        if len(tup) == 42:
                            insertdata.append(tup)
                        else:
                            # print(tup)
                            print(len(elms))
                            insertdata.append(tup)  # test 20200828
                            # break
                            pass

        f.close()

        insertdata = sorted(set(insertdata))
        df = pd.DataFrame(insertdata, columns=columdata)
        # print(len(columdata))
        cc = 0
        for i in columdata:
            # print(cc,i)
            cc += 1
        return df

    def mkDataFrame2(self, file):
        self.file = file
        columdata = []
        insertdata = []
        with open(file, "r", encoding="utf-8") as f:
            chk = 0
            for line in f:
                # エルゼビアがScopusデータを更新した日の取得
                if "Date last updated" in line:
                    tmp, update = line[:-1].split("\t")
                    udate = datetime.datetime.strptime(update, "%d %B %Y").strftime(
                        "%Y/%m/%d"
                    )
                    # print(update, udate)
                    # ハンゼン先生がScopusデータを入手した日の取得
                if "Date exported" in line:
                    tmp, exdate = line[:-1].split("\t")
                    edate = datetime.datetime.strptime(exdate, "%d %B %Y").strftime(
                        "%Y/%m/%d"
                    )
                    # print(exdate, edate)
                    # 項目名の行を取得
                if "Scopus Author Ids" in line:
                    line = line[:-1]
                    elms = line.split("\t")
                    for elm in elms:
                        elm = elm.replace('"', "")
                        columdata.append(elm)
                    columdata.append("update")
                    columdata.append("exdate")
                    # print(columdata)
                    chk = 1
                    # 書誌データの取扱
                if chk == 0:
                    pass
                else:
                    if "Elsevier B.V. All rights reserved." in line:
                        pass
                    elif "2-s2.0" in line:
                        line = line[:-1]
                        # print(line)
                        elms = line.split("\t")
                        elms[0] = elms[0].replace('"', "")
                        elms[-1] = elms[-1].replace('"', "")

                        for i in range(len(elms)):
                            if elms[i] == "-":
                                elms[i] = ""
                            if "𝔾a" in elms[i]:
                                elms[i] = elms[i].replace("𝔾a", "Ga")
                        elms.append(udate)
                        elms.append(edate)
                        tup = tuple(elms)
                        # insertdata.append(tup)
                        if len(tup) == 42:
                            insertdata.append(tup)
                        else:
                            # print(tup)
                            print(len(elms))
                            insertdata.append(tup)  # test 20200828
                            # break
                            pass
        f.close()

        insertdata = sorted(set(insertdata))
        df = pd.DataFrame(insertdata, columns=columdata)
        # print(len(columdata))
        cc = 0
        for i in columdata:
            # print(cc,i)
            cc += 1
        return df


class WoS:
    def __init__(self):
        print("WoSを処理できます。")
        pass

    def mkDataFrame(self, directory):
        """
        Web of Scienceの書誌情報（エクセル形式）をpythonで扱うデータフレームに変換する関数
        Parameters
        ----------
        directory : strings
            Web of Scienceのデータが置かれているディレクトリを指定します。
            データは再帰的に読み込まれます。

        Returns
        -------
        wosdf : pandasのデータフレーム
            読み込まれたWeb of Scienceデータをpandasのデータフレーム形式で返します。

        """
        self.directory = directory
        wosfiles = []
        for curDir, dirs, files in os.walk(directory):
            for file in files:
                if "savedrecs" in file and ".xls" in file:
                    wosfiles.append(os.path.join(curDir, file))

        df = []
        for file in wosfiles:
            tmpdf = pd.read_excel(file)
            df.append(tmpdf)

        wosdf = pd.concat(df, ignore_index=True, sort=False)
        return wosdf

    def c12afad(self, c1):

        """
        著者とその所属機関のデータを活用するためのリストを作成する関数
        Parameters
        ----------
        c1 : Script
            著者所属情報　Addresses列 (旧C1列）

        Returns
        -------
        afad :List
            [著者] 所属機関名＆住所を要素とするリスト

        """
        # 複数の著者＋所属機関名住所を区分け

        self.c1 = c1

        elms = []
        if "; [" in c1:
            c1 = c1.replace("; [", "; [[")
            elms = c1.split("; [")
            pass
        elif "[" in c1:
            elms.append(c1)
            pass
        elif ";" in c1:
            elms = c1.split("; ")
            pass
        else:
            elms.append(c1)
            pass

        return elms

    def mknamelist(self, afsadd):

        self.afsadd = afsadd
        afsadd = afsadd.replace("[", "")
        names, org = afsadd.split("]")
        names = names.strip()
        # org = org.strip()

        # if a == 'names':
        #    ret = names
        # else:
        #    ret = org
        return names

    def mkafad(self, c1):
        """
        Address列から著者名を返す

        Parameters
        ----------
        c1 : str
            Address列

        Returns
        -------
        namelist : list
            著者名のリスト

        """
        self.c1 = c1
        afadlist0 = self.c12afad(c1)
        # print(afadlist0)
        namelist = []

        for i in afadlist0:

            names = self.mknamelist(i)
            # print(names)
            if ";" in names:
                elms = names.split(";")
                for j in elms:
                    j = j.strip()
                    namelist.append(j)
                pass
            else:
                # print(names)
                namelist.append(names)

        namelist = sorted(set(namelist))

        returnlist = []
        for name in namelist:
            tmplist = []
            # print('---')
            # print(name)
            tmplist.append(name)
            for afad in afadlist0:
                if name in afad:
                    # print(afad)
                    elm = afad.split("]")
                    elm[1] = elm[1].strip()
                    tmplist.append(elm[1])
            # print(tmplist)
            resultline = "; ".join(tmplist)
            # print(resultline)

            returnlist.append(resultline)

        return returnlist

    def orgs(self, c1):
        """
        著者所属情報から所属機関名と住所を抽出してリストで出力する関数

        Parameters
        ----------
        c1 : script
            WoSのAddresses列（旧C1列）

        Returns
        -------
        orgs : list形式
            部局名と住所を要素とするリスト

        """
        self.c1 = c1
        elms = self.c12afad(c1)

        orgs = []
        for elm in elms:
            # org = self.orgname(elm)
            if "]" in elm:
                names, bukyoku = elm.split("] ")
            elif "[" in elm:
                # print(line)
                bukyoku = "OMMITED ORG&ADD, UNKNOWN"
            else:
                bukyoku = elm.strip()
            orgs.append(bukyoku)
        orgs = sorted(set(orgs))

        orgs1 = []
        for org in orgs:
            if ";," in org:
                orgs1.append(org)
            elif "; " in org:
                orgelms = org.split("; ")
                orgs1 += orgelms
            elif ";" in org:
                print("新しい表記パターンかも。")
                pass
            else:
                orgs1.append(org)
        orgs1 = sorted(set(orgs1))

        orgs = []
        for org in orgs1:
            if len(org) > 2:
                orgs.append(org)

        return orgs

    def intnldom(self, c1):
        """
        WoSのAddress列から国名を抽出して国際共著状況を判定する関数

        Parameters
        ----------
        c1 : script
            WoSのAddresses列

        Returns
        -------
        hantei : list
            国名のリストから国際共著状況を判定する
            但し、イングランド、スコットランド、ウェールズ、北アイルランドはUKとしている。

        """
        self.c1 = c1
        orgs = self.orgs(c1)

        nations = []
        for org in orgs:
            elms = org.split(", ")
            if " USA" in elms[-1]:
                elms[-1] = "USA"
            if elms[-1] == "P. R. China":
                elms[-1] = "Peoples R China"
            if (
                elms[-1] == "England"
                or elms[-1] == "Scotland"
                or elms[-1] == "Wales"
                or elms[-1] == "North Ireland"
            ):
                elms[-1] = "UK"
            nations.append(elms[-1])
        nations = sorted(set(nations))
        if len(nations) > 2:
            hantei = "Intl.Multi"
        elif len(nations) > 1:
            hantei = "Intl.Bi"
        else:
            hantei = "Domestic"
        return hantei


class TU:
    def __init__(self):
        print("東北大学に関するデータベースを処理できます。")
        pass

    def mkDataFrame(self, file):
        self.file = file
        df = pd.read_excel(file)
        return df

    def mknamelistWoS(self, line):
        self.line = line
        family, first = line.split(", ")
        family = family.capitalize()
        first = first.capitalize()

        name0 = family + ", " + first
        name1 = first + ", " + family
        name2 = name0.upper()
        name3 = name1.upper()
        name4 = name0.lower()
        name5 = name1.lower()

        namelist = [name0, name1, name2, name3, name4, name5]

        return namelist

    def mknamelistScps(self, line):
        self.line = line
        family, first = line.split(", ")
        family = family.capitalize()
        first = first.capitalize()

        name0 = family + ", " + first[0]
        name1 = first + ", " + family[0]
        name2 = name0.upper()
        name3 = name1.upper()
        name4 = name0.lower()
        name5 = name1.lower()

        namelist = [name0, name1, name2, name3, name4, name5]

        return namelist


if __name__ == "__main__":

    """datasetdir = '/Users/yumoto/Google Drive File Stream/共有ドライブ/data/'
    infile =datasetdir+'IMR/IMR_researchers_20200713.xlsx'
    #infile = '/Users/yumoto/Desktop/py_work/data/IMR_researchers_2020608.xlsx'
    infile ='wos/20200709/2019/savedrecs (4).xls'
    wos = WoS()
    df = pd.read_excel(datasetdir+infile)


    tmp1 = wos.mkafad('[Yumoto, Michiaki; Yumoto, Mariko] Kumamoto Univ, kumamoto, Japan; [Yumoto, Michiaki] Tohoku Univ, Inst Mat Res, Japan; [Kaibe, Kenji] Univ Tokyo, Japan')
    tmp2 = wos.orgs('[Yumoto, Michiaki; Yumoto, Mariko] Kumamoto Univ, kumamoto, Japan; [Yumoto, Michiaki] Tohoku Univ, Inst Mat Res, Japan; [Kaibe, Kenji] Univ Tokyo, Japan')
    for i in tmp1:
        print('Author:',i)"""

    kyoyudir = "/Users/yumoto/Google Drive File Stream/共有ドライブ/"
    scivaladir = "SciValMonitoringData20200525/"
    # yeardir = 'TU_20200318/'

    scival = SciVal()

    datadir0 = kyoyudir + scivaladir
    datedata = [
        "20200318",
        "20200325",
        "20200401",
        "20200408",
        "20200415",
        "20200422",
        "20200429",
        "20200513",
        "20200520",
        "20200527",
        "20200603",
        "20200610",
        "20200617",
        "20200624",
        "20200702",
        "20200709",
    ]
    datedata = ["20200714"]

    df_hit = []
    for ddd in datedata:
        if ddd == "20200624":
            datadir = datadir0 + "TU_" + ddd + " (Kyuteidai)/Tohoku University"
            pass
        else:
            datadir = datadir0 + "TU_" + ddd
        print("=== ", ddd)
        p_temp = pathlib.Path(datadir)
        file_list = []

        df_tmp0 = []
        for infile in list(p_temp.glob("**/Publication*.csv")):
            # print(infile)
            df0 = scival.mkDataFrame(infile)
            df_tmp0.append(df0)

        df_tmp0 = pd.concat(df_tmp0)
        df = df_tmp0.drop_duplicates()
        df0 = df[df["DOI"].isin(["10.1016/j.cep.2019.107531"])]

        df_hit.append(df0)
    df_hit = pd.concat(df_hit)
    df_hit.drop_duplicates()

    print(df_hit)
    df_hit.to_excel("/Users/yumoto/Desktop/tmp/suii.xlsx")
