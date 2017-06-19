import requests

#usr = 'YOUR-USERNAME'
#pwd = 'PASSWORD'

def bb_login(session,usr,passwd):
    url = "https://concordia.blackboard.com/webapps/login/"

    payload = {
        "user_id": usr,
        "password": passwd,
        "login":"Login",
        "action":"login",
        "remote-user": "",
        "new_loc": ""
        }    
    
    r = session.post(url, data=payload)

    #print(r.text)
    #print "\n"

    login_status = 0

    if r.text.find('<HTML') != -1:
        print "Login success!"
        login_status = 1
    #else:
    #    print "Login failed!"

    return session, login_status

    

# Session(): to persist the login session across all our requests.
# r_session = requests.session()
#print r_session

#session, login_status = bb_login(r_session,usr,pwd)
#print session, login_status



