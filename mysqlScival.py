# iMacに用意したMySQLを利用する
# ハンゼン先生取得のSciValデータ
# https://qiita.com/curry__30/items/432a21426c02a68e77e8

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float
from sqlalchemy import text

import pandas as pd

import config

HOST = config.HOST
USER = config.USER
PASSWD = config.PASSWD
DB = config.DB

# engineの設定
engine = create_engine(f"mysql://{USER}:{PASSWD}@{HOST}/{DB}?charset=utf8")

# セッションの作成
db_session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)

# DB:scivalのテーブル名をリスト化
tbls = []
with engine.connect() as conn:
    rows = conn.execute(text("SHOW Tables"))
    for row in rows:
        tbls.append(row[0])
        #print(row[0])
len(tbls)


def getvalue(eid,l):
    eid = eid
    l = l
    for i in l:
        exetext = "SELECT F\-W_Outputs_in_Top_Citation_Percentiles_per_percentile FROM "+i+" WHERE EID='"+eid+"'"
        with engine.connect() as conn:
            result = conn.execute(text(exetext))
        print(result.all())
print('end')

getvalue('2-s2.0-85052294506',tbls)
