import pandas as pd
import os
from researchcapability import SciVal

home = os.environ["HOME"]
sv = SciVal()

home

xfile = home + "/data/NIMS/Publications_NIMS.xlsx"
df = pd.read_excel(xfile, skiprows=18)
len(df)
xfile = home + "/data/NIMS/Publications_NIMS_WT.xlsx"
df1 = pd.read_excel(xfile, skiprows=19)

df0 = df[~df["EID"].isin(df1["EID"])]
df0.to_excel(home + "/data/NIMS/NIMS_notWT.xlsx")
