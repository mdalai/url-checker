import sys 
import os
sys.path.append(os.path.relpath("../common"))

from PyQt5 import QtWidgets, uic, QtCore, QtGui
from bb import Blackboard
import requests
import pandas as pd
import numpy as np
#import pickle
import webbrowser

import bb_login
from file_io import appendDFToCSV
from url_status import youtubeStatus,getYoutubeID,checkUrlStatus
import datetime
import logging
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

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

    	#-- create session --#
        self.session = requests.Session()
    	self.session, login_status = bb_login.bb_login(self.session,user,pwd)
    	if login_status==0:
            #-- End Wait Curser -------
            QtWidgets.QApplication.restoreOverrideCursor()            
            QtWidgets.QMessageBox.about(self, "Warning message box", "Login Failed!" )               
            #return
        
        else:
            # initialize Blackboard class
            self.bb = Blackboard(self.session)
    	
        try:
        	# Create a list to store all courses
        	courses =[]
        	# recall getCourses method from Blackboard Class
        	courses = self.bb.getCourses()
        	#courses =[['class1','1111'],['class2','2111'],['class3','3111']]
      		if courses == []:
      			print "No course available!"

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

    	#-------- Links data structure 1 --------------------------
    	#links = self.bb.getURLs(course_id)
    	#links = [['loc1',[url11,url12,url13]], ['loc2',[url21,ur22]] ]
    	#-------- Links data structure 2 --------------------------
    	links = self.bb.getAllURLs(course_id) # get urls with title
    	#links = [['loc1',[ [title11,url11],[title12,url12],[title13,url13] ]], ['loc2',[ [title21,url21],[title22,ur22] ]] ]
        if links == []:
            QtWidgets.QMessageBox.about(self, "My message box", "Returns no link. Please check the CONTENT in the Blackboard!!" )
            # has to close the wait curser, otherwise it will keep showing the curser that is running.
            QtWidgets.QApplication.restoreOverrideCursor()
            return
    	
        # ----- Check the URL responses and keep data into Panda DF ---------------------------------
    	df = pd.DataFrame(columns=('Location','URL_Name','URL','Status_code','Remark','flag'))
    	for urls in links:
    	  for url in urls[1]:
            if url[1].find("youtube.com") == -1 and url[1].find("youtu.be/") == -1:                                    
    	      #status_code, comment, flag = self.bb.urlStatus_code(url)
    	      status_code, comment, flag = checkUrlStatus(url[1],self.session)
    	      df = pd.DataFrame(np.array([[urls[0], url[0],url[1], status_code, comment, flag]]),
              columns=['Location','URL_Name','URL','Status_code','Remark','flag']).append(df, ignore_index=True)
    	    else:
                
    	      flag = 1
    	      r = requests.head(url[1], headers={'User-Agent': 'user_agent',})
    	      if r.status_code != 404:
    		#status = self.bb.youtubeStatus(url)
    		y_id = getYoutubeID(url[1])
    		if y_id == "youtube_channel":
                    flag = 0
                else:
                    status,_,_ = youtubeStatus(y_id)
                    if status == "processed":
                        flag = 0
                    elif status == None or status == 0:
                        flag = 2
                    else:
                        flag = 1
            

    	      else:
    		  status = "YOUTUBE Not Found"
    	      df = pd.DataFrame(np.array([[urls[0], url[0], url[1], r.status_code, status, flag]]),
              columns=['Location','URL_Name','URL','Status_code','Remark','flag']).append(df, ignore_index=True)


    	#---- Reverse DF order
    	df = df.iloc[::-1]

    	#----- Show the data of DF into a TableWidget ---------------
    	url_window.tableWidget_urls.setColumnCount(len(df.columns))
    	url_window.tableWidget_urls.setRowCount(len(df.index))
    	url_window.tableWidget_urls.setHorizontalHeaderLabels(['Location','URL_Name','URL','Status_code','Remark','flag'])

    	for i in range(len(df.index)):
    		for j in range(len(df.columns)):
       			url_window.tableWidget_urls.setItem(i, j, QtWidgets.QTableWidgetItem(str(df.iat[i, j])))
       		#-- set a row background color
       		if int(df.iat[i,5]) == 1:
       			url_window.tableWidget_urls.item(i,2).setBackground(QtGui.QColor(255, 128, 128))
       		if int(df.iat[i,5]) == 2:
       			url_window.tableWidget_urls.item(i,2).setBackground(QtGui.QColor(244, 252, 0))

       	url_window.tableWidget_urls.resizeColumnsToContents() 
       	url_window.tableWidget_urls.resizeRowsToContents() 


        #-- End Wait Curser -----------------------------------------------------------------
        QtWidgets.QApplication.restoreOverrideCursor()  


        #-- SAVE -- if Pandas Dataframe is not empty, save to a csv file
        #if not df.empty:
        #  df.to_csv(course_id +'.csv', encoding='utf-8')
           
        


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()

    # -- logout Blackboard before exit
    ret = app.exec_()
    window.logout()
    sys.exit(ret)
