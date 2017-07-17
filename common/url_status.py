import urllib, json
import re
import requests
from bs4 import BeautifulSoup

## Your Google API key, get one on Google Console 
GOOGLE_API_KEY = ""

def youtubeStatus(youtube_id):
    """
    Check Youtube response status
    :param youtube_id: 12 digits youtube ID
    :return: status,embeddagle,title
    """
    
    try:
        urlAPI = "https://www.googleapis.com/youtube/v3/videos?part=status,snippet&id=%s&key=%s"%(youtube_id,GOOGLE_API_KEY)
        response = urllib.urlopen(urlAPI)
        result = json.loads(response.read())
        if result["items"] == []:
            return None,None,None
        else:
            return result['items'][0]['status']['uploadStatus'],result['items'][0]['status']['embeddable'],result['items'][0]['snippet']['title']
    except:
        return 0,0,0


def getYoutubeID(y_url):
    """
    Extract Youtube ID from the Youtube URL
     :param y_url: Youtube URL
     :return: Youtube ID
    """    
    result = re.search(r'((?<=(v|V)/)|(?<=be/)|(?<=(\?|\&)v=)|(?<=embed/))([\w-]+)',y_url)
    if result:
        return result.group(0)
    else:
        return 'youtube_channel'


def checkUrlStatus(url,session=None):
    """
    Check URL response status
     :param url: any URL
     :param session: internal URL login session
     :return: status_code,description,flag
    Note: flag = 0: No problem, 1: problem, 2: further check
    """
    try:
        # IF it is not Blackboard URL
        if url.find("https://concordia.blackboard.com/") == -1:
            response = requests.head(url, headers={'User-Agent': 'user_agent',})
            if response.status_code == 200 or response.status_code == 403:
                return response.status_code,"OK",0
            elif response.status_code == 301 or response.status_code == 302:
                # content-type do not work
                #if response.headers['Content-Type'] == 'application/pdf' or response.headers['Content-Type'].find('image/') != -1:
                #    return response.status_code,"OK",0

                r = requests.get(response.url,headers={'User-Agent': 'user_agent',}, stream=True) # stream makes it faster
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


        # IF it is a Blackboard URL   
        else:
            response = session.head(url, headers={'User-Agent': 'user_agent',})
            if response.status_code == 200 or response.status_code == 403:
                return response.status_code,"OK",0
            elif response.status_code == 301 or response.status_code == 302:
                return response.status_code,"Blackboard Redirect",0
                
            elif response.status_code == 400 or response.status_code == 404 or response.status_code == 410:
                return response.status_code,"Broken Links/Page Not Found",1
            else:
                return response.status_code,None,2

        
    except Exception as ex:
        return 777,ex,2
        
    



#print getYoutubeID('https://www.youtube.com/watch?v=a_FdGxvLwW0&feature=youtu.be')
#print getYoutubeID('https://youtu.be/x_FdGxvLwW0')
#print getYoutubeID('https://youtube.com/channel/UCUZHFZ9jIKrLroW8LcyJEQQ')
#print getYoutubeID('https://youtube.com/c/YouTubeCreators')
'''
urls = [#'http://familybusiness.ey.com/pdfs/72-77.pdf',
        #'http://www.fbli-usa.com/wp-content/uploads/2015/02/WSJ-article-Famly-Businesses-Welcome-Outside-Buyers.pdf',
        'https://www.forbes.com/forbes/welcome/?/sites/chasewithorn/2015/04/20/new-report-reveals-the-500-largest-family-owned-companies-in-the-',
        'https://www.linkedin.com/pulse/family-businesses-have-richard-sink',
        'http://cuw.ezproxy.switchinc.org/login?url=http://search.ebscohost.com/login.aspx?direct=true&amp;AuthType=cookie,ip,cpid&amp;custid=s3443150&amp;db=bth&amp;AN=21897012&amp;site=ehost-live&amp;scope=site',
        #'https://concordia.blackboard.com/bbcswebdav/pid-614439-dt-content-rid-4434725_1/xid-4434725_1',
        #'https://concordia.blackboard.com/bbcswebdav/pid-614439-dt-content-rid-4359027_1/xid-4359027_1',
        'http://oai.dtic.mil/oai/oai?verb=getRecord&metadataPrefix=html&identifier=ADA204744'
        ]
for i,url in enumerate(urls):
    print "%s---------",i
    print checkUrlStatus(url) '''

    
