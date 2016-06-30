import argparse
import urllib2
import cookielib
from selenium import webdriver
import time
import re
import requests
import sys
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains


browser = None
"""
This script is to scrape a season page for all the links then to download all
of the MP4 files into a directory and label them.

"""
#set up browser
def setupBrowser():
    global browser
    browser = webdriver.Firefox()



#returns a list of urls to grab for the pages with the videos
def scrapeSeasonPage(link):
    print "Scraping season page"

    browser.get(link)
    time.sleep(10)
    html = browser.page_source
    #html = getFake('fakeSeason.txt')

    ret = []
    inside = False
    for s in html.split('\n'):
        if(re.match('\<table \s*class\=[\'\"]listing[\'\"]\>', s)):
            inside = True
        if(inside and re.match('\<\/table\>', s)):
            inside = False
        if(inside):
            if(re.match('\<a \s*title', s)):
                grp = re.search('href\=\"([^\"]+)\"', s)
                ret.append("http://kisscartoon.me" + str(grp.group(1)))
    return ret

#returns a link for the mp4 video. and file title
def scrapeEpisodePage(link):
    print "Scraping episode page for link ", link
    browser.get(link)
    time.sleep(10)
    try:
        highq = browser.find_element_by_xpath("//select[@id='selectQuality']/option[text()='1080p']")
        if(highq):
            highq.click()
    except:
        print "No 1080p video found, using 720p"

    html = browser.page_source
    browser.close()

    #html = getFake('fakeEpisode.txt')
    for s in html.split('\n'):
        if(re.match('.*\<video.*', s)):
            grp = re.search('.*\<video .*src\=\"([^\"]*)\".*\<\/video\>.*', s)
            retlink = grp.group(1)
            retlink = retlink.replace('&amp;', '&')

    #getting title
    grpt = re.search('.*\/([^\/\?]*)\?.*', link)
    rettitle = grpt.group(1)

    return retlink,rettitle

#Downloads the video to the filename
def downloadVideo(link, title):
    print "Downloading Video: "
    print "   Title: " + title
    print "   Link:  " + link

    file_name = title + ".mp4"
    with open(file_name, "wb") as f:
            print "Downloading %s" % file_name
            response = requests.get(link, stream=True)
            total_length = response.headers.get('content-length')

            if total_length is None: # no content length header
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content():
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
                    sys.stdout.flush()

def getFake(filename):
    val = ""
    with open(filename, 'r') as reader:
        val = reader.read()
    return val

#Controller logic for flow of script
def main():
    print "Start"
    parser = argparse.ArgumentParser(description='Scrape a season page for kisscartoon.me and get all episodes listed.')
    parser.add_argument('--url', dest='seasonUrl', required=True)
    args = parser.parse_args()

    setupBrowser()

    seasonUrl = args.seasonUrl
    episodeList = scrapeSeasonPage(seasonUrl)

    for e in episodeList:
        episodeLink, episodeTitle = scrapeEpisodePage(e)
        downloadVideo(episodeLink, episodeTitle)

    browser.close()

    print "Fin."




main()
