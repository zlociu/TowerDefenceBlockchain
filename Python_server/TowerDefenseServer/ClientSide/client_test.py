import requests
from zipfile import ZipFile
import os


def login():

    while True:
        patch = input("wpisz")

        if patch == "y":

            login = "test_user"
            password = "admin"

        elif patch == "n":
            login = "nie"
            password = "nie"

        elif patch == "1":
            login = input("login: ")
            password = input("password: ")

        else:
            break
        r = requests.post('http://127.0.0.1:8000/login', {"login": login, "pass": password})

        print(r)
        print(r.content)


def send_map(map_array):

    content = {"map": map_array, "player_address": "player_address_1"}

    r = requests.post('http://127.0.0.1:8000/map_upload', data=content)

    print(r.json())


def request_map(map_addr):

    r = requests.get(f'http://127.0.0.1:8000/map_download/{map_addr}')

    print(r.json())


def send_update():
    url = 'http://127.0.0.1:8000/request_update'

    path = "client_files/files.zip"
    dst_path = "client_files/files"

    response = requests.get(url, stream=True)
    handle = open(path, "wb")
    for chunk in response.iter_content(chunk_size=512):
        if chunk:  # filter out keep-alive new chunks
            handle.write(chunk)
    handle.close()

    with ZipFile(path, "r") as zip:
        zip.extractall(dst_path)

    os.remove(path)


if __name__ == '__main__':

    # login()
    # map_array = "1; 1; 1; 1; 1; 2; 2; 2; 2; 2; 3; 3; 3; 3; 3; 4; 4; 4; 4; 4; 5; 5; 5; 5; 5"
    # send_map(map_array)
    # map_addr = "random_address"
    # request_map(map_addr)
    send_update()