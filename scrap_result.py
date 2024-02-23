from bs4 import BeautifulSoup
import requests
import os.path
import json
import csv
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

municipios = {"SDE":223,
              "SDN":225,
              "SDO":224,
              "DN":2,
              }

primer_colegio_id = 11909
ultimo_colegio_id = 17324
# Note the firs colegioid is 11909 and last is 17324
failed = []


def get_cargos():
    """obtiene info de los cargos de los electivos"""
    url = "https://resultadoselecciones2024.jce.gob.do/api/filter/getCargos"
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chro1me/121.0.0.0 Safari/537.36"}
    response = requests.get(url, headers=headers, verify=False )
    if response.status_code != 200:
        raise ConnectionError ( f"Error in Page, got {response.status_code}")
    
    content = response.content
    parser = BeautifulSoup(content, "html.parser")
    return parser.text

def get_municipios(cargo_id):
    url = f"https://resultadoselecciones2024.jce.gob.do/api/filter/getMunicipio/{cargo_id}"
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chro1me/121.0.0.0 Safari/537.36"}
    response = requests.get(url, headers=headers, verify=False )
    if response.status_code != 200:
        raise ConnectionError ( f"Error in Page, got {response.status_code}")
    
    content = response.content
    parser = BeautifulSoup(content, "html.parser")
    return parser.text    

def get_colegios(cargo_id, municipio_id):
    """retorna el listado de colegio dado el cargo y el municipio"""
    url = f"https://resultadoselecciones2024.jce.gob.do/api/College?filter=&cargoId={cargo_id}&municipioId={municipio_id}&soloConResultados=N&PageIndex=1&PageSize=100"
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}
    response = requests.get(url, headers=headers, verify=False )
    
    if response.status_code != 200:
        raise ConnectionError ( f"Error in Page, got {response.status_code}")
    
    content = response.content
    parser = BeautifulSoup(content, "html.parser")
    return parser.text    


    

def get_results(colegio_id,municipio_id, cargo_id):
    """retorna los resultado del ud de colegio dados"""
    url = f"https://resultadoselecciones2024.jce.gob.do/api/College/info?cargoId={cargo_id}&municipioId={municipio_id}&colegioId={colegio_id}"
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}
    response = requests.get(url, headers=headers, verify=False )
    
    if response.status_code != 200:
        raise ConnectionError ( f"Error in Page, got {response.status_code}")
    
    content = response.content
    parser = BeautifulSoup(content, "html.parser")
    return parser.text


if __name__ == "__main__":
    print("Getting Data ...")
    cargos_path = "data/cargos.json"

    if not os.path.exists(cargos_path):
            with open(cargos_path, "w") as f:
                f.writelines(get_cargos())

    try:
        sde_colegios = json.loads(get_colegios(11,municipios["SDE"]))
        with open("data/sde/colegios.json", "w") as f:
            json.dump(sde_colegios, f)
    except ConnectionError as e:
        with open("data/sde/colegios.json", "r") as f:
            sde_colegios = json.load(f)

    
    for colegio_id in sde_colegios["items"]:
        if os.path.exists(f"data/sde/colegio_{colegio_id['letra']}.json"):
            #print(f"File colegio_{colegio_id}.json exist skipping...")
            continue 
        try:
           raw_data = get_results(cargo_id=61,municipio_id=municipios["SDE"],colegio_id=colegio_id["id"])
           with open(f"data/sde/colegio_{colegio_id['letra']}.json", "w") as f:
               f.writelines(raw_data)
        except ConnectionError as e:
            failed.append(colegio_id)
            print(f"El colegio {colegio_id['letra']} a fallado su descarga, detalles", e)
        except PermissionError as e:
            print(e)
    
    for _ in range(5):
        for colegio_id in failed:
            try:
               raw_data = get_results(cargo_id=61,municipio_id=municipios["SDE"],colegio_id=colegio_id["id"])
               with open(f"data/sde/colegio_{colegio_id['letra']}.json", "w") as f:
                   f.writelines(raw_data)
                   failed.remove(colegio_id)
            except ConnectionError as e:
                print(f"El colegio {colegio_id['letra']} a fallado su descarga, detalles", e)
            except PermissionError as e:
                print(e)

    print("finished to download election data")
    print(f"Total files: {len(sde_colegios['items'])}")
    print(f"Missing colegios number: {len(failed)}")
    print("Missing colegios id:", *failed)    


