import json
import requests
from decouple import config
from geopy import distance
import folium
import logging


def fetch_coordinates(apikey, address):
    base_url = 'https://geocode-maps.yandex.ru/1.x'
    response = requests.get(base_url, params={
        'geocode': address,
        'apikey': apikey,
        'format': 'json',
    })
    response.raise_for_status()
    found_places = response.json()[
        'response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(' ')
    return lat, lon


def get_coffeehouse_distance(coffeehouse):
    return coffeehouse['distance']


def main():
    apikey = config('APIKEY_YANDEX_GEOCODER')

    with open('src/coffee.json', 'r', encoding='CP1251') as file_coffeehouses:
        src_coffeehouses = json.loads(file_coffeehouses.read())

    while True:
        user_address = input('Где вы находитесь? ')

        if user_address == '':
            logging.error('Получено пустое значение user_address')
            continue

        user_coordinates = fetch_coordinates(apikey, user_address)

        if user_coordinates is None:
            logging.error('Получено пустое значение user_coordinates '
                          + 'при выполнении функции fetch_coordinates '
                          + f'с параметром user_address = "{user_address}"')
            continue
        else:
            logging.basicConfig(level=logging.INFO)
            logging.info(f'Для user_address = "{user_address}" получены '
                         + f'user_coordinates = "{user_coordinates}"')
            break

    ext_coffeehouses = []

    for src_coffeehouse in src_coffeehouses:
        ext_coffeehouses.append({
            'title': src_coffeehouse['Name'],
            'latitude': src_coffeehouse['Latitude_WGS84'],
            'longitude': src_coffeehouse['Longitude_WGS84'],
            'distance': distance.distance(
                user_coordinates,
                (src_coffeehouse['Latitude_WGS84'],
                 src_coffeehouse['Longitude_WGS84'])
            ).km,
        })

    user_map = folium.Map(user_coordinates, zoom_start=16)
    folium.Marker(
        location=user_coordinates,
        tooltip='Жмякни',
        popup='Я',
        icon=folium.Icon(icon='user', color='red'),
    ).add_to(user_map)

    for ext_coffeehouse in sorted(ext_coffeehouses,
                                  key=get_coffeehouse_distance)[:5]:
        folium.Marker(
            location=(ext_coffeehouse['latitude'],
                      ext_coffeehouse['longitude']),
            tooltip='Жмякни',
            popup=ext_coffeehouse['title'],
            icon=folium.Icon(icon='leaf', color='green'),
        ).add_to(user_map)

    user_map.save('index.html')


if __name__ == '__main__':
    main()
