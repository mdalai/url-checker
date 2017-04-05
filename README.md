# url-checker
Checking urls in Blackboard
# Installation:
1. python 2.7 64bit
2. pip install python-qt5
3. pip install pandas
4. pip install numpy
5. pip install requests
6. pip install webbrowser (sometimes, it is already included in the python basic)
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

# Notes
 - Make sure the course list in your Blackboard are NOT 'Group by Term'. 
 - Before running the program, make sure the 'Edit Mode is:' OFF.
