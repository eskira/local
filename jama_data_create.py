import requests
from requests.auth import HTTPBasicAuth
import sys
import json


###  使用するURLに合わせ変更してください
BASIC_URL = "https://jama.geniie.net"

### ベーシック認証のユーザー名とパスワードを設定
username1 = 'standard_pf_tool'
password1 = 'B8tNaP9F'

### OAuTH使用時は生成したクライアントID、シークレットを設定してください
client_id = 'xxxxx'
client_secret = 'xxxxx'

item_type_id_FR = 136       # Functional Requirement_STDPFのID
item_type_id_NFR = 137      # Functional Requirement_STDPFのID    

#target_project_id = 96      # CP標準PF_DEMOv2"
target_project_id = 53      # CP標準PF

target_itemtype = [                 #itemtypeのdisplayの値
    "Functional Requirement_STDPF",
    "Non-Functional Requirement_STDPF",
    "Functional Safety Requirement_STDPF",
    "Technical Safety Requirement_STDPF",
    "Change Request_STDPF",
    "Test Case_STDPF"
]
     
# --------------------------------------------
#       Jama RESR API処理
# --------------------------------------------
class JamaRest(  ):

    def __init__(self, auth_mode,url,user=None,passwd=None,clientID=None,clientSecret=None):

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
    
    def get_piclist_id( self, picklist_id ):
        get_url = self.base_url + "/rest/latest/picklists/" + str(picklist_id) + "/options"
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

    def get_itemtypes_id( self, itemtype_id ):
        get_url = self.base_url + "/rest/latest/itemtypes/" + str(itemtype_id)
        return self.get_request(get_url)
    



# ----------------------------------------------------
#             メイン処理
# ----------------------------------------------------
if __name__ == '__main__':        
    
    jama_rest = JamaRest(auth_mode='BASIC', \
        url=BASIC_URL,\
        user=username1, \
        passwd=password1)
    
    jama_rest.authenticate()
    
    # ---------------------------------------------
    #       プロジェクトリスト取得
    # ---------------------------------------------
    projects_json = jama_rest.get_projects()
    #print(json.dumps(ret_json, indent=4, sort_keys=True, separators=(',', ': ')))

    with open("./setinfo/project.json", 'w', encoding='UTF-8') as f:
        json.dump(projects_json, f, ensure_ascii=False, indent=4)      

    print ("プロジェクトリスト :")
    for curr_data in projects_json["data"]:
        name = curr_data["fields"]["name"]
    print(name)
    
    
    # ---------------------------------------------
    #       PickListリスト取得
    # ---------------------------------------------
    # [Output] picklist_json: 指定したitemtypeの定義リスト (picklist.json)
    
    picklist_json = jama_rest.get_piclists(0, 50)
    
    count_total = 0
    index_max = 0
    count_now = 0
    while count_total < index_max or index_max == 0:     # 初回か、総データ数取得完了まで繰返す
    
        if count_total == 0:
            #  初回のitemデータ(0~50個目まで)取得 
            ret_json = jama_rest.get_piclists(0, 50)          #itemデータ取得 (startAt: 0 maxResult: 50)
            index_max = ret_json["meta"]["pageInfo"]["totalResults"]        # FR全データ数
            count_now = ret_json["meta"]["pageInfo"]["resultCount"]         # 今回取得したデータ数 
            
            picklist_json = ret_json
            
            #print("[LOG] FR総数:  " + str(index_max))
            #print("[LOG] 初回取得データ数:  " + str(count_total))
        else:
            # 2回目(51個目以上の時)以降、総データ数取得完了までの繰返し 
            ret_json = jama_rest.get_piclists((count_total-1), 50)
            count_now = ret_json["meta"]["pageInfo"]["resultCount"]         # 今回取得したデータ数 
             
            # 取得したデータのフィルタ判定
            for i in range(count_now):
                data = ret_json["data"][i]
                picklist_json["data"].append(data)      # itemデータ追加
                        
        count_total += count_now                                        # ここまでの取得データ総数   
    
    with open("./setinfo/picklist.json", 'w', encoding='UTF-8') as f:
        json.dump(picklist_json, f, ensure_ascii=False, indent=4)   



    # ---------------------------------------------
    #     指定したitemtypeのリスト作成 
    # ---------------------------------------------
    # [Input] target_itemtype: 使用するItemType名のリスト
    # [Output] itemtypelist_json: 指定したitemtypeの定義リスト (itemtypelist.json)
    
        
    count_total = 0
    index_max = 0
    count_now = 0
    while count_total < index_max or index_max == 0:     # 初回か、総データ数取得完了まで繰返す
    
        if count_total == 0:
            #  初回のitemデータ(0~50個目まで)取得 
            ret_json = jama_rest.get_itemtypes(target_project_id, 0, 50)          #itemデータ取得 (startAt: 0 maxResult: 50)
            index_max = ret_json["meta"]["pageInfo"]["totalResults"]        # FR全データ数
            count_now = ret_json["meta"]["pageInfo"]["resultCount"]         # 今回取得したデータ数 
            
            itemtypelist_all_json = ret_json
            
            #print("[LOG] FR総数:  " + str(index_max))
            #print("[LOG] 初回取得データ数:  " + str(count_total))
        else:
            # 2回目(51個目以上の時)以降、総データ数取得完了までの繰返し 
            ret_json = jama_rest.get_itemtypes(target_project_id, (count_total-1), 50)
            count_now = ret_json["meta"]["pageInfo"]["resultCount"]         # 今回取得したデータ数 
             
            # 取得したデータのフィルタ判定
            for i in range(count_now):
                data = ret_json["data"][i]
                itemtypelist_all_json["data"].append(data)      # itemデータ追加
                        
        count_total += count_now                                        # ここまでの取得データ総数   
    
    print(str(len(target_itemtype)))   
    
    itemtypelist_json = []
    for i in range(len(target_itemtype)):
  
        #print(target_itemtype[i])
        num = len(itemtypelist_all_json["data"])
        for j in range(num):
            if str(itemtypelist_all_json["data"][j]["display"]) == str(target_itemtype[i]):
                print(itemtypelist_all_json["data"][j]["display"] )

                itemtypelist_json.append(itemtypelist_all_json["data"][j])
    
    with open("./setinfo/itemtypelist.json", 'w', encoding='UTF-8') as f:
        json.dump(itemtypelist_json, f, ensure_ascii=False, indent=4)       #Itemtypeリスト出力
           
    

    # ---------------------------------------------
    #    PickListに値の定義追加したリスト作成
    # ---------------------------------------------
    # [Input] itemtypelist_json: 使用するItemtypeの定義リスト (itemtypelist.json)
    # [Input] picklist_json:  PickList定義のリスト(picklist.json)
    # [Output] picklist_spec_json: リストの値（選択肢）の定義を追加したPickList定義リスト (picklist_spec.json)
    
    # 使用するitemtypeで使われるPickList IDをリストアップ
    picklist_id = []
    
    #print("itemtypelist_json: " + str(len(itemtypelist_json)))     [Debug]
    for i in range(len(itemtypelist_json)):
        for j in range(len(itemtypelist_json[i]["fields"])):
            
            flag_id_exist = False
            #print("itemtypelist_json[i]: " + str(len(itemtypelist_json[i]["fields"])))
            if "pickList" in itemtypelist_json[i]["fields"][j]:
                
                # 次のfieldsのPickList Idのリストアップ判定
                for x in range(len(picklist_id)):
                    
                    #print("picklist_id[x]: " + str(picklist_id[x]) + "    itemtypelist_json: " + str(itemtypelist_json[i]["fields"][j]["pickList"]))
                    
                    if int(picklist_id[x]) == int(itemtypelist_json[i]["fields"][j]["pickList"]) :
                        flag_id_exist = True
                        #print("ID一致")
                        break                                              
                
                if flag_id_exist == False:
                    data = itemtypelist_json[i]["fields"][j]["pickList"]
                    picklist_id.append(str(data))
                    #print( "picklist_id_num: " + str(len(picklist_id)) + "    picklist_id:  " + str((itemtypelist_json[i]["fields"][j]["pickList"] )))

                    
    # 各PickListのリストの値（選択肢）の定義を追加
    picklist_spec_json = []
    
    # picklist_json:  PickList定義のリスト(picklist.json)
    print(len(picklist_id))
    for i in range(len(picklist_id)):
        
        data_picklist_json = {}     #初期化
        #print(len(picklist_json))
        
        for j in range(len(picklist_json["data"])):
            if int(picklist_id[i]) == int(picklist_json["data"][j]["id"]):    # PickList IDが一致
                
                print("picklist_id:" + str(picklist_id[i]) + "    picklist_json: " + str(picklist_json["data"][j]["id"]))
                
                ret_json = jama_rest.get_piclist_id(picklist_id[i])     # Jamaからpicklist_id[i]のデータ定義を取得
                
                data_picklist_json["picklist_id"] = picklist_json["data"][j]["id"]
                data_picklist_json["picklist_name"] = picklist_json["data"][j]["name"] 
                data_picklist_json["picklist_description"] = picklist_json["data"][j]["description"]      
                data_picklist_json["data"] = ret_json["data"]           # PickListの値の追加
                
                picklist_spec_json.append(data_picklist_json)
                break  
    
    with open("./setinfo/picklist_spec.json", 'w', encoding='UTF-8') as f:
        json.dump(picklist_spec_json, f, ensure_ascii=False, indent=4)       # リストの値（選択肢）の定義を追加したPickList出力
        
           
    # -------------------------------------------------------
    #   field Label(表示名)-name(フィールド名)変換用データ作成
    # -------------------------------------------------------
    # [Input] itemtypelist_json: 使用するItemtypeの定義リスト (itemtypelist.json)
    # [Input] picklist_spec_json: リストの値（選択肢）の定義を追加したPickList定義リスト (picklist_spec.json)
    # [Output] field_info_json: フィールド要素の表示名⇔フィールド名・ID判定用データ
    
    field_info_json = []
    
    for i in range(len(itemtypelist_json)):
         
        itemid = itemtypelist_json[i]["id"]
        itemname = itemtypelist_json[i]["display"]
            
        for a in range(len(itemtypelist_json[i]["fields"])):         
            
            # Field内データの判定
            field_data = {}
            
            key = "field_id_" + str(itemname)
            
            # 同じFiled要素（フィールド名）の定義の有無チェック（他ItemTypeの定義有無）
            # 　※同じField要素の定義がある場合、ItemTypeごとのIDのみ追加する
            flag_fieldname_exist = False
            data = str(itemtypelist_json[i]["fields"][a]["name"])
            if ("$" in data) == True:
                name_id = str(itemtypelist_json[i]["fields"][a]["name"]) 
                target = '$'
                idx = name_id.find(target)
                name = name_id[:idx]            # フィールド名抽出（ItemTypeのIDを除く）
                print(str(data) + "  $より前を取出し: " + str(name))
            else:
                name = itemtypelist_json[i]["fields"][a]["name"]
                                    
            if len(field_info_json) > 0:
                for x in range(len(field_info_json)):                  
                    if itemtypelist_json[i]["fields"][a]["label"] == field_info_json[x]["field_label"]: # 同じField名の定義あり
                        flag_fieldname_exist = True  
                        field_info_json[x][str(key)] = itemtypelist_json[i]["fields"][a]["id"]          # フィールドのIDを設定
            
            field_data["field_name"] = name                         # フィールド名を設定
            if flag_fieldname_exist == False:
                field_data["field_label"] = itemtypelist_json[i]["fields"][a]["label"]   # フィールドの表示名
                field_data[str(key)] = itemtypelist_json[i]["fields"][a]["id"]         # フィールドのIDを設定
                field_info_json.append(field_data)          # Fieldデータ追加
                
    with open("./setinfo/fields_info.json", 'w', encoding='UTF-8') as f:
        json.dump(field_info_json, f, ensure_ascii=False, indent=4)       # リストの値（  
    


    # ---------------------------------------------
    #    itemリスト取得 Functional Requirement_STDPF
    # ---------------------------------------------
    #itemslist_json = jama_rest.get_items_by_itemtype(target_project_id, item_type_id_FR, 0, 50)

    count_total = 0
    index_max = 0
    count_now = 0
    while count_total < index_max or index_max == 0:     # 初回か、総データ数取得完了まで繰返す
    
        if count_total == 0:
            #  初回のitemデータ(0~50個目まで)取得 
            ret_json = jama_rest.get_items_by_itemtype(target_project_id, item_type_id_FR, 0, 50)    #itemデータ取得 (startAt: 0 maxResult: 50)
            index_max = ret_json["meta"]["pageInfo"]["totalResults"]        # FR全データ数
            count_now = ret_json["meta"]["pageInfo"]["resultCount"]         # 今回取得したデータ数 
            
            itemslist_fr_json = ret_json
            
            #print("[LOG] FR総数:  " + str(index_max))
            #print("[LOG] 初回取得データ数:  " + str(count_total))
        else:
            # 2回目(51個目以上の時)以降、総データ数取得完了までの繰返し 
            ret_json = jama_rest.get_items_by_itemtype(96, item_type_id_FR, (count_total-1), 50)
            count_now = ret_json["meta"]["pageInfo"]["resultCount"]         # 今回取得したデータ数 
             
            # 取得したデータのフィルタ判定
            for i in range(count_now):
                data = ret_json["data"][i]
                itemslist_fr_json["data"].append(data)      # itemデータ追加
                        
        count_total += count_now                                        # ここまでの取得データ総数   

    with open("./setinfo/itemslist_FR.json", 'w', encoding='UTF-8') as f:
        json.dump(itemslist_fr_json, f, ensure_ascii=False, indent=4)   





        

        
        
        
        
            
    
    
    
    
    
    

    
    
    