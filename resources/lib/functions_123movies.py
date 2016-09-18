from BeautifulSoup import BeautifulSoup
import hashlib
import json
import random
import string
from helpers import make_request, make_request_no_redirect

SITE_URL = "http://123movies.to/"


def _get_menu():
    resp = make_request(SITE_URL)

    soup = BeautifulSoup(resp)

    div_menu = soup.find('div', {'id': 'menu'})

    li_level1 = div_menu.find('ul').findAll('li', recursive=False)

    menu = []

    for li in li_level1:
        a = li.find('a')
        attrs = dict(a.attrs)
        if attrs['title'] in ('Genre', 'Country'):
            children = []
            for a in li.find('ul').findAll('a'):
                children.append({'title': a.text, 'url': dict(a.attrs)['href']})
            menu.append({'title': attrs['title'], 'url': '', 'children': children})
        elif attrs['title'] == 'TV - Series':
            menu.append({'title': attrs['title'], 'url': attrs['href']})

    return menu

def get_main_menu_options():
    menu = _get_menu()

    options = []

    for item in menu:
        item.pop('children', None)
        options.append(item)

    return options


def get_menu_options(title):
    menu = _get_menu()

    options = []

    for item in menu:
        if item['title'] == title:
            options = item['children']

    return options


def get_listing(url):
    resp = make_request(url)

    soup = BeautifulSoup(resp)

    li_next = soup.find('div', {'id': 'pagination'}).find('li', {'class': lambda x: x and 'next' in x.split()})

    next_link = None
    if li_next:
        next_link = dict(li_next.find('a').attrs)['href']

    div_movies = soup.find('div', {'class': lambda x: x and 'movies-list-full' in x.split()}).findAll('div', {'class': lambda x: x and 'ml-item' in x.split()})

    listing = {
        'next': next_link,
        'listing': []
    }

    for div_movie in div_movies:
        quality_span = div_movie.find('span', {'class': lambda x: x and 'mli-quality' in x.split()})
        quality = None
        if quality_span:
            quality = quality_span.text
        listing['listing'].append({
            'movie_id': dict(div_movie.attrs)['data-movie-id'],
            'title': div_movie.find('h2').text,
            'quality': quality,
            'image': dict(div_movie.find('img').attrs)['data-original'],
            'url': dict(div_movie.find('a').attrs)['href'],
        })

    return listing


def get_movie_servers(movie_id):
    url = '{0}ajax/v2_get_episodes/{1}'.format(SITE_URL, movie_id)

    resp = make_request(url)

    soup = BeautifulSoup(resp)

    div_servers = soup.findAll('div', {'class': lambda x: x and 'le-server' in x.split()})

    movie_info = []

    for div_server in div_servers:
        server_name = div_server.find('strong').text.strip()
        js_info = map(int, dict(div_server.find('a').attrs)['onclick'].replace('loadEpisode(', '').replace(')', '').split(','))

        movie_info.append({
            'title': server_name,
            'info': js_info
        })

    return movie_info


def get_movie(server_name, server_id, movie_code):
    movie_info = []

    video_url = None
    if server_id in (0, 12, 13, 14, 15):
        video_url = json.loads(make_request('{0}ajax/load_embed/{1}'.format(SITE_URL, movie_code)))['embed_url']
        movie_info.append({
            'title': server_name,
            'url': video_url
        })
    else:
        uniq = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(6))
        key = hashlib.md5('{0}{1}7bcq9826avrbi6m4'.format(movie_code, uniq)).hexdigest()
        cookie = 'i6m49vd7shxkn985mhodk{0}twz87wwxtp3dqiicks2dfyud213k6yg={1}'.format(movie_code, uniq)
        info = json.loads(make_request('{0}ajax/get_sources/{1}/{2}/2'.format(SITE_URL, movie_code, key), cookie))
        for source in info['playlist'][0]['sources']:
            movie_info.append({
                'title': '{0} ({1})'.format(server_name, source['label']),
                'url': make_request_no_redirect(source['file']).url
            })

    return movie_info
