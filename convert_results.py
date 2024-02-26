import csv
import pandas as pd
import numpy as np
import json
#with open("relacion_circunscripcion_colegio_sde.csv", "r", encoding="utf-8") as f:
#    data = csv.DictReader(f)

data = pd.read_csv("relacion_circunscripcion_colegio_sde.csv")

print(data.head)

def reformat_colums(colegio):
     jsondata = pd.read_json(f"data/sde/colegio_{colegio}.json", dtype={"letra": str})
     print(jsondata["votosPreferenciales"][0])
     num_colums = len(jsondata["votosPreferenciales"][0])
     votos = pd.DataFrame(list(jsondata["votosPreferenciales"]))
     votos.columns = ["Casilla_{}".format(x) for x in range(1,num_colums +1)]
     new_votos = votos.map(lambda x: x["votos"])
     new_cat = pd.concat([jsondata,new_votos], axis=1)
     #print(new_cat.head())
     #print(jsondata.head())
     #print(new_cat["Casilla_4"].loc[2],"----", jsondata["votosPreferenciales"].loc[2])
     return new_cat


pda = reformat_colums(colegio="0001")
pdb = reformat_colums(colegio="0911A")
data_gen = (reformat_colums(x) for x in ["0001","0911A","2349"])
new_data = pd.concat(data_gen, ignore_index=True, )
print(new_data)
new_data = new_data.fillna(-1)
new_data = new_data.astype({"Casilla_10": np.int64, })
print(new_data.dtypes)
