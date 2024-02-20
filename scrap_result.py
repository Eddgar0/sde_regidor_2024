from bs4 import BeautifulSoup
import requests
import json
import time
import csv
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



primer_colegio_id = 11909
ultimo_colegio_id = 17324
# Note the firs colegioid is 11909 and last is 17324
failed = []




def get_colegios(colegio_id):
    """retorna los colegios dados los ids"""
    url = f"https://resultadoselecciones2024.jce.gob.do/api/College/info?cargoId=61&municipioId=223&colegioId={colegio_id}"
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}
    response = requests.get(url, headers=headers, verify=False )
    
    if response.status_code != 200:
        raise ConnectionError ( f"Error in Page, got {response.status_code}")
    
    content = response.content
    parser = BeautifulSoup(content, "html.parser")
    return parser.text


if __name__ == "__main__":
    print("Getting Data ...")
    for colegio_id in range(primer_colegio_id, ultimo_colegio_id + 1):
        try:
           raw_data = get_colegios(colegio_id=colegio_id)
           with open(f"results/colegio_{colegio_id}.json", "w") as f:
               f.writelines(raw_data)
        except ConnectionError as e:
            failed.append(colegio_id)
            print(f"El colegio {colegio_id} a fallado su descarga, detalles", e)
        except PermissionError as e:
            print(e)
    
    for _ in range(3):
        for colegio_id in failed:
            try:
               raw_data = get_colegios(colegio_id=colegio_id)
               with open(f"results/colegio_{colegio_id}.json", "w") as f:
                   f.writelines(raw_data)
                   failed.remove(colegio_id)
            except ConnectionError as e:
                print(f"El colegio {colegio_id} a fallado su descarga, detalles", e)
            except PermissionError as e:
                print(e)

    print("finished to download election data")
    print(f"Missing colegios number: {len(failed)}")
    print("Missing colegios id:", *failed)    
    
    #with open(f"results/colegio{primer_colegio_id}.json","r") as f:
    #    data = data =json.load(f)
    
    #print(data[-1])
    #print( *[d["votosPreferenciales"] for d in data], sep="\n")


