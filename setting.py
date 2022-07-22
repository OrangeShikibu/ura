# iMacに用意したMySQLを利用する
# ハンゼン先生取得のSciValデータ

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()
import os

HOST = os.getenv("HOST")
USER = os.getenv("USERNAME")
PASSWD = os.getenv("PASSWORD")
DB = os.getenv("DATABASE")

# データベース接続
engine = create_engine(f"mysql://{USER}:{PASSWD}@{HOST}/{DB}?charset=utf8")
session = scoped_session(sessionmaker(bind=engine))

# modelで使用する
Base = declarative_base()
Base.query = session.query_property()
