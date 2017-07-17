import requests
import urllib2
import urlparse
import sys
from bs4 import BeautifulSoup
from PyQt5 import QtWidgets
import urllib, json
from get_targats_html import get_course_and_id,get_next_course_and_id,get_all_links_and_name,get_next_link_and_name
#from get_targats_html import get_all_links,get_next_link


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

        return get_course_and_id(text)
    

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


    

       
    ## -----  2. get all URLs from a course --------------------------------------
    def getAllURLs(self, courseid):
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
            try:                
                # if it is folder
                if li.find("img")['src'][-13:] == 'folder_on.gif' and li.find("div").find("h3").find("a"):
                    wk = li.find("div").find("h3").find("a").find("span").contents[0] 
                    # get the Content ID from URL
                    contentid = self._getContentIdFromUrl(li.find("div").find("h3").find("a")['href'])
                    # get links from the folder
                    self.openFolderGetUrlsName(courseid, contentid, wk)

                # else if it is File, Test, Discussion,Dropbox ...
                else:
                    if li.find("div").find("h3").find("span",{"style":"color:#000000;"}).contents[0]:
                        name = u'\\'.join([unicode("ROOT"),
                                           unicode(li.find("div").find("h3").find("span",{"style":"color:#000000;"}).contents[0])])
                    else:
                        name = "ROOT-XXXXX"

                    #print name
                    page = str(li.find("div",{"class":"vtbegenerated"})) # must convert Soup to string
                    links2= get_all_links_and_name(page)
                    if links2:
                        self.urlList.append([name, links2])
            except Exception as e:
                #print "ERROR"
                print "Error:", e
                continue 

        return self.urlList

                  
    def openFolderGetUrlsName(self,courseid, contentid, title):
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
                        links= get_all_links_and_name(page)
                        if links:
                            self.urlList.append([wk, links])
                               
                    contentid = self._getContentIdFromUrl(li.find("div").find("h3").find("a")['href'])
                    # keep digging into the folder
                    self.openFolderGetUrlsName(courseid, contentid, wk)


                # if it is File
                elif li.find("img")['src'][-15:] == 'document_on.gif':
                    name = u'\\'.join([unicode(title), 
                        unicode(li.find("div").find("h3").find("span",{"style":"color:#000000;"}).contents[0])])
                    #print "File--",name
                    page = str(li.find("div",{"class":"vtbegenerated"})) # must convert Soup to string
                    links= get_all_links_and_name(page)
                    #print links
                    if links:
                        self.urlList.append([name, links])

                # else if it is Test, Discussion, Dropbox ...
                else:
                    name = u'\\'.join([unicode(title), 
                        unicode(li.find("div").find("h3").find("a").find("span").contents[0])])
                    #print "Dropbox--", name
                    page = str(li.find("div",{"class":"vtbegenerated"})) # must convert Soup to string
                    links= get_all_links_and_name(page)
                    if links:
                        self.urlList.append([name, links])
            #if linksList:
            #    return linksList
                #print linksList

        except Exception as e:
            QtWidgets.QMessageBox.about(self, "URL Capture Excepion", e)


# -------------------------- Planning to NOT USE from here -------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------

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
                links2= get_all_links(page)
                if links2:
                    self.urlList.append([name, links2])

        return self.urlList


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
                        links= get_all_links(page)
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
                    links= get_all_links(page)
                    if links:
                        self.urlList.append([name, links])

                # else if it is Test, Discussion, Dropbox ...
                else:
                    name = u'\\'.join([unicode(title), 
                        unicode(li.find("div").find("h3").find("a").find("span").contents[0])])
                    #print "Dropbox--", name
                    page = str(li.find("div",{"class":"vtbegenerated"})) # must convert Soup to string
                    links= get_all_links(page)
                    if links:
                        self.urlList.append([name, links])
            #if linksList:
            #    return linksList
                #print linksList

        except Exception as e:
            QtWidgets.QMessageBox.about(self, "URL Capture Excepion", e)
