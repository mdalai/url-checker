import sys
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from bb1 import Blackboard
import requests
import pandas as pd
import numpy as np
import pickle
import urllib, json
import webbrowser

reload(sys)
sys.setdefaultencoding('utf-8')

qtCreatorFile1 = "bb_urls.ui" # Enter file here.
Ui_urlWindow , QtBaseClass = uic.loadUiType(qtCreatorFile1)

class urlWindow(QtWidgets.QDialog, Ui_urlWindow):
    def __init__(self, parent=None):
    	super(urlWindow,self).__init__(parent)
        #QtWidgets.QDialog.__init__(self)
        #Ui_urlWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.tableWidget_urls.itemDoubleClicked.connect(self.openURL)

    def openURL(self, QTableWidgetItem):
    	#print QTableWidgetItem.text()
    	webbrowser.open(QTableWidgetItem.text(), new=0, autoraise=True)

qtCreatorFile = "bb_login.ui" # Enter file here.
Ui_Window , QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtWidgets.QMainWindow, Ui_Window):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_Window.__init__(self)
        self.setupUi(self)

        #-- create session --#
        self.session = requests.Session()
        # initialize Blackboard class
        self.bb = Blackboard(self.session)

        # Login 
        self.pushButton_getCourses.clicked.connect(self.login)
        # Check URL
        self.pushButton_checkURLs.clicked.connect(self.checkURLs)	

    def logout(self):
    	#print self.session.cookies.get_dict()
    	print "Logout Successful!!"
    	r = self.session.get("https://concordia.blackboard.com/webapps/login/?action=logout")

    def login(self):
    	user = self.lineEdit_username.text()
    	pwd = self.lineEdit_pass.text()
    	#-- Start Wait Curser -----------------------------------------------------------------
    	QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
    	
    	payload = {
            "user_id": user,
            "password": pwd,
            "login":"Login",
            "action":"login",
            "remote-user": "",
            "new_loc": "",
            "auth_type":"",
            "one_time_token": ""
            }
        try:
        	# make session for visiting blackboard site
        	r = self.session.post("https://concordia.blackboard.com/webapps/login/", data=payload)
        	# Create a list to store all courses
        	courses =[]
        	# recall getCourses method from Blackboard Class
        	courses = self.bb.getCourses()
      		if courses != []:
      			print "Login Success!"

      		# Use TableWidget to show course list
       		self.tableWidget_courses.setColumnCount(2)
       		self.tableWidget_courses.setRowCount(len(courses))
       		self.tableWidget_courses.setHorizontalHeaderLabels(['Courses Name', 'Courses ID'])
       		i = 0
       		for p in courses:
       			self.tableWidget_courses.setItem(i, 0, QtWidgets.QTableWidgetItem(p[0]))
       			self.tableWidget_courses.setItem(i, 1, QtWidgets.QTableWidgetItem(p[1]))
       			i = i+1
        	self.tableWidget_courses.resizeColumnsToContents()     	        	

        except Exception as e:
        	print e
        	QtWidgets.QMessageBox.about(self, "Warning message box", "Server Exception! please try again!!" )

        #-- End Wait Curser -----------------------------------------------------------------
        QtWidgets.QApplication.restoreOverrideCursor() 

    def checkURLs(self):    	
    	row = self.tableWidget_courses.currentRow()
        #print row
        if row == -1:
            QtWidgets.QMessageBox.about(self, "My message box", "Please choose a Course!" )
            return
            #raise Exception("cause of the problem")
    	course_id = self.tableWidget_courses.item(row,1).text()

        url_window = urlWindow(self)
        url_window.show()

    	#-- Start Wait Curser -----------------------------------------------------------------
    	QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
    	
    	#print course_id
    	links = self.bb.getURLs(course_id)
    	#---------- Test Start ---------------------------------
    	#with open('urlTest.txt', 'rb') as f:
    	#	links = pickle.load(f)
    	'''links = [['root',['http://www.onlinejcf.com/article/S1071-9164%2816%2930550-4/pdf',
                           'http://www.onlinejcf.com/article/S1071-9164(10)00174-0/fulltext',
                           'http://www.pbs.org/wgbh/pages/frontline/the-spill/']],
                ['test1',['http://www.dfwhcfoundation.org/wp-content/uploads/2013/10/Cultural-and-linguistic-competence-in-Patient-care_Sushma-Sharma-1.jpg',
                          'https://www.youtube.com/user/WhiteHouseAAPI',
                          'https://en-us.help.blackboard.com/Learn/9.1_2014_04/Instructor/100_Assignments/025_Use_SafeAssign/010_SafeAssign_Originality_Reports']]
                ] '''

    	#---------- Test End ---------------------------------
        #print links
        if links == []:
            QtWidgets.QMessageBox.about(self, "My message box", "Returns no link. Please check the CONTENT in the Blackboard!!" )
            return
        #with open('linksTest.txt', 'wb') as f:
        #    pickle.dump(links, f)

        # ----- Check the URL responses and keep data into Panda DF ---------------------------------
    	df = pd.DataFrame(columns=('Location','URL','Status_code','Remark','flag'))
    	for urls in links:
    	  for url in urls[1]:
            if url.find("youtube.com") == -1 and url.find("youtu.be/") == -1:          
              #print url                            
    	      status_code, comment, flag = self.bb.urlStatus_code(url)
    	      df = pd.DataFrame(np.array([[urls[0], url, status_code, comment, flag]]),
              columns=['Location','URL','Status_code','Remark','flag']).append(df, ignore_index=True)
    	    else:
    	      flag = 1
    	      r = requests.head(url, headers={'User-Agent': 'user_agent',})
    	      if r.status_code != 404:
    		status = self.bb.youtubeStatus(url)
    		if status == "processed" or status == "Youtube Channel":
    		  flag = 0
    		elif status == "UNAVAILABLE" or status == "EXCEPTION":
    		  flag = 2
    		else:
    		  flag = 1

    	      else:
    		  status = "YOUTUBE Not Found"
    	      df = pd.DataFrame(np.array([[urls[0], url, r.status_code, status, flag]]),
              columns=['Location','URL','Status_code','Remark','flag']).append(df, ignore_index=True)

    	#---- Reverse DF order
    	df = df.iloc[::-1]

    	#----- Show the data of DF into a TableWidget ---------------
    	url_window.tableWidget_urls.setColumnCount(len(df.columns))
    	url_window.tableWidget_urls.setRowCount(len(df.index))
    	url_window.tableWidget_urls.setHorizontalHeaderLabels(['Location','URL','Status_code','Remark','flag'])

    	for i in range(len(df.index)):
    		for j in range(len(df.columns)):
       			url_window.tableWidget_urls.setItem(i, j, QtWidgets.QTableWidgetItem(str(df.iat[i, j])))
       		#-- set a row background color
       		if int(df.iat[i,4]) == 1:
       			url_window.tableWidget_urls.item(i,1).setBackground(QtGui.QColor(255, 128, 128))
       		if int(df.iat[i,4]) == 2:
       			url_window.tableWidget_urls.item(i,1).setBackground(QtGui.QColor(244, 252, 0))

       	url_window.tableWidget_urls.resizeColumnsToContents() 
       	url_window.tableWidget_urls.resizeRowsToContents() 


        #-- End Wait Curser -----------------------------------------------------------------
        QtWidgets.QApplication.restoreOverrideCursor()  


        # if Pandas Dataframe is not empty, save to a csv file
        if not df.empty:
          df.to_csv(course_id +'.csv', encoding='utf-8')


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()

    # -- logout Blackboard before exit
    ret = app.exec_()
    window.logout()
    sys.exit(ret)
