import pandas as pd

table = pd.read_excel('portlist.xls', skiprows = 1, usecols = "H:I")
col_names = table.columns.values

for n in col_names :

    print (col_names(n))