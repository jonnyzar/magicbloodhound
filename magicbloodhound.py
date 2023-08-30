import os
import json 
import requests
import argparse
import platform
import sys 

sistema = format(platform.system())

if (sistema == "Linux"):
	# Text colors
	normal_color = "\33[00m"
	info_color = "\033[1;33m"
	red_color = "\033[1;31m"
	green_color = "\033[1;32m"
	whiteB_color = "\033[1;37m"
	detect_color = "\033[1;34m"
	banner_color="\033[1;33;40m"
	end_banner_color="\33[00m"
elif (sistema == "Windows"):
	normal_color = ""
	info_color = ""
	red_color = ""
	green_color = ""
	whiteB_color = ""
	detect_color = ""
	banner_color=""
	end_banner_color=""

def banner():

    print (banner_color + " __  __             _        ____  _                 _ _   _                       _" + end_banner_color) 
    print (banner_color + "|  \/  | __ _  __ _(_) ___  | __ )| | ___   ___   __| | | | | ___  _   _ _ __   __| |" + end_banner_color)
    print (banner_color + "| |\/| |/ _` |/ _` | |/ __| |  _ \| |/ _ \ / _ \ / _` | |_| |/ _ \| | | | '_ \ / _` |" + end_banner_color)
    print (banner_color + "| |  | | (_| | (_| | | (__  | |_) | | (_) | (_) | (_| |  _  | (_) | |_| | | | | (_| |" + end_banner_color)
    print (banner_color + "|_|  |_|\__,_|\__, |_|\___| |____/|_|\___/ \___/ \__,_|_| |_|\___/ \__,_|_| |_|\__,_|" + end_banner_color)
    print (banner_color + "              |___/                                                                  " + end_banner_color)


def checkArgs():
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description=red_color + 'Magic BloodHound 1.0\n' + info_color)
    parser.add_argument('-f', "--file", action="store",dest='file',help="ZIP File to ingest in BloodHound")
    parser.add_argument("--host", action="store",dest='host',help="Host that runs BloodHound API in format http[s]://domain.tld:port by default: http://localhost:8080")
   
    args = parser.parse_args()
    if (len(sys.argv)==1) or args.file==False:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return args

def login(host):
    loginPayload = {
	"login_method": "secret",
        "secret": "<here_your_password>",
	"username": "admin"
    }

    response = requests.post(host+'/api/v2/login', json=loginPayload)
    response_content = response.content.decode('utf-8')
    json_obj = json.loads(response_content)
    session_token = json_obj['data']['session_token']
    return session_token

def get_json_files_in_directory(directory):
    json_files = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            json_files.append(filename)
    return json_files

def start_upload(filename, token, host):
    url = host+"/api/v2/file-upload/start"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "bhe-python-sdk 0001",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers)

    return response

def upload_data(filename, token, uploaded_id,host):
    url = host+"/api/v2/file-upload/" + str(uploaded_id)
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "http://localhost:8080/ui/administration/file-ingest",
        "Content-Type": "application/json",
        "Origin": "http://localhost:8080",
        "Connection": "close",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }


    os.system("dd if=" + filename + " of="+filename+"-bh bs=3 skip=1 > /dev/null 2>&1")

    with open(filename+"-bh", "r", encoding="iso-8859-1") as file:
        json_data = file.read()

    os.system("rm -rf " + filename + "-bh")

    response = requests.post(url, headers=headers, data=json_data)

    return response

def finish_upload_data(filename, token, uploaded_id,host):
    url = host+"/api/v2/file-upload/" + str(uploaded_id) + "/end"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "bhe-python-sdk 0001",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers)

    return response

#Main
banner()
args = checkArgs()
if (args.host):
	host = args.host
	lastchar = len(host)
	if (host[lastchar-1] == "/"):
		host = host[0:len(host)-1]
else:
	host = "http://localhost:8080"

inicio = args.file.find(".zip")
if (inicio != -1):
	os.system("unzip -q " + args.file)

current_directory = os.getcwd()
json_files = get_json_files_in_directory(current_directory)

token = login(host)
for filename in json_files:
    try:
	    response = start_upload(filename, token, host)
	    json_data = json.loads(response.text)
	    uploaded_id = json_data["data"]["id"]
	    response2 = upload_data(filename, token, uploaded_id, host)
	    print ("[+] File " + str(filename) + " uploaded successfully! BloodHound is ingesting now :)")
	    response3 = finish_upload_data(filename, token, uploaded_id, host)
    except:
            print ("[-] File " + str(filename) + " can't be upload correctly. BloodHound is not analyzing data! :(")

    
os.system("rm -rf *_*.json")
