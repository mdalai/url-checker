# url-checker
Checking URLs on the [Blackboard](http://www.blackboard.com) are tedious. This project is created for the purpose of automating URLs checking work on the Blackboard. This work simplifies instructional designer's job. So far, there are three main functions those are Single Course URLs checking, Multiple Courses URLs checking and Specific URL identifying.
## Requirements
### Installation
1. Download and install [python 2.7 64bit](https://www.python.org/downloads/release/python-2714/). Check your installation by doing ```python --version``` in your command terminal.
2. Download the [repository](https://github.com/mdalai/url-checker/archive/master.zip), unzip it OR ```git clone https://github.com/mdalai/url-checker.git``` if you are familiar with **git bash**.
3. Open the command terminal, input following command to install dependencies:
```sh
   pip install python-qt5 pandas requests, webbrowser
```
### Configuration
Go into the download code folder and edit the GOOGLE_API_KEY variable in "common/url_status.py". You should apply GOOGLE_API_KEY on [Google Cloud Console](https://console.cloud.google.com) with your google account. The GOOGLE_API_KEY is used to check Youtube URLs.
```
## Your Google API key, get one on Google Console 
GOOGLE_API_KEY = ""
```
## How to use the program
### Single Course URLs checking
It can do followings:
* Log into Blackboard account and display all the enrolled coruses.
* Choose a course which has URLs need to be checked
* By clicking the **Check URLs** button, the new window will be prompted. It displays the list of all URLs within the courses. The display inlcudes following info: location, hyperlink text, URL, status. If the URL is broken, the row will be shown in red color. 
* Double click the cell with URL, it will open the link in browser. Some of links are hard to trace by programming. These are shown in orange color. This function makes this manual checking process convenient.
#### Run the program
1. Double click "run.py" under the **Singel** foler.
   - Then input your Blackboard username and password, click 'Load Courses' button. 
   - From the course list choose a course you want to check URLs, then click 'Check URLs' button. 
   - The new window will be openned and list out all the URLs and statuses. It may take longer time if the course has many URLs.
2. Or you can run the program on the command line. 
   - python run.py
   - other steps are same as above.
   
### Multiple Courses URLs checking
It can do followings:
* Log into Blackboard account and display all the enrolled coruses.
* Choose multiple courses for checking URLs
* The URL checking process will be treggered by clicking the **Check URLs** button. It might take for a while.
* After the program done running, 3 csv files will be generated in **result** folder. Each file inlcudes following info: location, hyperlink text, URL, status.
  * "xx_broken.csv": all broken links are listed in the file.
  * "xx_check.csv": links that need to be checked furtherly.
  * "xx_OK.csv": all links that are fine listed in this file.
#### Run the program
1. Double click "run.py" under the ** Batch ** foler.
   - Then input your Blackboard username and password, click 'Load Courses' button. 
   - List in the left hand side are there to let you choose by double clicking. You will see the course appears in the right hand side by the operation. If you want to delete from a course from the right hand, just double click as well. Finally, click 'Check URLs' button to start the URL checking process. 
   - It may take longer time if many courses have chosen. Await patiently.
2. Or you can run the program on the command line. 
   - python run.py
   - other steps are same as above.
### Specific URL identifying
I developed this program for the purpose of idendifying specific links in the courses. For example, if we want to find all youtube links from the all course design in the blackboard, this is the right tool to use.
It can do followings:
* Log into Blackboard account and display all the enrolled coruses.
* The identifying process will start by clicking the **Check URLs** button. You can see the progress in the command line window. It should show the info like staring a course, ending a course etc.
* After it is done, a csv file and a lot file will be generated in **result** folder. 
  * csv file: inlcudes following info: location, hyperlink text, URL.
  * log file: courses progress info.
#### Run the program
1. Double click "run.py" under the ** Specific ** foler.
   - Then input your Blackboard username and password, click 'Load Courses' button. 
   - Click 'Check URLs' button to start the URL identifying process. 
2. Or you can run the program on the command line. 
   - python run.py
   - other steps are same as above.


-------


