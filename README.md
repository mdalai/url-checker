# url-checker
Checking urls in Blackboard
# Installation:
1. python 2.7 64bit
2. pip install python-qt5
3. pip install pandas
4. pip install requests
5. pip install webbrowser (sometimes, it is already included in the python basic)
# Run the program
1. Double click "pyqt_bb.py" will start the program. 
   - Then input your Blackboard username and password, click 'Load Courses' button. 
   - From the course list choose a course you want to check URLs, then click 'Check URLs' button. 
   - The new window will be openned and list out all the URLs and statuses. It may take longer time if the course has many URLs.
2. Or you can run the program on the command line. 
   - python pyqt_bb.py
  
# Revealing Programming Process
## Login

## Course list
The course list under the login user.

## Extract URLs 
Extract URLs from selected course. List out all the URLs from the course chosen.

## Check URLS
In order to get precise information about Youtube URL, I have adopted different tactics for Youtube URLs. I have seperated Youtube URLs from the URL list. I made two methods accordingly. "Def urlStatus_code" is for checking non Youtube URLs; and "Def youtubeStatus" is for Youtube URLs.
### def urlStatus_code
It mainly extract status_code of URL. In order to make the URL response faster, I used head which will only return header part of response page. 
 -- status_code = 200: OK
 -- status_code = 403: OK
 -- status_code = 301/302: need to further check the redirect case:
   - status_code = 400/404: Broken link
   - Blackboard internal link: OK
   - Check according to return title
 -- status_code = 400: Broken Link
 -- status_code = 404: Broken Link

### def youtubeStatus
1. Extract Youtube ID from URL.
2. Apply Google API for Youtube. You have to apply Google API Key first. 
   - [Guide](https://developers.google.com/youtube/v3/getting-started), [Video Guide](https://www.youtube.com/watch?v=-UCHsqxBqwY)
3. Use https://www.googleapis.com/youtube/v3/videos?part=status&id=[outube ID]&key=[your api key] to extract json which include all the detail info of Youtube URL status.


### Store URLs into Pandas DataFrame
In order to keep the URL status info, I decided to use Pandas DataFrame. In addition, it gives a possibility of data analysis afterwards.
1. Reverse DataFrame data order. The data are stored in reverse order. Therefore, it is better to correct it.
2. Adopted tableWidet to show the data. I used backgroud color to make it more clear. Red color means these URLs are broken. Orange color mean it is better to further check by double clicking the link.
3. save it as CSV file.
# Notes
 - Make sure you have enrolled in the course you want to check URLs.
 - Make sure the course list in your Blackboard are NOT 'Group by Term'. 
 - Before running the program, make sure the 'Edit Mode is:' OFF.
 
# URL batch checking
Check URLs and find out the broken links.
  - go to the folder '\bb_batch', double click the file 'urlChecker_UI.py'.
  - login, you should see all the courses that have enrolled in.
  - double click to select courses that need to be checked.
  - click 'Check URLs' button; that's all you need to do;
  - the program will generate 3 CSV files: _broken.csv, _check.csv, _OK.csv
# Specific URLs filtering
Go through all courses on the blackboard and find out the specific links (like proquest.com links).
  - go to the folder '\bb_find_specific_urls', double click the file 'urlChecker_UI.py'.
  - login, you should see all the courses that have enrolled in.
  - click 'Check URLs' button; that's all you need to do;
  - the program will generate a CSV file which include all the specific links you wanted. CSV file has header: Course name, Location(where the link locate), Hyperlink title, URL
  - it will generate a log file as well. 
