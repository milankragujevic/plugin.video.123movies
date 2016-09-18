import urllib
import urllib2
import xbmcgui
import xbmcplugin


USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.130 Safari/537.36'


def make_request(url, cookie=None):
    request = urllib2.Request(url)
    request.add_header('User-Agent', USER_AGENT)
    if cookie is not None:
        request.add_header('Cookie', cookie)
    opener = urllib2.build_opener()
    response = opener.open(request)
    data = response.read()

    return data


def make_request_no_redirect(url):
    class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
        def http_error_301(self, req, fp, code, msg, headers):
            result = urllib2.HTTPRedirectHandler.http_error_301(
                self, req, fp, code, msg, headers)
            result.status = code
            return result

        def http_error_302(self, req, fp, code, msg, headers):
            result = urllib2.HTTPRedirectHandler.http_error_302(
                self, req, fp, code, msg, headers)
            result.status = code
            return result

    request = urllib2.Request(url)
    opener = urllib2.build_opener(SmartRedirectHandler())
    response = opener.open(request)

    return response


def add_dir(addon_handle, base_url, name, url, mode, icon_image='DefaultFolder.png', thumbnail='DefaultFolder.png', is_folder=True):
    u = base_url + '?' + urllib.urlencode({'url': urllib.quote(url, safe=''), 'mode': str(mode), 'name': urllib.quote(name, safe='')})

    liz = xbmcgui.ListItem(unicode(name), iconImage=icon_image, thumbnailImage=thumbnail)

    ok = xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=liz, isFolder=is_folder)

    return ok


def add_dir_video(addon_handle, name, url, thumbnail, plot):
    liz = xbmcgui.ListItem(name, iconImage='DefaultVideo.png', thumbnailImage=thumbnail)
    liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot})
    liz.setProperty("IsPlayable", "true")
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=liz)


def extract_var(args, var, unquote=True):
    val = args.get(var, ['', ])[0]
    if unquote:
        val = urllib.unquote(val)

    return val

