# iMacに用意したMySQLを利用する
# ハンゼン先生取得のSciValデータ

from sqlalchemy import Column, String
from setting import Base, engine

class User(Base):
    """
    """
    pass


def main():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    main()
