import json
import os
import re
import zipfile
from datetime import datetime
from pathlib import Path

import django
from django.contrib.auth import authenticate, logout, login
from django.db.utils import IntegrityError
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from std_server.models.graphics_model import Graphic, Music
from std_server.models.level_model import Level
from std_server.models.player_model import Player
from std_server.models.setter_model import Test
from std_server.models.turret_model import Turret
from std_server.models.user_model import MyUser


@csrf_exempt
def register(request):
    username = request.POST['username']
    passwd = request.POST['password']

    print(username)
    print(passwd)

    game_build = Test.objects.get(name="game").actual_build

    try:
        MyUser.objects.create_user(username=username, password=passwd, game_build=game_build)
        response = JsonResponse({"User": "Created"})
        response.status_code = 201
        print("register OK")
    except django.db.utils.IntegrityError:
        response = JsonResponse({"User": "Already exists"})
        response.status_code = 409

    return response


@csrf_exempt
def login_user(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        response = JsonResponse({"User": "Logged"})
        response.status_code = 201
    else:
        response = JsonResponse({"User": "Invalid login"})
        response.status_code = 401

    return response


def logout_view(request):
    logout(request)


# noinspection PyBroadException
def setup(request):
    """
    url: /setup
    :param request: GET
    Run to setup database with default data
    """

    try:
        Test.objects.create(actual_build=0)

        MyUser.objects.create(username="test_user_1", password="admin", game_build=0)

        user = MyUser.objects.get(username="test_user_1")

        Player.objects.create(identity=user,
                              user_address="user_address_1",
                              player_address="player_address_1",
                              level=0,
                              points=0)

        Player.objects.get(user_address="user_address_1")

        response = JsonResponse({"success": True})
    except Exception:
        response = JsonResponse({"success": False})

    return response


def update_stats(request):
    identity = request.POST['player']
    new_level = request.POST['level']

    status = Player.objects.filter(identity=identity).update(level=new_level)

    if status:
        response = JsonResponse({"Player": "Error"})
        response.status_code = 403
    else:
        response = JsonResponse({"Player": f"new level: {new_level}"})
        response.status_code = 200

    return response


def create_player(request):
    """
    Constructor
    # id = unique number, will be public key
    # login = user's name
    # password = password hashed with SHA256
    """

    identity = request.POST['identity']
    player_address = request.POST['player_address']
    user_address = request.POST['user_address']

    Player.objects.get_or_create(
        identity=identity,
        player_address=player_address,
        user_address=user_address
    )


# noinspection PyBroadException
@csrf_exempt
def map_upload(request):
    """
    url: /map-upload

    map_array - map array written as positive integers, separated with ";".
    player_address - field in Player object.
    :param request: POST {"map": map_array, "path": player_address}
    :return:
    {"status": "map successfully loaded"}, status code: 201
    {"status": "error loading map"}, status code: 400
    """
    content_json = json.loads(request.body)
    map_array = content_json["map"]
    map_path: str = content_json["path"]

    try:
        print(map_array)

        if map_path.endswith(".json"):
            map_path -= ".json"

        Path("data/Levels/").mkdir(parents=True, exist_ok=True)
        with open(f"data/Levels/{map_path}.json", "w+") as f:
            f.write(json.dumps({'map': map_array}))

        Level.objects.update_or_create(path=map_path)

        response = JsonResponse({"status": "map successfully loaded"})
        response.status_code = 201
    except Exception:
        response = JsonResponse({"status": "error loading map"})
        response.status_code = 400

    return response


# noinspection PyBroadException
@csrf_exempt
def map_download(request):
    """
    url: /map-download?name={map_name}

    :param request: GET
    :return:
    {"map": map_obj.map_array}, status code 200
    {"map": "Failed"}, status code 404
    """
    try:
        map_name = str(request.GET.get('name'))
        map_obj = Level.objects.get(name=map_name)
        with open(map_obj.path, "r") as f:
            map_json: dict = json.loads(f.read())
        response = JsonResponse(map_json)
        response.status_code = 200
    except Exception:
        response = JsonResponse({})
        response.status_code = 404

    return response


# noinspection PyBroadException
@csrf_exempt
def turret_download(request):
    """
    url: /turret-download?name={map_name}

    :param request: GET
    :return:
    {"turret": map_obj.map_array}, status code 200
    {"map": "Failed"}, status code 404
    """
    try:
        turret_name = str(request.GET.get('name'))
        turret_obj = Turret.objects.get(name=turret_name)
        with open(turret_obj.path, "r") as f:
            turret_json: dict = json.loads(f.read())
        response = JsonResponse(turret_json)
        response.status_code = 200
    except Exception:
        response = JsonResponse({})
        response.status_code = 404

    return response


def serve_new_instance(request):
    """
    Used for new user, that wants to download game.

    url: /download-full-game

    :param request: GET
    :return:
    Stream containing zipfile with all game files including graphic and music.
    """
    files = Graphic.objects.all()

    filenames = []
    zipfile_name = "zip_z_plikami"

    print("XDDDDDDD")

    for f in files.all():
        filenames.append(f.path)

    print(filenames)

    response = HttpResponse(content_type='application/zip')
    zip_file = zipfile.ZipFile(response, 'w')
    for filename in filenames:
        zip_file.write(filename)
    response['Content-Disposition'] = f'attachment; filename={zipfile_name}'
    return response


def submit_update(request):
    """
    ! Used only by administrator.
    Loading all files from path to database.
    {path} = "TowerDefense\\Packages"
    Method, that updates game files.

    url: /submit-update

    :param request: GET
    ver = version number : positive integer
    :return:
    {"update": "ok"}, status code 200
    """
    t = Test.objects.get(name="game")
    date = datetime.now()

    _, _, r1, r2, _, m1, m2, _, d1, d2, *_ = str(date)

    build = ""

    build = build + r1 + r2 + m1 + m2 + d1 + d2

    print(build)

    t.actual_build = ver = build

    t.save()

    graphic_files = []
    sound_files = []
    level_files = []
    turret_files = []

    # List all files
    for root, dirs, paths in os.walk(os.getcwd() + os.path.sep + "data"):
        for path in paths:
            file_path: str = os.path.join(root, path).replace("\\", "/")
            file_path = "." + re.search(r".+(/data.+)", file_path).group(1)
            if "sprites" in root.lower():
                graphic_files.append(file_path)
            elif "sounds" in root.lower():
                sound_files.append(file_path)
            elif "levels" in root.lower():
                level_files.append(file_path)
            elif "turrets" in root.lower():
                turret_files.append(file_path)

    # Clean undesired files

    g_all = Graphic.objects.all()
    m_all = Music.objects.all()

    for g in g_all:
        if g.path not in graphic_files:
            Graphic.objects.get(path=g.path).delete()

    for m in m_all:
        if m.path not in sound_files:
            Music.objects.get(path=m.path).delete()

    # Update database

    for path in graphic_files:
        g, _ = Graphic.objects.get_or_create(path=path, build=ver)
        g.version = ver

    for path in sound_files:
        m, _ = Music.objects.get_or_create(path=path, build=ver)
        m.version = ver

    for path in level_files:
        level_name = path.split("/")[-1].split(".")[0]
        level_obj, _ = Level.objects.get_or_create(name=level_name, path=path)
        level_obj.version = ver

    for path in turret_files:
        with open(path, 'r') as file:
            turret_name: str = json.loads(file.read())['name']
        turret_obj, _ = Turret.objects.get_or_create(name=turret_name, path=path)
        turret_obj.version = ver

    response = JsonResponse({"update": "ok"})
    response.status_code = 200

    return response


def serve_newest_update(request):
    """
    user_identity - unique user id.
    System for updating game files.
    url: /request-update?version={version}
    :param request: GET
    :return:
    """

    version = int(request.GET.get('version', '-1'))

    actual_build = Test.objects.get(name="game").actual_build

    if version >= actual_build:
        response = JsonResponse({"status": "up-to-date"})
        response.status_code = 200
    else:
        files = []

        all_graphic = Graphic.objects.all()
        all_music = Music.objects.all()

        zip_name = f"update_{actual_build}.zip"

        [files.append(b.path) for b in all_graphic if b.build > version]
        [files.append(b.path) for b in all_music if b.build > version]

        print(files)

        response = HttpResponse(content_type='application/zip')
        response.set_cookie("build", actual_build)

        print(response.cookies['build'])

        zip_file = zipfile.ZipFile(response, 'w')
        for filename in files:
            zip_file.write(filename)
        response['Content-Disposition'] = f'attachment; filename={zip_name}'

        print(response.items())

    return response


def list_all_maps(request):
    maps = Level.objects.all()

    map_list = []

    for m in maps:
        map_list.append(m.name)

    response = JsonResponse({"maps": map_list})
    response.status_code = 200

    return response
