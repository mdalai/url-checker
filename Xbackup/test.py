import sys 
import os
sys.path.append(os.path.relpath("common"))
from url_status import youtubeStatus,getYoutubeID,checkUrlStatus


# https://youtu.be/x_FdGxvLwW0
y_id = "x_FdGxvLwW0"

if __name__ == "__main__":

    status,embeddagle,title  = youtubeStatus(y_id)
    print status,embeddagle,title
