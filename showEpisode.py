#v 0.0.2
import re
import xbmcplugin
import xbmcgui
import sys
import urllib, urllib2
try:
    import urlresolver
except:
    print "No urlresolver"

thisPlugin = int(sys.argv[1])

def showEpisode(episode_page):
    
    providers = (
        {"function":showEpisodeBip, "regex":"(http://blip.tv/play/.*?)(.html|\")"},
        {"function":showEpisodeYoutube, "regex":"http://www.youtube.com/(embed|v)/(.*?)(\"|\?|\ |&)"},
        {"function":showEpisodeDorkly, "regex":"http://www.dorkly.com/(e/|moogaloop/noobtube.swf\?clip_id=)([0-9]*)"},
        {"function":showEpisodeSpringboard, "regex":"\.springboardplatform\.com/mediaplayer/springboard/video/(.*?)/(.*?)/(.*?)/"},
        {"function":showEpisodeSpringboard, "regex":"\\$sb\\(\"(.*?)\",{\"sbFeed\":{\"partnerId\":(.*?),\"type\":\"video\",\"contentId\":(.*?),\"cname\":\"(.*?)\"},\"style\":{\"width\":.*?,\"height\":.*?}}\\);"},
        {"function":showEpisodeSpringboardBitLy, "regex":"<script.*?src=\"http://www.springboardplatform.com/js/overlay\".*? id=\".*?\".*?src=\"(.*?)\".*?</iframe>"},
        #http://thepunkeffect.com/?p=5830
        {"function":showEpisodeYoutube, "regex":"\\$sb\\(\"(.*?)\",{\"sbFeed\":{\"partnerId\":.*?,\"type\":\"youtube\",\"contentId\":\"(.*?)\",\"cname\":\"(.*?)\"},\"style\":{\"width\":.*?,\"height\":.*?}}\\);"},
        {"function":showEpisodeYoutube, "regex":"\.springboardplatform\.com/mediaplayer/springboard/youtube/(.*?)/(.*?)/"}, 
        {"function":showEpisodeDaylimotion, "regex":"(http://www.dailymotion.com/video/.*?)_"},          
        {"function":showEpisodeGametrailers, "regex":"<a href=\"(http://www.gametrailers.com/video/angry-video-screwattack/(.*))\" target=\"_blank\">"},
        #http://cinemassacre.com/2012/07/07/mortal-kombat-memories/
        {"function":showEpisodeGametrailers2, "regex":"<a href=\"(http://www.gametrailers.com/videos/.*/.*?)\" target=\"_blank\">"},
        {"function":showEpisodeSpike, "regex":"<a href=\"(http://www.spike.com/.*?)\""},
        #http://thepunkeffect.com/?p=5639
        #http://thepunkeffect.com/?p=4217
        {"function":showEpisodePlaywire, "regex":"<iframe src=\"(http://cdn.playwire.com/(.*)/embed/(.*).html)\""},
        #http://cdn.playwire.com/11043/embed/80834.html
        {"function":showKickstarter, "regex":"http://www.kickstarter.com/projects/.*/widget/video.html"},
        #http://thepunkeffect.com/?p=1690
        {"function":showEpisodeSpringboardEncrypted, "regex":"<param name=\"movie\" value=\"http://cdn.springboard.gorillanation.com/storage/xplayer/yo033.swf\"><param name=\"flashvars\" value=\"e=(.*?)&#038;"},
        #http://thepunkeffect.com/?p=5966
        {"function":showEpisodeTeamcoco, "regex":"http://teamcoco.com/embed/v/([0-9]*)"},
        #http://thepunkeffect.com/?p=4930
        {"function":showEpisodeCollegeHumor,"regex":"http://www.collegehumor.com/e/([0-9]*)"}
    )
    
    for provider in providers:
        regex = re.compile(provider['regex'])
        videoItem = regex.search(episode_page)
        if videoItem is not None:
            return provider['function'](videoItem)

def showKickstarter(videoItem):
    url = videoItem.group(0)
    page = showEpisodeLoadPage(url)
    
    stream_url = re.compile("file=(.*?)&amp;").search(page).group(1)
    stream_url = urllib.unquote(stream_url)
    
    item = xbmcgui.ListItem(path=stream_url)
    return xbmcplugin.setResolvedUrl(thisPlugin, True, item)

def showEpisodePlaywire(videoItem):
    configUrl = "http://cdn.playwire.com/%s/embed/%s.xml"%(videoItem.group(2),videoItem.group(3))
    page = showEpisodeLoadPage(configUrl)
    
    f4mUrl = re.compile("<src>(.*?)</src>").search(page).group(1)#http://cdn.playwire.com/11043/hd-80834.f4m
    
    page = showEpisodeLoadPage(f4mUrl)
    
    baseUrl = re.compile("<baseURL>(.*?)</baseURL>").search(page).group(1)
    mediaUrls = re.compile("<media.*?url=\"(.*?)\".*?height=\"([0-9]*).*?/>")
    
    height = 0
    for mediaUrl in mediaUrls.finditer(page):
        print int(mediaUrl.group(2))
        if height < int(mediaUrl.group(2)):
            height = int(mediaUrl.group(2))
            playPath = mediaUrl.group(1)
    
    stream_url = baseUrl + ' playpath=' + playPath
    item = xbmcgui.ListItem(path=stream_url)
    return xbmcplugin.setResolvedUrl(thisPlugin, True, item)

    
def showEpisodeBip(videoItem):
    _regex_extractVideoFeedURL = re.compile("file=(.*?)&", re.DOTALL);
    _regex_extractVideoFeedURL2 = re.compile("file=(.*)", re.DOTALL);
    _regex_extractVideoFeedURL3 = re.compile("data-episode-id=\"(.*?)\"", re.DOTALL);

    videoLink = videoItem.group(1)
    
    #GET the 301 redirect URL
    req = urllib2.Request(videoLink)
    response = urllib2.urlopen(req)
    fullURL = response.geturl()
    
    feedURL = _regex_extractVideoFeedURL.search(fullURL)
    if feedURL is None:
        feedURL = _regex_extractVideoFeedURL2.search(fullURL)
    
    if feedURL is None:
        page = showEpisodeLoadPage(videoLink) 
        blipId = _regex_extractVideoFeedURL3.search(page).group(1)
    else:#This still needed for older links
        feedURL = urllib.unquote(feedURL.group(1))
        blipId = feedURL[feedURL.rfind("/") + 1:]
    
    stream_url = "plugin://plugin.video.bliptv/?action=play_video&videoid=" + blipId
    item = xbmcgui.ListItem(path=stream_url)
    return xbmcplugin.setResolvedUrl(thisPlugin, True, item)

def showEpisodeYoutube(videoItem):
    youTubeId = videoItem.group(2)
    stream_url = "plugin://plugin.video.youtube/?action=play_video&videoid=" + youTubeId
    item = xbmcgui.ListItem(path=stream_url)
    xbmcplugin.setResolvedUrl(thisPlugin, True, item)
    return False

def showEpisodeDorkly(videoItem):
    _regex_extractEpisodeDorklyVideo = re.compile("<file><!\[CDATA\[(.*?)\]\]></file>")
    
    dorklyID = videoItem.group(2)
    
    feedUrl = "http://www.dorkly.com/moogaloop/video/" + dorklyID
    feedPage = showEpisodeLoadPage(feedUrl)
    videoItem = _regex_extractEpisodeDorklyVideo.search(feedPage)
    if videoItem is not None:
        stream_url = videoItem.group(1)
        item = xbmcgui.ListItem(path=stream_url)
        xbmcplugin.setResolvedUrl(thisPlugin, True, item)
    return False
    
def showEpisodeSpringboard(videoItem):
    _regex_extractVideoSpringboardStream = re.compile("<media:content duration=\"[0-9]*?\" medium=\"video\" bitrate=\"[0-9]*?\" fileSize=\"[0-9]*?\" url=\"(.*?)\" type=\".*?\" />");
    
    siteId = videoItem.group(2)
    contentId = videoItem.group(3)
    feedUrl = "http://cms.springboard.gorillanation.com/xml_feeds_advanced/index/" + siteId + "/rss3/" + contentId + "/"

    req = urllib2.Request(feedUrl)
    response = urllib2.urlopen(req)
    feed = response.read()
    response.close()

    feedItem = _regex_extractVideoSpringboardStream.search(feed);
    stream_url = feedItem.group(1)
    item = xbmcgui.ListItem(path=stream_url)
    xbmcplugin.setResolvedUrl(thisPlugin, True, item)
    return False

def showEpisodeSpringboardEncrypted(videoItem):
    data = videoItem.group(1).decode("hex")
    key = "sPr1ngB0@rd"
    
    #RC4 - http://de.wikipedia.org/wiki/RC4
    L = len(key)
    s = []
    for i in range(256):
        s.append(i)
    j = 0
    for i in range(256):
        j = (j + s[i] + ord(key[i % L])) % 256
        s[i], s[j] = s[j], s[i]
    
    schl = ""
    X = len(data)
    i, j = 0, 0
    for n in range(X):
        i = (i + 1) % 256
        j = (j + s[i]) % 256
        s[i], s[j] = s[j], s[i]
        zufallszahl = s[(s[i] + s[j]) % 256]
        schl = schl + chr(zufallszahl ^ ord(data[n]))
        
        
    #http://cms.springboard.gorillanation.com/xml_feeds_advanced/index/71/3/272521/0/0/0/0/0/0/0/
    videoItem = re.compile("(.*?)/index/(.*?)/.*?/(.*?)/.*?").search(schl)
    return showEpisodeSpringboard(videoItem)

def showEpisodeSpringboardBitLy(videoItem):
    videoLink = videoItem.group(1)
    #GET the 301 redirect URL
    req = urllib2.Request(videoLink)
    response = urllib2.urlopen(req)
    fullURL = response.geturl()
    
    _regex_extractVideoSpringboard = re.compile("(embed_iframe)/(.*?)/video/(.*?)/(.*?)/.*?")
    
    videoItem = _regex_extractVideoSpringboard.search(fullURL)
    
    return showEpisodeSpringboard(videoItem)

def showEpisodeDaylimotion(videoItem):
    url = videoItem.group(1)
    stream_url = urlresolver.resolve(url)
    item = xbmcgui.ListItem(path=stream_url)
    xbmcplugin.setResolvedUrl(thisPlugin, True, item)
    return False

def showEpisodeGametrailers2(videoItem):
    page = showEpisodeLoadPage(videoItem.group(1))
    
    extractMgid = re.compile("data-mgid=\"(.*?)\"")
    
    mgid = extractMgid.search(page).group(1)
    
    urlXml1 = "http://www.gametrailers.com/feeds/mrss?uri="+mgid
    showEpisodeGametrailers(None,urlXml=urlXml1)

def showEpisodeGametrailers(videoItem,urlXml=None):
    _regex_extractVideoGametrailersXML = re.compile("<media:content type=\"text/xml\" medium=\"video\".*?url=\"(.*?)\"")
    _regex_extractVideoGametrailersStreamURL = re.compile("<src>(.*?)</src>")

    if urlXml is None:
        url = videoItem.group(1)
        videoId = videoItem.group(2)
    
        urlXml = "http://www.gametrailers.com/neo/?page=xml.mediaplayer.Mrss&mgid=mgid%3Amoses%3Avideo%3Agametrailers.com%3A" + videoId + "&keyvalues={keyvalues}"
    xml1 = showEpisodeLoadPage(urlXml)
    urlXml = _regex_extractVideoGametrailersXML.search(xml1).group(1)
    urlXml = urlXml.replace("&amp;", "&")
    xml2 = showEpisodeLoadPage(urlXml)
    stream_url = _regex_extractVideoGametrailersStreamURL.search(xml2).group(1)
    item = xbmcgui.ListItem(path=stream_url)
    xbmcplugin.setResolvedUrl(thisPlugin, True, item)
    return False

def showEpisodeSpike(videoItem):
    _regex_extraxtVideoSpikeId = re.compile("<meta property=\"og:video\" content=\"(http://media.mtvnservices.com/mgid:arc:video:spike.com:(.*?))\" />");
    _regex_extractVideoSpikeSreamURL = re.compile("<rendition bitrate=\"(.*?)\".*?<src>(.*?)</src>.*?</rendition>",re.DOTALL)
    
    videoUrl = videoItem.group(1)
    videoPage = showEpisodeLoadPage(videoUrl)
    swfUrl = _regex_extraxtVideoSpikeId.search(videoPage).group(1)
    #GET the 301 redirect URL
    req = urllib2.Request(swfUrl)
    response = urllib2.urlopen(req)
    swfUrl = response.geturl()
    
    videoId = _regex_extraxtVideoSpikeId.search(videoPage).group(2)
    feedUrl = "http://udat.mtvnservices.com/service1/dispatch.htm?feed=mediagen_arc_feed&account=spike.com&mgid=mgid%3Aarc%3Acontent%3Aspike.com%3A"+videoId+"&site=spike.com&segment=0&mgidOfMrssFeed=mgid%3Aarc%3Acontent%3Aspike.com%3A"+videoId
    videoFeed = showEpisodeLoadPage(feedUrl)
    videoStreamUrls = _regex_extractVideoSpikeSreamURL.finditer(videoFeed)
    
    curStream = None
    curBitrate = 0
    for stream in videoStreamUrls:
        streamUrl = stream.group(2)
        streamBitrate = int(stream.group(1))
        if streamBitrate>curBitrate:
            curStream = streamUrl.replace(" ","%20")
            curBitrate = streamBitrate
    
    swfUrl = swfUrl.replace("&geo=DE","&geo=US")
    swfUrl = swfUrl.replace("geo%3dDE%26","geo%3dUS%26")
   
    stream_url = curStream + " swfUrl="+swfUrl+" swfVfy=1"
    if curStream is not None:
        item = xbmcgui.ListItem(path=stream_url)
        xbmcplugin.setResolvedUrl(thisPlugin, True, item)
        return False

def showEpisodeTeamcoco(videoItem):
    #http://teamcoco.com/embed/v/36637
    xmlUrl = "http://teamcoco.com/cvp/2.0/"+videoItem.group(1)+".xml"
    xmlPage = showEpisodeLoadPage(xmlUrl)
    
    _regex_ExtractStreamUrl = re.compile("<file.*?bitrate=\"([0-9]*)\".*?>(.*?)</file>")
    
    streamUrl = "";
    curBitRate = 0
    for streamItem in _regex_ExtractStreamUrl.finditer(xmlPage):
        if curBitRate < int(streamItem.group(1)):
            curBitRate = int(streamItem.group(1))
            streamUrl= streamItem.group(2)
    
    item = xbmcgui.ListItem(path=streamUrl)
    xbmcplugin.setResolvedUrl(thisPlugin, True, item)

def showEpisodeCollegeHumor(videoItem):
    print "test"
    xmlUrl = "http://www.collegehumor.com/moogaloop/video/"+videoItem.group(1)
    _regex_extractStreamUrl = re.compile("<file>.*?<!\[CDATA\[(.*?)\]",re.DOTALL)
    xmlPage = showEpisodeLoadPage(xmlUrl)
    streamUrl = _regex_extractStreamUrl.search(xmlPage).group(1)
    
    item = xbmcgui.ListItem(path=streamUrl)
    xbmcplugin.setResolvedUrl(thisPlugin, True, item)

def showEpisodeLoadPage(url):
    print url
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link

