import os
import requests
from pprint import pprint
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

owner_id = input("Введите ID пользователя: ") or 1
count = input("Введите количество фотографий: ") or 5

vk_token = os.environ.get("VK_TOKEN")

VK_URL = 'https://api.vk.com/method/'                 # Базовый адрес обращения к VK API
YA_URL = 'https://cloud-api.yandex.net/v1/disk/'      # Базовый адрес обращения к YA API

params_photo_profile = {                              # Параметры подгрузки фоток в профиле
    'owner_id': owner_id,
    'album_id': 'profile',
    'extended': '1',
    'access_token': vk_token,
    'v': '5.131'
}
params_photo_wall = {                                  # Параметры подгрузки фоток на стене
    'owner_id': owner_id,
    'album_id': 'wall',
    'extended': '1',
    'access_token': vk_token,
    'photo_sizes': 1,
    # 'count': count,
    'v': '5.131'
}
ya_headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'OAuth {os.environ.get("YA_TOKEN")}'
}

photos_list = []
owner_folder = requests.get(f'{VK_URL}users.get?user_ids={owner_id}&access_token={vk_token}&v=5.131').json()
photos = requests.get(f'{VK_URL}photos.get', params=params_photo_wall).json()

if 'error' in photos:
    pprint("Пользователь ограничил просмотр своих фотографий на стене")
else:
    for photo in tqdm(photos['response']['items'], ncols=80, desc="Получаем фото"):
        href = photo['sizes'][-1]['url']
        if href[-4:] == '.jpg':
            res_photo = {'name': f"{photo['likes']['count']}.jpg", 'size': photo['sizes'][-1]['type'], 'href': href}
            photos_list.append(res_photo)


name_folder = owner_folder['response'][0]['last_name']
folder_result = requests.put(f'{YA_URL}resources?path={name_folder}', headers=ya_headers).json()

for photo in tqdm(photos_list[:count], ncols=80, ascii=True, desc="Загружаем фотографии на диск"):
    name_file = photo['name']                     # Имя файла
    href_file = photo['href']                      #Путь к файлу
    check_result = None
    if check_result not in ['in-progress', 'success']:
        result = requests.post(f'{YA_URL}resources/upload?url={href_file}&path={name_folder}'
                               f'/photo_with_like_{name_file}&disable_redirects=true&overwrite=true',
                               headers=ya_headers).json()

        check_result = requests.get(result['href'], headers=ya_headers).json()['status']

