import pandas as pd
import os

from researchcapability import Scopus

# ホームディレクトリのpathを設定
home = os.environ["HOME"]
# データディレクトリのpathを設定
data = "/data/scopus/20220607/"
print(home)
scps = Scopus()
