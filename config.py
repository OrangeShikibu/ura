# iMacに用意したMySQLを利用する
# ハンゼン先生取得のSciValデータをMySQLに登録している。
# データベースへアクセスするための設定
from dotenv import load_dotenv
load_dotenv()
import os

HOST = os.getenv("HOST")
USER = os.getenv("USERNAME")
PASSWD = os.getenv("PASSWORD")
DB = os.getenv("DATABASE")
