# -*- coding: utf-8 -*-

'''
    atv_hu Add-on
    Copyright (C) 2023 heg, vargalex

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os, sys, re, xbmc, xbmcgui, xbmcplugin, xbmcaddon, locale, base64
from bs4 import BeautifulSoup
import requests
import urllib.parse
import resolveurl as urlresolver
from resources.lib.modules.utils import py2_decode, py2_encode
import html
import random

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])
addonFanart = xbmcaddon.Addon().getAddonInfo('fanart')

version = xbmcaddon.Addon().getAddonInfo('version')
kodi_version = xbmc.getInfoLabel('System.BuildVersion')

base_log_info = f'atv.hu | v{version} | Kodi: {kodi_version[:5]}'

xbmc.log(f'{base_log_info}', xbmc.LOGINFO)

base_url = 'https://atv.hu'

BR_VERS = [
    ['%s.0' % i for i in range(18, 43)],
    ['61.0.3163.79', '61.0.3163.100', '62.0.3202.89', '62.0.3202.94', '63.0.3239.83', '63.0.3239.84', '64.0.3282.186', '65.0.3325.162', '65.0.3325.181', '66.0.3359.117', '66.0.3359.139',
     '67.0.3396.99', '68.0.3440.84', '68.0.3440.106', '68.0.3440.1805', '69.0.3497.100', '70.0.3538.67', '70.0.3538.77', '70.0.3538.110', '70.0.3538.102', '71.0.3578.80', '71.0.3578.98',
     '72.0.3626.109', '72.0.3626.121', '73.0.3683.103', '74.0.3729.131'],
    ['11.0']]
WIN_VERS = ['Windows NT 10.0', 'Windows NT 7.0', 'Windows NT 6.3', 'Windows NT 6.2', 'Windows NT 6.1']
FEATURES = ['; WOW64', '; Win64; IA64', '; Win64; x64', '']
RAND_UAS = ['Mozilla/5.0 ({win_ver}{feature}; rv:{br_ver}) Gecko/20100101 Firefox/{br_ver}',
            'Mozilla/5.0 ({win_ver}{feature}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{br_ver} Safari/537.36',
            'Mozilla/5.0 ({win_ver}{feature}; Trident/7.0; rv:{br_ver}) like Gecko']

ind_ex = random.randrange(len(RAND_UAS))
r_u_a = RAND_UAS[ind_ex].format(win_ver=random.choice(WIN_VERS), feature=random.choice(FEATURES), br_ver=random.choice(BR_VERS[ind_ex]))

headers = {
    'authority': 'api.atv.hu',
    'accept': 'application/json, text/plain, */*',
    'origin': 'https://www.atv.hu',
    'referer': 'https://www.atv.hu/',
    'user-agent': r_u_a,
}

if sys.version_info[0] == 3:
    from xbmcvfs import translatePath
    from urllib.parse import urlparse, quote_plus
else:
    from xbmc import translatePath
    from urlparse import urlparse
    from urllib import quote_plus

class navigator:
    def __init__(self):
        try:
            locale.setlocale(locale.LC_ALL, "hu_HU.UTF-8")
        except:
            try:
                locale.setlocale(locale.LC_ALL, "")
            except:
                pass
        self.base_path = py2_decode(translatePath(xbmcaddon.Addon().getAddonInfo('profile')))      

    def root(self):
        self.addDirectoryItem("Műsorok", f"get_musorok&url={base_url}/musorok", '', 'DefaultFolder.png')
        self.addDirectoryItem("Videók", f"get_videok", '', 'DefaultFolder.png')
        self.addDirectoryItem("Élő", f"play_live&url=https://streamservers.atv.hu/atvliveedge/_definst_/atvstream_2_aac/playlist.m3u8", '', 'DefaultFolder.png', isFolder=False)

        self.endDirectory()

    def getMusorok(self, url, image_url, full_title, content):
        html_source = requests.get(url, headers=headers)
        soup = BeautifulSoup(html_source.text, 'html.parser')
        
        shows = soup.find_all('div', class_='show')
        
        idojaras_data = {
            "musor_title": "Időjárás",
            "musor_link": base_url + "/musor/idojaras",
            "content": "Időjárás jelentések..",
            "img_src": ""
        }
        
        shows_data = [idojaras_data]
        
        exclude_this = [
            re.compile(r'.*/500.*'),
            re.compile(r'.*/aradivarga-show.*'),
            re.compile(r'.*/bochkor.*'),
            re.compile(r'.*/hit-es-elet.*'),
            re.compile(r'.*/huzos.*'),
            re.compile(r'.*/jakupcsek-night.*'),
            re.compile(r'.*/magyarorszag-segit.*'),
            re.compile(r'.*/mondd-el-tatar-csillanak.*'),
            re.compile(r'.*/sorok-kozott-lutter-imrevel.*'),
            re.compile(r'.*/sznobjektiv.*'),
            re.compile(r'.*/vidam-vasarnap.*'),
            re.compile(r'.*/vilaghirado.*'),
            re.compile(r'.*/visszajatszas.*'),
        ]
        
        for show in shows:
            musor_title = show.find('h2').text.strip()
            musor_link = base_url + show.find('a')['href'].replace("\n", " ")
        
            if any(pattern.match(musor_link) for pattern in exclude_this):
                continue
        
            content = show.find('div', class_='lead').text.strip()

            img_src = show.find('img')['src']
        
            shows_data.append({
                "musor_title": musor_title,
                "musor_link": musor_link,
                "content": content,
                "img_src": img_src
            })
        
        for show_data in shows_data:
            full_title = show_data['musor_title']
            sh_musor_link = show_data['musor_link']
            content = show_data['content']
            image_url = show_data['img_src']

            self.addDirectoryItem(f'[B]{full_title}[/B]', f'ext_musorok&url={quote_plus(sh_musor_link)}&image_url={image_url}&full_title={full_title}&content={content}', image_url, 'DefaultMovies.png', isFolder=True, meta={'title': full_title, 'plot': content})    
    
        self.endDirectory('movies')    

    def extMusorok(self, url, image_url, full_title):

        import requests
        from urllib.parse import quote
        import re
        
        headers = {
            'authority': 'api.atv.hu',
            'accept': 'application/json, text/plain, */*',
            'origin': 'https://www.atv.hu',
            'referer': 'https://www.atv.hu/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        }
        
        resp_00 = requests.get(url, headers=headers).text
        
        show_id = re.findall(r',(\b\d{6,7}\b).*?\"without_restrictions\"', str(resp_00))[0].strip()
        
        params = {
            'limit': '2000',
            'showId': show_id,
        }
        
        response = requests.get('https://api.atv.hu/cms/video/all-published', params=params, headers=headers).json()
        
        all_content = response['pager']['count']
        
        def clean_html_tags(description):
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(description, 'html.parser')
            cleaned_text = soup.get_text(separator=' ', strip=True)
            return cleaned_text        
        
        for stuffs in response['videos']:
            name = stuffs['name']
        
            posterKey = stuffs['posterKey']
            fixed_poster_link = 'https://media.atv.hu/' + quote(posterKey, safe=':/')
        
            descr_with_tags = stuffs['description']
            
            description = clean_html_tags(descr_with_tags)
        
            m3u8_link = 'https://streamservers.atv.hu/mediacache/_definst_/mp4:atv/' + stuffs['path'] + '/playlist.m3u8'

            self.addDirectoryItem(f'[B]{name}[/B]', f'play_movie&url={m3u8_link}&image_url={fixed_poster_link}&full_title={name}', fixed_poster_link, 'DefaultMovies.png', isFolder=False, meta={'title': name, 'plot': f"{description}"})

        self.endDirectory('movies')

    def getVideok(self, url, image_url, full_title, content):
        
        import requests
        from urllib.parse import quote
        
        headers = {
            'authority': 'api.atv.hu',
            'accept': 'application/json, text/plain, */*',
            'origin': 'https://www.atv.hu',
            'referer': 'https://www.atv.hu/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        }
        
        params = {
            'limit': '2000',
        }
        
        response = requests.get('https://api.atv.hu/cms/video/all-published', params=params, headers=headers).json()
        
        def clean_html_tags(description):
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(description, 'html.parser')
            cleaned_text = soup.get_text(separator=' ', strip=True)
            return cleaned_text        
        
        for stuffs in response['videos']:
            name = stuffs['name']
        
            posterKey = stuffs['posterKey']
            fixed_poster_link = 'https://media.atv.hu/' + quote(posterKey, safe=':/')
        
            descr_with_tags = stuffs['description']
            
            description = clean_html_tags(descr_with_tags)
        
            m3u8_link = 'https://streamservers.atv.hu/mediacache/_definst_/mp4:atv/' + stuffs['path'] + '/playlist.m3u8'

            self.addDirectoryItem(f'[B]{name}[/B]', f'play_movie&url={m3u8_link}&image_url={fixed_poster_link}&full_title={name}', fixed_poster_link, 'DefaultMovies.png', isFolder=False, meta={'title': name, 'plot': f"{description}"})        

        
        self.endDirectory('movies')

    def playMovie(self, url, image_url, full_title):
        
        xbmc.log(f'{base_log_info}| playMovie | url: {url}', xbmc.LOGINFO)
        
        play_item = xbmcgui.ListItem(path=url)
        from inputstreamhelper import Helper
        is_helper = Helper('hls')
        if is_helper.check_inputstream():
        
            play_item.setProperty('inputstream', 'inputstream.adaptive')  # compatible with recent builds Kodi 19 API
            
            try:
                play_item.setProperty('inputstream.adaptive.stream_headers', url.split("|")[1])
                play_item.setProperty('inputstream.adaptive.manifest_headers', url.split("|")[1])
            except:
                pass
            
            play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
        
        xbmcplugin.setResolvedUrl(syshandle, True, listitem=play_item)

    def playLive(self, url):
        
        play_item = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(syshandle, True, listitem=play_item)

    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True, Fanart=None, meta=None, banner=None):
        url = f'{sysaddon}?action={query}' if isAction else query
        if thumb == '':
            thumb = icon
        cm = []
        if queue:
            cm.append((queueMenu, f'RunPlugin({sysaddon}?action=queueItem)'))
        if not context is None:
            cm.append((context[0].encode('utf-8'), f'RunPlugin({sysaddon}?action={context[1]})'))
        item = xbmcgui.ListItem(label=name)
        item.addContextMenuItems(cm)
        item.setArt({'icon': thumb, 'thumb': thumb, 'poster': thumb, 'banner': banner})
        if Fanart is None:
            Fanart = addonFanart
        item.setProperty('Fanart_Image', Fanart)
        if not isFolder:
            item.setProperty('IsPlayable', 'true')
        if not meta is None:
            item.setInfo(type='Video', infoLabels=meta)
        xbmcplugin.addDirectoryItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)

    def endDirectory(self, type='addons'):
        xbmcplugin.setContent(syshandle, type)
        xbmcplugin.endOfDirectory(syshandle, cacheToDisc=True)  