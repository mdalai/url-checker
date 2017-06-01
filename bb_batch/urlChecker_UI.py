import sys
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from bb import Blackboard
import requests
import pandas as pd
import numpy as np
import pickle

import bb_login
from file_io import appendDFToCSV
import datetime

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
        # double click to Select course
        self.tableWidget_courses.itemDoubleClicked.connect(self.selectCourse)
        # double click to Delete course
        self.tableWidget_selected_courses.itemDoubleClicked.connect(self.deleteCourse)        
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

        	# initialize the selected course tableWidget in here
        	self.tableWidget_selected_courses.setColumnCount(2)
                self.tableWidget_selected_courses.setHorizontalHeaderLabels(['Courses Name', 'Courses ID'])
        	

        except Exception as e:
        	print e
        	QtWidgets.QMessageBox.about(self, "Warning message box", "Server Exception! please try again!!" )

        #-- End Wait Curser -----------------------------------------------------------------
        QtWidgets.QApplication.restoreOverrideCursor()
        


    def selectCourse(self):       		
        row_index = self.tableWidget_courses.currentRow()
        course = self.tableWidget_courses.item(row_index,0).text()
        cid = self.tableWidget_courses.item(row_index,1).text()

        # Check if the value is already selected ---------
        for row in range(self.tableWidget_selected_courses.rowCount()):
            exist_cid = self.tableWidget_selected_courses.item(row,1).text()
            if exist_cid == cid:
                QtWidgets.QMessageBox.about(self, "Warning message box", "The course is already selected!!" )
                return
        rowPos = self.tableWidget_selected_courses.rowCount()
        self.tableWidget_selected_courses.insertRow(rowPos)
        self.tableWidget_selected_courses.setItem(rowPos, 0, QtWidgets.QTableWidgetItem(course))
        self.tableWidget_selected_courses.setItem(rowPos, 1, QtWidgets.QTableWidgetItem(cid))

        self.tableWidget_selected_courses.resizeColumnsToContents()

    def deleteCourse(self):
        row_index = self.tableWidget_selected_courses.currentRow()
        self.tableWidget_selected_courses.removeRow(row_index)
        

    def checkURLs(self):    	
    	rowCount = self.tableWidget_selected_courses.rowCount()
    	if rowCount == 0:
            QtWidgets.QMessageBox.about(self, "My message box", "Please select Course first!" )
            return

        # ----- Check the URL responses and keep data into Panda DF ---------------------------------
    	df = pd.DataFrame(columns=('Course','Location','URL','Status_code','Remark','flag'))

    	# get the current datetime for filename
    	dtime = datetime.datetime.now().strftime("%y%m%d%H%M")
            
    	for row_index in range(rowCount):
            course_name = self.tableWidget_selected_courses.item(row_index,0).text()
            cid = self.tableWidget_selected_courses.item(row_index,1).text()
            #print cid
            links = self.bb.getURLs(cid)
            '''links = [['root',['https://www.youtube.com/watch?v=YdtLELVhEQg',
                           'https://www.youtube.com/watch?v=esPRsT-lmw8',
                           'http://youtu.be/sRc9Noz80ko']],['course2',['https://stackoverflow.com/questions/311627/how-to-print-date-in-a-regular-format-in-python',
                           'www.yahoo.com']]] '''
            if links != []:
                for urls in links:
                    for url in urls[1]:
                        if url.find("youtube.com") == -1 and url.find("youtu.be/") == -1:
                            status_code, comment, flag = self.bb.urlStatus_code(url)
    	                    df = pd.DataFrame(np.array([[course_name,urls[0], url, status_code, comment, flag]]),
                                              columns=['Course','Location','URL','Status_code','Remark','flag']).append(df, ignore_index=True)
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
                            df = pd.DataFrame(np.array([[course_name,urls[0], url, r.status_code, status, flag]]),
                                              columns=['Course','Location','URL','Status_code','Remark','flag']).append(df, ignore_index=True)

                #---- Reverse DF order
                df = df.iloc[::-1]
                #print df

                # if Pandas Dataframe is not empty, save to a csv file             
                #-- flag = 0: No problem, 1: problem, 2: further check
                if not df.loc[df['flag']=='1'].empty:
                    appendDFToCSV(df.loc[df['flag']=='1'], 'result/'+dtime+'_broken.csv')
                    
                if not df.loc[df['flag']==2].empty:
                    appendDFToCSV(df.loc[df['flag']==2], 'result/'+dtime+'_check.csv')
                
                if not df.loc[df['flag']=='0'].empty:
                    appendDFToCSV(df.loc[df['flag']=='0'], 'result/'+dtime+'_OK.csv')


                # drop all values
                df.drop(df.index, inplace=True)

                # Print the process
                print "[%s/%s]>>>%s>>>IS DONE"%(row_index+1,rowCount,course_name)
                                  

                
           
        


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()

    # -- logout Blackboard before exit
    ret = app.exec_()
    window.logout()
    sys.exit(ret)
