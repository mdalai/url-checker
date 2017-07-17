import requests
import urllib2
import urlparse
import sys
from bs4 import BeautifulSoup
from PyQt5 import QtWidgets
import urllib, json


class Blackboard(object):
    def __init__(self, session):
        self.session = session
        # keep all urls in following global list variable
        self.urlList = []

    ## -----  1. get Course list --------------------------------------------------
    def getCourses(self):
        # https://concordia.blackboard.com/webapps/portal/execute/tabs/tabAction?action=refreshAjaxModule&modId=_22_1&tabId=_2_1&tab_tab_group_id=_2_1
        payload = {'action': 'refreshAjaxModule', 'modId': '_22_1', 'tabId': '_2_1', 'tab_tab_group_id':'_2_1'}
        r = self.session.get("https://concordia.blackboard.com/webapps/portal/execute/tabs/tabAction",
                             params = payload)
        text =r.text.encode("utf-8")
        text_start_pos = text.find("<ul")
        text_end_pos = text.find("</ul")
        text = text[text_start_pos:text_end_pos]

        return self.get_all_target(text)

    def get_all_target(self,page):
        p =[]
        while True:
            coursename,courseid,endpos = self.get_next_target(page)
            if coursename:
                p.append([coursename,courseid])
                page = page[endpos:]
            else:
                break
        return p

    def get_next_target(self,page):
        a_start_pos = page.find("<a href=")
        if a_start_pos == -1:
            return None,None,0
        id_start_pos = page.find("Course&id=", a_start_pos)
        id_end_pos = page.find("&", id_start_pos+10)
        courseid = page[id_start_pos+10:id_end_pos]

        a_end_pos = page.find(">", a_start_pos+1)
        title_start_pos = a_end_pos + 1
        title_end_pos = page.find("</a>", title_start_pos+1)
        coursename = page[title_start_pos:title_end_pos]
        return coursename,courseid, title_end_pos
            
        
    ## -----  2. get URL list from a course --------------------------------------
    def getURLs(self, courseid):
        # --- clean the variable every time ----
        self.urlList = []
        
        payload_temp = {'course_id': courseid}
        r_temp = self.session.get("https://concordia.blackboard.com/webapps/blackboard/content/courseMenu.jsp",
                             params = payload_temp)
        text_temp = r_temp.text.encode("utf-8")
        # make sure it is Content menu
        content_pos = text_temp.find('<span title="Content">Content</span>') # <span title="Content">Content</span>
        cnt_start_pos = text_temp.find("content_id=", content_pos-180)         
        cnt_end_pos = text_temp.find("&",cnt_start_pos)
        cnt_id = text_temp[cnt_start_pos+11:cnt_end_pos]
        #print cnt_id
        payload = {'course_id': courseid, 'content_id': cnt_id, 'mode':'reset' }
        r = self.session.get("https://concordia.blackboard.com/webapps/blackboard/content/listContent.jsp",
                             params = payload)
        soup = BeautifulSoup(r.text,"html.parser")

        if soup.find(id="content_listContainer") == None:
            return []

        for li in soup.find(id="content_listContainer").findAll("li", recursive=False):
            # if it is folder
            if li.find("img")['src'][-13:] == 'folder_on.gif' and li.find("div").find("h3").find("a"):
                wk = li.find("div").find("h3").find("a").find("span").contents[0] 
                # get the Content ID from URL
                contentid = self._getContentIdFromUrl(li.find("div").find("h3").find("a")['href'])
                # get links from the folder
                self.openFolder(courseid, contentid, wk)

            # else if it is File, Test, Discussion,Dropbox ...
            else:
                name = u'\\'.join([unicode("ROOT"), 
                unicode(li.find("div").find("h3").find("span",{"style":"color:#000000;"}).contents[0])])
                #print name
                page = str(li.find("div",{"class":"vtbegenerated"})) # must convert Soup to string
                links2= self.get_all_links(page)
                if links2:
                    self.urlList.append([name, links2])

        return self.urlList

    def _getContentIdFromUrl(self, url):
        link = urlparse.urlparse(url)
        if link.path == "/webapps/blackboard/content/listContent.jsp":
            q = urlparse.parse_qs(link.query)
            if q.has_key('content_id'):
                return q['content_id'][0]
        # if it is Folder link, need to find Redirect URL
        elif link.path == "/webapps/blackboard/content/launchLink.jsp":
            r = self.session.get("https://concordia.blackboard.com" + url, headers={'User-Agent': 'user_agent',})
            linkNew = urlparse.urlparse(r.url)
            q1 = urlparse.parse_qs(linkNew.query)
            if q1.has_key('content_id'):
                return q1['content_id'][0]
        else:
            return None


    def openFolder(self,courseid, contentid, title):
        try:
            payload = {'course_id': courseid, 'content_id': contentid, 'mode':'reset'}
            r = self.session.get("https://concordia.blackboard.com/webapps/blackboard/content/listContent.jsp",
                                params = payload)
            soup = BeautifulSoup(r.text,"html.parser")

            #linksList = []
            # if it is empty Folder return none
            if soup.find(id="content_listContainer") == None:
                #self.urlList.append(['Empty Folder',None])
                return            

            for li in soup.find(id="content_listContainer").findAll("li", recursive=False):
                # if it is folder
                if li.find("img")['src'][-13:] == 'folder_on.gif' and li.find("div").find("h3").find("a"):
                    #--- if there are links under folder ----
                    wk = u'\\'.join([unicode(title), unicode(li.find("div").find("h3").find("a").find("span").contents[0])]) 
                    if li.find("div",{"class":"vtbegenerated"}):
                        page = str(li.find("div",{"class":"vtbegenerated"})) # must convert Soup to string
                        links= self.get_all_links(page)
                        if links:
                            self.urlList.append([wk, links])
                               
                    contentid = self._getContentIdFromUrl(li.find("div").find("h3").find("a")['href'])
                    # keep digging into the folder
                    self.openFolder(courseid, contentid, wk)


                # if it is File
                elif li.find("img")['src'][-15:] == 'document_on.gif':
                    name = u'\\'.join([unicode(title), 
                        unicode(li.find("div").find("h3").find("span",{"style":"color:#000000;"}).contents[0])])
                    #print "File--",name
                    page = str(li.find("div",{"class":"vtbegenerated"})) # must convert Soup to string
                    links= self.get_all_links(page)
                    if links:
                        self.urlList.append([name, links])

                # else if it is Test, Discussion, Dropbox ...
                else:
                    name = u'\\'.join([unicode(title), 
                        unicode(li.find("div").find("h3").find("a").find("span").contents[0])])
                    #print "Dropbox--", name
                    page = str(li.find("div",{"class":"vtbegenerated"})) # must convert Soup to string
                    links= self.get_all_links(page)
                    if links:
                        self.urlList.append([name, links])
            #if linksList:
            #    return linksList
                #print linksList

        except Exception as e:
            QtWidgets.QMessageBox.about(self, "URL Capture Excepion", e)

        

    def get_all_links(self, page):
        urls =[]
        while  True:
            url, endpos = self.get_next_link(page)
            if url:
                urls.append(url)
                page = page[endpos:]
            else:
                break
        return urls

    def get_next_link(self, page):
        a_link = page.find('<a ')
        start_link = page.find(' href="', a_link+1) #http
        if start_link ==  -1:
            return None, 0
        start_quote = page.find('"', start_link)
        end_quote = page.find('"', start_quote + 1)
        url = page[start_quote + 1: end_quote]
        return url, end_quote

    ## -----  3. check URL list --------------------------------------
    def urlStatus_code(self, url):
        #-- flag = 0: No problem, 1: problem, 2: further check
        try:
            response = self.session.head(url, headers={'User-Agent': 'user_agent',})
            if response.status_code == 200 or response.status_code == 403:
                return response.status_code,"OK",0
            elif response.status_code == 301 or response.status_code == 302:
                #-- Checking "redirect" situation" ----- 
                if url.find("https://concordia.blackboard.com/") != -1 or response.headers['Content-Type'] == 'application/pdf' or response.headers['Content-Type'].find('image/') != -1:
                    return response.status_code,"OK",0

                r = self.session.get(response.url,headers={'User-Agent': 'user_agent',}, stream=True) # stream makes it faster
                soup = BeautifulSoup(r.text,"html.parser")

                #-- if soup returns without TITLE ----
                if soup.title == None:
                    return response.status_code,"Redirection returns ABNORMAL content",2
                if soup.title.string.lower().find('page not found') == -1:
                    return response.status_code,soup.title.string,0
                else:
                    return response.status_code,"It is Page Not Found",1
                    
            elif response.status_code == 400 or response.status_code == 404 or response.status_code == 410:
                return response.status_code,"Broken Links/Page Not Found",1
            else:              
                return response.status_code,None,2
        except Exception as ex:
            return 777,ex,2



    #-- Check YOUTUBE URLs 
    def youtubeStatus(self,url):
        
        if url.find("v=") != -1:
            start_pos = url.find("v=") + 2
    	    end_pos = url.find("&", start_pos)
    	    if end_pos == -1:
    		end_pos = url.find("#", start_pos)
    		if end_pos == -1:
    		    youtube_id = url[start_pos:]
    		else:
    		    youtube_id = url[start_pos:end_pos]
    	    else:
    		youtube_id = url[start_pos:end_pos]
    	elif url.find(".be/") != -1:
    	    start_pos = url.find(".be/") + 4
    	    end_pos = url.find("?", start_pos)
            if end_pos == -1:
                youtube_id = url[start_pos:]
            else:
                youtube_id = url[start_pos:end_pos]
        else:
            return "Youtube Channel"

    	#print youtube_id
    	try:
    	    urlAPI = "https://www.googleapis.com/youtube/v3/videos?part=status&id=%s&key=[YOUR-API-KEY]"%youtube_id
    	    response = urllib.urlopen(urlAPI)
    	    result = json.loads(response.read())
    	    if result["items"] == []:
    		return "UNAVAILABLE"
    	    else:
    		return result['items'][0]['status']['uploadStatus']
    	except Exception, e:
            #print e
    	    return "EXCEPTION"  
    





                  
                  
            
