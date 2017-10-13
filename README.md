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
Go into the download code folder and edit the GOOGLE_API_KEY variable in "common/url_status.py". You should see following line the code file. Put your KEY into the double quotation mark.
```
## Your Google API key, get one on Google Console 
GOOGLE_API_KEY = ""
```
The GOOGLE_API_KEY can be applied on [Google Cloud Console](https://console.cloud.google.com) with your google account. 
 * Login the Google Cloud console
 * Go to _APIs & Services_  
 * Click _ENABLE APIS AND SERVICES_ 
 * Search **Youtube data API v3** and click it then __ENABLE__ it.
 
 **Note**: The GOOGLE_API_KEY is used to check Youtube URLs.

## How to use the program
### Single Course URLs checking
With this program, you can check URLs for one course at a time. 

**Guide to use the program**:
1. To start the program, double click "run.py" file under the **Single** folder :file_folder:.
2. Input your Blackboard username and password, click 'Load Courses' button. This will load all courses under your username from Blackboard. 
3. From the course list select a course you want to process URLs checking, then click 'Check URLs' button :black_square_button:. 
4. The new window popup, URLs checking work is processing and eventually it will display all URLs with status. This step may take 2-3 minutes if the course has many URLs.
5. To check displayed URLs list, you need to know:
    - List include following columns: location, hyperlink text, URL, status.
    - URL column shows url link. The broken URLs are shown in red color.  The orange one means code is unable to identity if it is broken. You need to further check these URLs. Other ones are normal.
    - To check the URL, you can just double click the URL cell, it will open the link in the browser.

   
### Multiple Courses URLs checking
With this program, you can check URLs for multiple courses at a time. 

**Guide to use the program**:
1. To start the program, double click "run.py" file under the **Batch** folder :file_folder:.
2. Input your Blackboard username and password, click 'Load Courses' button. All courses under your username will be loaded in the left side window. 
3. To select/delete courses, double click the course row. It will appear/disappear on the right side window.
4. After selection is done, click 'Check URLs' button :black_square_button: to start the URL checking process. It may takes longer time if many courses have chosen. Await patiently. You should the progress in the command terminal.
5. After the program done running, 3 csv files will be generated in **result** folder :file_folder:. Each file inlcudes following info: location, hyperlink text, URL, status.
   * "xx_broken.csv": all broken links are listed in the file.
   * "xx_check.csv": links that need to be checked furtherly.
   * "xx_OK.csv": all links that work normal listed in this file.

### Specific URL identifying
I developed this program for the purpose of idendifying specific links in the courses. For example, if we want to find all youtube links from the all course design in the blackboard, this is the right tool to use.
It can do followings:
* Log into Blackboard account and display all the enrolled coruses.
* The identifying process will start by clicking the **Check URLs** button. You can see the progress in the command line window. It should show the info like staring a course, ending a course etc.
* After it is done, a csv file and a lot file will be generated in **result** folder. 
  * csv file: inlcudes following info: location, hyperlink text, URL.
  * log file: courses progress info.
#### Run the program
1. Double click "run.py" under the **Specific** folder :file_folder:.
   - Then input your Blackboard username and password, click 'Load Courses' button. 
   - Click 'Check URLs' button to start the URL identifying process. 
2. Or you can run the program on the command line. 
   - python run.py
   - other steps are same as above.


-------


