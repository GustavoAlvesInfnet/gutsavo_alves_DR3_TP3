import requests
import random

def random_canto():
    url = "https://xeno-canto.org/api/2/recordings?query=cnt:brazil"

    response = requests.get(url)

    json = response.json()

    rand = random.randint(0, len(json['recordings'])-1)

    # consigo o file a partir do ID
    file_url = json['recordings'][rand]['file']

    # baixo o arquivo
    response = requests.get(file_url, stream=True)

    # salvo o arquivo em um arquivo local
    with open('.\cantos\canto.mp3', 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            f.write(chunk)

    print("Arquivo baixado com sucesso!")

#random_canto()


def pesquisa_canto(nome_ave):
    url = f"https://xeno-canto.org/api/2/recordings?query={nome_ave}"

    response = requests.get(url)

    json = response.json()

    rand = random.randint(0, len(json['recordings'])-1)

    # consigo o file a partir do ID
    file_url = json['recordings'][rand]['file']

    # baixo o arquivo
    response = requests.get(file_url, stream=True)

    # salvo o arquivo em um arquivo local
    with open('.\cantos\canto_especifico.mp3', 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            f.write(chunk)

    print("Arquivo baixado com sucesso!")

#pesquisa_canto("Cockatiel")