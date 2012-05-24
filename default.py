import xbmcplugin
import xbmcgui
import xbmcaddon
import sys
import urllib, urllib2
import re

addon = xbmcaddon.Addon(id='plugin.video.thepunkeffect')

thisPlugin = int(sys.argv[1])
baseLink = "http://thepunkeffect.com/"

#3090 - The Weekly Effect
hideMenuItem = ["3090"]

_regex_extractMenu = re.compile("<div id=\"nav\">(.*?)<ul class=\"quick-nav clearfix\">", re.DOTALL);

_regex_extractMenuItem = re.compile("<li id=\"menu-item-([0-9]{0,5})\" class=\".*?\"><a href=\"(.*?)\">(.*?)</a>");
_regex_extractMenuSub = re.compile('<ul class="sub-menu">');
_regex_extractMenuSubEnd = re.compile("</ul>");

_regex_extractEpisodes = re.compile('<li class=".*?">.*?<div class="entry-thumbnails"><a class="entry-thumbnails-link" href="(.*?)"><img.*?src="(.*?)".*?/></a></div><h3 class="entry-title"><a href=".*?" rel="bookmark">(.*?)</a></h3>.*?</div>(.*?)<p class="quick-read-more">', re.DOTALL)
_regex_extractEpisodeBlipTv = re.compile("(http://blip.tv/play/.*?)(.html|\")");
_regex_extractEpisodeYouTubeId = re.compile("http://www.youtube.com/(embed|v)/(.*?)(\"|\?|\ |&)");
_regex_extractEpisodeDorkly = re.compile("http://www.dorkly.com/(e/|moogaloop/noobtube.swf\?clip_id=)([0-9]*)")
_regex_extractEpisodeSpringboard = re.compile("\.springboardplatform\.com/mediaplayer/springboard/video/(.*?)/(.*?)/(.*?)/")

_regex_extractEpisodeDorklyVideo = re.compile("<file><!\[CDATA\[(.*?)\]\]></file>")

_regex_extractVideoSpringboardStream = re.compile("<media:content duration=\"[0-9]*?\" medium=\"video\" bitrate=\"[0-9]*?\" fileSize=\"[0-9]*?\" url=\"(.*?)\" type=\".*?\" />");

#blip.tv
_regex_extractVideoFeedURL = re.compile("file=(.*?)&", re.DOTALL);
_regex_extractVideoFeedURL2 = re.compile("file=(.*)", re.DOTALL);

def mainPage():
    global thisPlugin
 
    subMenu(level1=0, level2=0)

def subMenu(level1=0, level2=0):
    global thisPlugin
    page = load_page(baseLink)
    mainMenu = extractMenu(page)
    
    if level1 == 0:
        menu = mainMenu
    elif level2 == 0:
        menu = mainMenu[int(level1)]['children']
    else:
        menu = mainMenu[int(level1)]['children'][int(level2)]['children']
    
    counter = 0
    for menuItem in menu:
        menu_name = remove_html_special_chars(menuItem['name']);
        
        menu_link = menuItem['link'];
        if len(menuItem['children']) and level1 == 0:
            addDirectoryItem(menu_name, {"action" : "submenu", "link": counter})  
        elif len(menuItem['children']):
            addDirectoryItem(menu_name, {"action" : "subsubmenu", "link": level1 + ";" + str(counter)})  
        else:        
            addDirectoryItem(menu_name, {"action" : "show", "link": menu_link})
        counter = counter + 1
    xbmcplugin.endOfDirectory(thisPlugin)
    
def extractMenu(page):
    menu = _regex_extractMenu.search(page).group(1);
    menuList = []
    
    sub = 0
    parent = -1;
    for line in menu.split("\n"):
        #print line
        if _regex_extractMenuSub.search(line) is not None:
            sub = sub + 1
        if _regex_extractMenuSubEnd.search(line) is not None:
            sub = sub - 1
        menuItem = _regex_extractMenuItem.search(line)
        if menuItem is not None:
            if not menuItem.group(1) in hideMenuItem:
                print menuItem.group(1)
                if sub == 0:
                    parent = parent + 1
                    parent2 = -1
                    menuList.append({"name" : menuItem.group(3), "link" : menuItem.group(2), "children" : []})
                elif sub == 1:
                    parent2 = parent2 + 1
                    menuList[parent]['children'].append({"name" : menuItem.group(3), "link" : menuItem.group(2), "children" : []});
                elif sub == 2:
                    menuList[parent]['children'][parent2]['children'].append({"name" : menuItem.group(3), "link" : menuItem.group(2), "children" : []});
    return menuList

def showPage(link):
    global thisPlugin
    page = load_page(urllib.unquote(link))
    
    #print page
    
    episodes = list(_regex_extractEpisodes.finditer(page))
    
    for episode in episodes:
        episode_link = episode.group(1)
        episode_img = episode.group(2)
        episod_title = remove_html_special_chars(episode.group(3))
        episode_teaser = remove_html_special_chars(episode.group(4).strip())

        addDirectoryItem(episod_title, {"action" : "episode", "link": episode_link}, episode_img, False)
    xbmcplugin.endOfDirectory(thisPlugin)
    

def showEpisodeBip(url):    
    #GET the 301 redirect URL
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    fullURL = response.geturl()
    
    feedURL = _regex_extractVideoFeedURL.search(fullURL)
    if feedURL is None:
        feedURL = _regex_extractVideoFeedURL2.search(fullURL)
    feedURL = urllib.unquote(feedURL.group(1))
    
    blipId = feedURL[feedURL.rfind("/") + 1:]
    
    stream_url = "plugin://plugin.video.bliptv/?action=play_video&videoid=" + blipId
    item = xbmcgui.ListItem(path=stream_url)
    return xbmcplugin.setResolvedUrl(thisPlugin, True, item)

def showEpisodeYoutube(youtubeID):
    stream_url = "plugin://plugin.video.youtube/?action=play_video&videoid=" + youtubeID
    item = xbmcgui.ListItem(path=stream_url)
    xbmcplugin.setResolvedUrl(thisPlugin, True, item)
    return False

def showEpisodeDorkly(dorklyID):
    feedUrl = "http://www.dorkly.com/moogaloop/video/"+dorklyID
    feedPage = load_page(feedUrl)
    videoItem = _regex_extractEpisodeDorklyVideo.search(feedPage)
    if videoItem is not None:
        stream_url = videoItem.group(1)
        item = xbmcgui.ListItem(path=stream_url)
        xbmcplugin.setResolvedUrl(thisPlugin, True, item)
    return False
    
def showEpisodeSpringboard(videoItem):
    siteId = videoItem.group(2)
    contentId = videoItem.group(3)
    feedUrl = "http://cms.springboard.gorillanation.com/xml_feeds_advanced/index/" + siteId + "/rss3/" + contentId + "/"
    feed = load_page(feedUrl)
    feedItem = _regex_extractVideoSpringboardStream.search(feed);
    stream_url = feedItem.group(1)
    item = xbmcgui.ListItem(path=stream_url)
    xbmcplugin.setResolvedUrl(thisPlugin, True, item)
    return False

def showEpisode(link):
    episode_page = load_page(urllib.unquote(link))

    videoItem = _regex_extractEpisodeBlipTv.search(episode_page)
    if videoItem is not None:
        videoLink = videoItem.group(1)
        showEpisodeBip(videoLink)
    else:
        videoItem = _regex_extractEpisodeYouTubeId.search(episode_page)
        if videoItem is not None:
            youTubeId = videoItem.group(2)
            showEpisodeYoutube(youTubeId)
        else:
            videoItem = _regex_extractEpisodeDorkly.search(episode_page)
            if videoItem is not None:
                dorklyID = videoItem.group(2)
                showEpisodeDorkly(dorklyID)
            else:
                videoItem = _regex_extractEpisodeSpringboard.search(episode_page)
                if videoItem is not None:
                    showEpisodeSpringboard(videoItem);

def load_page(url):
    print url
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link

def addDirectoryItem(name, parameters={}, pic="", folder=True):
    li = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=pic)
    if not folder:
        li.setProperty('IsPlayable', 'true')
    url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

def remove_html_special_chars(inputStr):
    inputStr = inputStr.replace("&#8211;", "-")
    inputStr = inputStr.replace("&#8217;", "'")#\x92
    inputStr = inputStr.replace("&#8230;", "'")
    inputStr = inputStr.replace("&#039;", chr(39))# '
    inputStr = inputStr.replace("&#038;", chr(38))# &
    return inputStr
    
def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    
    return param
    
if not sys.argv[2]:
    mainPage()
else:
    params = get_params()
    if params['action'] == "show":
        showPage(params['link'])
    elif params['action'] == "submenu":
        subMenu(params['link'])
    elif params['action'] == "subsubmenu":
        levels = urllib.unquote(params['link']).split(";")
        subMenu(levels[0], levels[1])
    elif params['action'] == "recent":
        recentPage()
    elif params['action'] == "episode":
        print "Episode"
        showEpisode(params['link'])
    else:
        mainPage()

