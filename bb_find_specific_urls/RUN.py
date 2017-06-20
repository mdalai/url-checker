import sys
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from bb import Blackboard
import requests
import pandas as pd
import numpy as np
#import pickle

import bb_login
from file_io import appendDFToCSV
from url_status import youtubeStatus,getYoutubeID,checkUrlStatus
import datetime
import logging
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

reload(sys)
sys.setdefaultencoding('utf-8')


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
    	rowCount = self.tableWidget_courses.rowCount()
    	if rowCount == 0:
            QtWidgets.QMessageBox.about(self, "My message box", "Login first or Your account has not courses!" )
            return

        # ----- Check the URL responses and keep data into Panda DF ---------------------------------
    	df = pd.DataFrame(columns=('Course','Location','URL_Name','URL'))

    	# get the current datetime for filename
    	dtime = datetime.datetime.now().strftime("%y%m%d%H%M")
            
    	for row_index in range(rowCount):
            #if row_index ==4:
            #    break
            course_name = self.tableWidget_courses.item(row_index,0).text()
            cid = self.tableWidget_courses.item(row_index,1).text()
            #print cid
            links = self.bb.getSpecificURLs(cid)
            '''links = [['root',['https://www.youtube.com/watch?v=YdtLELVhEQg',
                           'https://www.youtube.com/watch?v=esPRsT-lmw8',
                           'http://youtu.be/sRc9Noz80ko']],['course2',['https://stackoverflow.com/questions/311627/how-to-print-date-in-a-regular-format-in-python',
                           'www.yahoo.com']]] '''


            if links != []:
                for urls in links:
                    for url in urls[1]:
                        #print urls[0],url[0],url[1]

                        # check proquest.com
                        if url[1].find('proquest.com') != -1:
                            print "FINDING Proquest.com"
                            df = pd.DataFrame(np.array([[course_name,urls[0], url[0], url[1]]]),
                                              columns=['Course','Location','URL_Name','URL']).append(df, ignore_index=True)

                #---- Reverse DF order
                df = df.iloc[::-1]
                #print df

                appendDFToCSV(df, 'result/'+dtime+'_ProguestUrls.csv')

                # drop all values
                df.drop(df.index, inplace=True)

                # Print the process
                print "[%s/%s]>>>%s>>>IS DONE"%(row_index+1,rowCount,course_name)
                logging.basicConfig(level=logging.DEBUG, filename="result/logfile", filemode="a+", format="%(asctime)-15s %(levelname)-8s %(message)s")
                logging.info("[%s/%s]>>>%s>>>IS DONE"%(row_index+1,rowCount,course_name))


            else:
                print "[%s/%s]>>>%s>>>has no links!"%(row_index+1,rowCount,course_name)
                logging.basicConfig(level=logging.DEBUG, filename="result/logfile", filemode="a+", format="%(asctime)-15s %(levelname)-8s %(message)s")
                logging.info("[%s/%s]>>>%s>>>has no links!"%(row_index+1,rowCount,course_name))
                
                                  

                
           
        


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()

    # -- logout Blackboard before exit
    ret = app.exec_()
    window.logout()
    sys.exit(ret)
