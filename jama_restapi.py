import tkinter as tk
import tkinter.ttk as ttk
import requests
from requests.auth import HTTPBasicAuth
import sys
import os
import json
import jama_user_set


###  使用するURLに合わせ変更してください
BASIC_URL = "https://jama.geniie.net"

### ベーシック認証のユーザー名とパスワードを設定
username1 = 'xxxxx'
password1 = 'xxxxx'

### OAuTH使用時は生成したクライアントID、シークレットを設定してください
client_id = 'xxxxx'
client_secret = 'xxxxx'


     
# --------------------------------------------
#       Jama RESR API処理
# --------------------------------------------
class JamaRest(  ):

    def __init__(self, auth_mode,url,user=None,passwd=None,clientID=None,clientSecret=None):
        
        if os.path.isfile("./setinfo/jama_init.json") == False:   
            status = jama_user_set.account_check("init")
        else:
            pass
        
        with open('./setinfo/jama_init.json', 'r', encoding='utf-8') as f:
            json_load = json.load(f)
            
        user = json_load["username"]
        passwd = json_load["password"]
        print("user:" + str(user) + "    password:" + str(passwd))
                
        self.auth_mode=auth_mode
        self.base_url = url
        self.user = user
        self.passwd = passwd
        self.clientID = clientID
        self.clientSecret=clientSecret
        self.session = requests.Session()
        self.verify = None
        self.proxies = None
        self.access_token = None
        self.headers = None

    # ユーザ名・パスワードの再設定処理
    def user_info_reset(self):
 
        status = jama_user_set.account_check("reset")    
        with open('./setinfo/jama_init.json', 'r', encoding='utf-8') as f:
            json_load = json.load(f)
            
        user = json_load["username"]
        passwd = json_load["password"]
        print("user:" + str(user) + "    password:" + str(passwd))  
              
        self.user = user
        self.passwd = passwd
        


    def authenticate( self ):
    
        if self.auth_mode == 'OAUTH':
            return self.oauth_authenticate()
        self.session.auth = HTTPBasicAuth( username1, password1 )
        return True
        
    def oauth_authenticate( self ):
        oauth_url = self.base_url + "/rest/oauth/token"
        ret = self.session.post(oauth_url, \
            auth=HTTPBasicAuth(self.clientID, self.clientSecret),\
            data={"grant_type": "client_credentials"})
            
        self.access_token = json.loads(ret.text)['access_token']
        self.headers =  {"Authorization": "Bearer {}".format(self.access_token)}
        return True

    def get_request( self, req_url ):
        #print(req_url)                 [Debug]
        ret = self.session.get(req_url, headers=self.headers)
        if ret.status_code >= 400:
            sys.exit("[ERROR] get_request HTTP STATUS CODE : " + str(ret))
        #print(ret.status_code)         [Debug]
        return json.loads(ret.text)

    def put_request( self, req_url, payload ):
        ret = self.session.put(req_url, headers=self.headers, json=payload)
        if ret.status_code >= 400:
            sys.exit("[ERROR] put_request HTTP STATUS CODE : " + str(ret))
        return 0
    
    def get_projects( self ):
        get_url = self.base_url + "/rest/latest/projects"
        return self.get_request(get_url)

    def get_project( self, proj_ID ):
        get_url = self.base_url + "/rest/latest/projects/"  + str(proj_ID)
        return self.get_request(get_url)

    def get_piclists( self, start_at, max_result ):
        get_url = self.base_url + "/rest/latest/picklists?startAt=" + str(start_at) + "&maxResults=" + str(max_result)
        return self.get_request(get_url)
    
    def get_itemtypes( self, proj_ID, start_at, max_result ):
        get_url = self.base_url + "/rest/latest/projects/" + str(proj_ID) + "/itemtypes?startAt=" + str(start_at) + "&maxResults=" + str(max_result)
        return self.get_request(get_url)

    def get_items_by_type( self, proj_ID, item_type ):
        get_url = self.base_url + "/rest/latest/abstractitems?project=" + str(proj_ID) + "&itemType=" + str(item_type)
        return self.get_request(get_url)
       
    def get_items_by_itemtype( self, proj_ID, itemtype, start_at, max_result):    
        get_url = self.base_url + "/rest/latest/abstractitems?project=" + str(proj_ID) + "&itemType=" + str(itemtype) + "&startAt=" + str(start_at) + "&maxResults=" + str(max_result)
        return self.get_request(get_url)


    

        