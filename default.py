import xbmcplugin
import xbmcgui
import xbmcaddon
import sys
import urllib, urllib2
import re
import showEpisode

#http://thepunkeffect.com/?s=test

addon = xbmcaddon.Addon(id='plugin.video.thepunkeffect')

thisPlugin = int(sys.argv[1])

baseLink = "http://thepunkeffect.com/"
recentLink = "http://thepunkeffect.com/?paged=1"

#3090 - The Weekly Effect
hideMenuItem = ["3090"]
hideTopicsStartWith = ["The Weekly Effect","A Jumps B Shoots"]

_regex_extractMenu = re.compile("<div id=\"nav\">(.*?)<ul class=\"quick-nav clearfix\">", re.DOTALL);

_regex_extractMenuItem = re.compile("<li id=\"menu-item-([0-9]{0,5})\" class=\".*?\"><a href=\"(.*?)\">(.*?)</a>");
_regex_extractMenuSub = re.compile('<ul class="sub-menu">');
_regex_extractMenuSubEnd = re.compile("</ul>");

_regex_extractEpisodes = re.compile('<li class=".*?">.*?<div class="entry-thumbnails"><a class="entry-thumbnails-link" href="(.*?)"><img.*?src="(.*?)".*?/></a></div><h3 class="entry-title"><a href=".*?" rel="bookmark">(.*?)</a></h3>.*?</div>(.*?)<p class="quick-read-more">', re.DOTALL)

_regex_extractShowMore = re.compile('<div class="floatleft"><a href="(.*?)" >&laquo; Older Entries</a></div>')

def mainPage():
    global thisPlugin
 
    subMenu(level1=0, level2=0)

def subMenu(level1=0, level2=0):
    global thisPlugin
    page = load_page(baseLink)
    mainMenu = extractMenu(page)
    
    if level1 == 0:
        menu = mainMenu
        
        menu_name = addon.getLocalizedString(30000)
        addDirectoryItem(menu_name, {"action" : "show", "link": recentLink})
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
    
    episodes = list(_regex_extractEpisodes.finditer(page))
    
    for episode in episodes:
        episode_link = episode.group(1)
        episode_img = episode.group(2)
        episode_title = remove_html_special_chars(episode.group(3))
        episode_teaser = remove_html_special_chars(episode.group(4).strip())
        
        showTopic = True
        for hide in hideTopicsStartWith:
            startWith = episode_title[0:len(hide)]
            if startWith == hide:
                showTopic = False
            
        if showTopic:
            addDirectoryItem(episode_title, {"action" : "episode", "link": episode_link}, episode_img, False)
    
    showMore = _regex_extractShowMore.search(page)
    if showMore is not None:
        menu_name = addon.getLocalizedString(30002)
        menu_link = showMore.group(1).replace("&#038;","&")
        addDirectoryItem(menu_name, {"action" : "show", "link": menu_link})
    
    xbmcplugin.endOfDirectory(thisPlugin)

def playEpisode(url):
    episode_page = load_page(urllib.unquote(url))
    showEpisode.showEpisode(episode_page)

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
    inputStr = inputStr.replace("&#8216;", "'")
    inputStr = inputStr.replace("&#8217;", "'")#\x92
    inputStr = inputStr.replace("&#8220;","\"")#\x92
    inputStr = inputStr.replace("&#8221;","\"")#\x92
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
    elif params['action'] == "episode":
        print "Episode"
        playEpisode(params['link'])
    else:
        mainPage()

