# -*- coding: utf-8 -*-
import urllib2,urllib,re,os
import json
from parseutils import *
from stats import *
import xbmcplugin,xbmcgui,xbmcaddon
from cookielib import MozillaCookieJar

__baseurl__ = 'https://videoarchiv.markiza.sk/'
_UserAgent_ = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0'
addon = xbmcaddon.Addon('plugin.video.markiza.sk')
profile = xbmc.translatePath(addon.getAddonInfo('profile'))
__settings__ = xbmcaddon.Addon(id='plugin.video.markiza.sk')
home = __settings__.getAddonInfo('path')
icon = xbmc.translatePath( os.path.join( home, 'icon.png' ) )
fanart = xbmc.translatePath( os.path.join( home, 'fanart.jpg' ) )
loginurl = 'https://moja.markiza.sk/'

#Nacteni informaci o doplnku
__addon__      = xbmcaddon.Addon()
__addonname__  = __addon__.getAddonInfo('name')
__addonid__    = __addon__.getAddonInfo('id')
__cwd__        = __addon__.getAddonInfo('path').decode("utf-8")
__language__   = __addon__.getLocalizedString
__set__ = __addon__.getSetting

settings = {'username': __set__('markiza_user'), 'password': __set__('markiza_pass')}
cookiepath = xbmc.translatePath("special://temp/markiza.cookies")

#handle Sectigo CA cert missing in cacerts - disable SSL checks
try:
   import ssl
   ssl._create_default_https_context = ssl._create_unverified_context
except:
   pass

def log(msg):
    xbmc.log(("### [%s] - %s" % (__addonname__.decode('utf-8'), msg.decode('utf-8'))).encode('utf-8'), level=xbmc.LOGDEBUG)

def fetchUrl(url):
    log("fetchUrl " + url)
    httpdata = ''	
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    resp = urllib2.urlopen(req)
    httpdata = resp.read()
    resp.close()
    return httpdata


def OBSAH():
    addDir('Relácie a seriály A-Z',__baseurl__ + 'relacie-a-serialy',5,icon)
    addDir('Televízne noviny',__baseurl__ + 'video/televizne-noviny',2,icon)
    addDir('TOP relácie',__baseurl__,9,icon)
    addDir('Najnovšie epizódy',__baseurl__,8,icon)
    addDir('Live Markiza',__baseurl__ + 'live/1-markiza',10,icon,IsPlayable=True)
    addDir('Live Doma',__baseurl__ + 'live/3-doma',10,icon,IsPlayable=True)
    addDir('Live Dajto',__baseurl__ + 'live/2-dajto',10,icon,IsPlayable=True)


def HOME_POSLEDNI(url):
    doc = read_page(url)

    for section in doc.findAll('section', 'b-main-section'):
        if section.div.h3 and section.div.h3.getText(" ").encode('utf-8') == 'NAJNOVŠIE EPIZÓDY':
            for article in section.findAll('article'):
                url = article.a['href'].encode('utf-8')
                title = article.a.find('div', {'class': 'e-info'}).getText(" ").encode('utf-8')
                thumb = article.a.div.img['data-original'].encode('utf-8')
                addDir(title,url,3,thumb)

def HOME_TOPPORADY(url):
    doc = read_page(url)

    for section in doc.findAll('section', 'b-main-section my-5'):
        if section.div.h3.getText(" ").encode('utf-8') == 'TOP RELÁCIE':
            for article in section.findAll('article'):
                url = article.a['href'].encode('utf-8')
                title = article.a['title'].encode('utf-8')
                thumb = article.a.div.img['data-original'].encode('utf-8')
                addDir(title,url,2,thumb)

def CATEGORIES(url):
    print 'CATEGORIES *********************************' + str(url)
    doc = read_page(url)

    for article in doc.findAll('article'):
        url = article.a['href'].encode('utf-8')
        title = article.a['title'].encode('utf-8')
        thumb = article.a.div.img['data-original'].encode('utf-8')
        addDir(title,url,2,thumb)

def EPISODES(url):
    print 'EPISOD9ES *********************************' + str(url)
    try:
        doc = read_page(url)
    except urllib2.HTTPError:
        xbmcgui.Dialog().ok('Chyba', 'CHYBA 404: STRÁNKA NEBOLA NÁJDENÁ', '', '')
        return False

    for article in doc.findAll('article', 'b-article b-article-text b-article-inline'):
        url = article.a['href'].encode('utf-8')
        title = article.a.find('div', {'class': 'e-info'}).getText(" ").encode('utf-8').strip() 
        thumb = article.a.div.img['data-original'].encode('utf-8')
        addDir(title,url,3,thumb)

    for section in doc.findAll('section', 'b-main-section'):
        if section.div.h3.getText(" ").encode('utf-8') == 'Celé epizódy':
            for article in section.findAll('article'):
                url = article.a['href'].encode('utf-8')
                if (article.a.find('div', {'class': 'e-date'})):
                   title = 'Celé epizódy - ' + article.a.find('div', {'class': 'e-info'}).getText(" ").encode('utf-8')
                else:
                   title = 'Celé epizódy - ' + article.a['title'].encode('utf-8')
                thumb = article.a.div.img['data-original'].encode('utf-8')
                addDir(title,url,3,thumb)

        if section.div.h3.getText(" ").encode('utf-8') == 'Mohlo by sa vám páčiť':
            for article in section.findAll('article'):
                url = article.a['href'].encode('utf-8')
                title = 'Mohlo by sa vám páčiť - ' + article.a.find('div', {'class': 'e-info'}).getText(" ").encode('utf-8') 
                thumb = article.a.div.img['data-original'].encode('utf-8')
                addDir(title,url,3,thumb)

        if section.div.h3.getText(" ").encode('utf-8') == 'Zo zákulisia':
            for article in section.findAll('article'):
                url = article.a['href'].encode('utf-8')
                title = 'Zo zákulisia - ' + article.a['title'].encode('utf-8')
                thumb = article.a.div.img['data-original'].encode('utf-8')
                addDir(title,url,3,thumb)
                
def VIDEOLINK(url):
    print 'VIDEOLINK *********************************' + str(url)

    doc = read_page(url)
    main = doc.find('main')
    if (not main.find('iframe')):
       xbmcgui.Dialog().ok('Chyba', 'Platnost tohoto videa už vypršala', '', '')
       return False
    url = main.find('iframe')['src']
    httpdata = fetchUrl(url)
    httpdata = httpdata.replace("\r","").replace("\n","").replace("\t","")
    if '<title>Error</title>' in httpdata:
        error=re.search('<h2 class="e-title">(.*?)</h2>', httpdata).group(1) #Video nie je dostupné vo vašej krajine
        xbmcgui.Dialog().ok('Chyba', error, '', '')
        return False

    #url = re.search('src = {\s*\"hls\": [\'\"](.+?)[\'\"]\s*};', httpdata)
    url = re.search('\"HLS\":\[{\"src\":\"(.+?)\"', httpdata)
    url=url.group(1).replace('\/','/')
     
    thumb = re.search('<meta property="og:image" content="(.+?)">', httpdata)
    thumb = thumb.group(1) if thumb else ''
    name = re.search('<meta property="og:title" content="(.+?)">', httpdata)
    name = name.group(1) if name else '?'
    desc = re.search('<meta name="description" content="(.+?)">', httpdata)
    desc = desc.group(1) if desc else name

    httpdata = fetchUrl(url)

    streams = re.compile('RESOLUTION=\d+x(\d+).*\n([^#].+)').findall(httpdata) 
    url = url.rsplit('/', 1)[0] + '/'
    streams.sort(key=lambda x: int(x[0]),reverse=True)
    for (bitrate, stream) in streams:
        bitrate=' [' + bitrate + 'p]'
        addLink(name + bitrate,url + stream,thumb,desc)


def LIVE(url, relogin=False):
    if not (settings['username'] and settings['password']):
        xbmcgui.Dialog().ok('Chyba', 'Nastavte prosím moja.markiza.sk konto', '', '')
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, xbmcgui.ListItem())
        raise RuntimeError
    cj = MozillaCookieJar()	
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    if not relogin:
       try:
          cj.load(cookiepath)
       except IOError:
          relogin=True
    if relogin:
       response = opener.open(loginurl).read()
       token = re.search(r'name=\"_token_\" value=\"(\S+?)\">',response).group(1)
       logindata = urllib.urlencode({'email': settings['username'], 'password': settings['password'], '_token_': token, '_do': 'content1-loginForm-form-submit' }) + '&login=Prihl%C3%A1si%C5%A5+sa'
       opener.open(loginurl, logindata)
       log('Saving cookies') 
       cj.save(cookiepath)
   
    response = opener.open(url).read()
    link = re.search(r'<iframe src=\"(\S+?)\"',response).group(1) #https://videoarchiv.markiza.sk/api/v1/user/live
    link = link.replace('&amp;','&')    
    response = opener.open(link).read()
    if '<iframe src=\"' not in response:   #handle expired cookies
       if relogin:
          xbmcgui.Dialog().ok('Chyba', 'Skontrolujte prihlasovacie údaje', '', '')
          raise RuntimeError # loop protection
       else:
          LIVE(url, relogin=True) 
          return
    opener.addheaders = [('Referer',link)]
    link = re.search(r'<iframe src=\"(\S+?)\"',response).group(1) #https://media.cms.markiza.sk/embed/
    response = opener.open(link).read()
    if '<title>Error</title>' in response:
        error=re.search('<h2 class="e-title">(.*?)</h2>', response).group(1) #Video nie je dostupné vo vašej krajine
        xbmcgui.Dialog().ok('Chyba', error, '', '')
        raise RuntimeError 
    link = re.search(r'\"hls\": \"(\S+?)\"',response).group(1) #https://h1-s6.c.markiza.sk/hls/markiza-sd-master.m3u8
    response = opener.open(link).read()
    
    cookies='|Cookie='
    for cookie in cj:
      cookies+=cookie.name+'='+cookie.value+';'
    cookies=cookies[:-1]
    play_item = xbmcgui.ListItem(path=link+cookies)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=play_item)
	
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]

        return param

def addLink(name,url,iconimage,popis):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": popis} )
        liz.setProperty( "Fanart_Image", fanart )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage, IsPlayable=False):
        if ("voyo.markiza.sk" in url):
           return False 
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty( "Fanart_Image", fanart )
        liz.setProperty('IsPlayable', ('True' if IsPlayable else 'False'))
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=(False if IsPlayable else True))
        return ok

params=get_params()
url=None
name=None
thumb=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if mode==None or url==None or len(url)<1:
        STATS("OBSAH", "Function")
        OBSAH()

elif mode==8:
        STATS("HOME_POSLEDNI", "Function")
        HOME_POSLEDNI(url)

elif mode==9:
        STATS("HOME_TOPPORADY", "Function")
        HOME_TOPPORADY(url)

elif mode==5:
        STATS("CATEGORIES", "Function")
        CATEGORIES(url)

elif mode==2:
        STATS("EPISODES", "Function")
        EPISODES(url)

elif mode==3:
        STATS("VIDEOLINK", "Function")
        VIDEOLINK(url)

elif mode==10:
        STATS("LIVE", "Function")
        LIVE(url)


xbmcplugin.endOfDirectory(int(sys.argv[1]))
