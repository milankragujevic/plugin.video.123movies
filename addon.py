import os.path
import sys
import urlparse
import xbmcplugin

sys.path = [os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'lib'), ] + sys.path

import functions_123movies as f
import helpers as h


def main_index():
    for option in f.get_main_menu_options():
        if not option['url']:
            h.add_dir(addon_handle, base_url, option['title'], option['url'], 'menu_options')
        else:
            h.add_dir(addon_handle, base_url, option['title'], option['url'], 'listing')


def menu_options():
    for option in f.get_menu_options(h.extract_var(args, 'name')):
        h.add_dir(addon_handle, base_url, option['title'], option['url'], 'listing')


def listing():
    listing_info = f.get_listing(h.extract_var(args, 'url'))
    for info in listing_info['listing']:
        title = info['title']
        if info['quality'] is not None:
            title += ' ({0})'.format(info['quality'])
        h.add_dir(addon_handle, base_url, title, info['movie_id'], 'movie_servers', info['image'], info['image'])


def movie_servers():
    for info in f.get_movie_servers(h.extract_var(args, 'url')):
        h.add_dir(addon_handle, base_url, info['title'], '{0},{1}'.format(info['info'][0], info['info'][1]), 'movie')

def movie():
    url_info = h.extract_var(args, 'url').split(',')
    name = h.extract_var(args, 'name')

    links = f.get_movie(name, int(url_info[0]), int(url_info[1]))

    for info in links:
        h.add_dir_video(addon_handle, info['title'], info['url'], '', '')


base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', ['', ])[0]

if mode:
    globals()[mode]()
else:
    main_index()

xbmcplugin.endOfDirectory(addon_handle)
