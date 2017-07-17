

##****** Extract coursename, course ID **********
## **** From HTML **************************
def get_course_and_id(htmlTxt):
    course_and_ids =[]
    while True:
        course,cid,endpos = get_next_course_and_id(htmlTxt)
        if course:
            course_and_ids.append([course,cid])
            htmlTxt = htmlTxt[endpos:]
        else:
            break
    return course_and_ids

def get_next_course_and_id(page):
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
    return coursename,courseid,title_end_pos



def get_all_links(page):
    urls =[]
    while  True:
        url, endpos = get_next_link(page)
        if url:
            urls.append(url)
            page = page[endpos:]
        else:
            break
    return urls

def get_next_link(page):
    a_link = page.find('<a ')
    start_link = page.find(' href="http', a_link+1) #http will exclude # button
    if start_link ==  -1:
        return None, 0
    start_quote = page.find('"', start_link)
    end_quote = page.find('"', start_quote + 1)
    url = page[start_quote + 1: end_quote]
    return url, end_quote
