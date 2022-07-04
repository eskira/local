from glob import glob
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import openpyxl
from openpyxl.styles import Alignment
import os
import pprint
#import requests
import sys
#from requests.auth import HTTPBasicAuth
import json
import jama_restapi


item_type_id_FR = 136      # Functional Requirement_STDPFのID
item_type_id_NFR = 137      # Functional Requirement_STDPFのID   


    
# -----------------------------------
#           APP用関数
# -----------------------------------

#------ 変換処理終了メッセージ ------     
def msg_end_info():
    ret = messagebox.showinfo("info", "変換処理が終了しました")
    print(ret)
    if ret == "ok":
        root.destroy()  #ウィンドウ閉じる


#------ warningメッセージ ------     
def msg_warning(x):
    global flag_destroy
    
    ret = messagebox.showwarning("warning",str(x))
    print("[LOG]  warning: " + str(x))
    if ret == "ok":
        flag_destroy = True
        root.destroy()  #ウィンドウ閉じる

    
#---------- 画面の入力フォームの前回値取込み -----------
def entry_insert():
    if os.path.isfile("./setinfo/collect_init.json") == True:
        with open('./setinfo/collect_init.json', 'r', encoding='utf-8') as f:
            json_load = json.load(f)
            
        pprint.pprint(json_load)
        en_prj.insert(tk.END, str(json_load["prj_name"]))
        en_filter1.insert(tk.END, str(json_load["domain"]))
        en_filter2.insert(tk.END, str(json_load["reqkind"]))
        en_filter3.insert(tk.END, str(json_load["product"]))
        en_filter4.insert(tk.END, str(json_load["remarks"]))
        en_filter5.insert(tk.END, str(json_load["keyword"]))
        
        
#------------------ 入力ワードのチェック -------------------
def check_input_word(datakind, in_word):
    
    #print(datakind)         # [Debug] PickListの種類
    #print(in_word)          # [Debug] 入力データ

    with open('./setinfo/picklist_ivi.json', 'r', encoding='utf-8') as f:   #JamaのPickListの定義ファイル読み込み
        json_load = json.load(f)
                
    ret_id = 0xFF       # 初期値： 無効値(0xFF)
    for i in range(json_load["meta"]["pageInfo"]["totalResults"]):
        
        #print("PickList名：  " + str(json_kind_load["data"][i]["name"]))     # [Debug]
        #print(json_load["data"][i]["totalResults"])
        
        if json_load["data"][i]["name"] == str(datakind):
            
            for j in range(json_load["data"][i]["totalResults"]):
                
                kind = json_load["data"][i]["datainfo"][j]["name"]
                print(str(datakind) + ":  " + str(kind))                    # [Debug] 照合した値の確認
                                   
                # 入力データとPickList定義との照合（定義されていない不正データでないか確認）
                if in_word == kind:
                    ret_id = json_load["data"][i]["datainfo"][j]["id"]
                    #print(str(datakind) + "のID:  " + str(ret_id))          # [Debug] 照合した値のIDの確認
                    break
            break
    return ret_id


#------------- itemデータ取得 -------------
def get_target_project_items(project_id, item_type_id):
        
    # データ処理用の変数定義
    count_max = 0    # itemの総数
    count_total = 0        # itemの取出した数の合計
    count_now = 0    # itemの今回取出した数
        
                
    # -------- Jamaからitemデータ取得 ---------
    while count_total < count_max or count_max == 0:     # 初回か、総データ数取得完了まで繰返す
        
        if count_total == 0:
            #  初回のitemデータ(0~50個目まで)取得 
            ret_json = jama_rest.get_items_by_itemtype(project_id, item_type_id, 0, 50)  #itemデータ取得 (startAt: 0 maxResult: 50)
            count_max = ret_json["meta"]["pageInfo"]["totalResults"]    # FR全データ数
            item_list_json = ret_json
            
            # 取得したデータのフィルタ判定
            for i in range(count_now):
                data = ret_json["data"][i]
                item_list_json["data"].append(data)      # itemデータ追加
            
                        
            #print("[LOG] FR総数:  " + str(count_max))
            #print("[LOG] 初回取得データ数:  " + str(count_total))
        else:
            # 2回目(51個目以上の時)以降、総データ数取得完了までの繰返し 
            ret_json = jama_rest.get_items_by_itemtype(project_id, item_type_id, (count_total-1), 50)  # itemデータ取得
        
        count_now = ret_json["meta"]["pageInfo"]["resultCount"]         # 今回取得したデータ数 
        count_total += count_now                                        # ここまでの取得データ総数
        
        
        
    #    print("追加取得データ数:  " + str(count_now))  
    #    print("ここまでの取得データ数:  " + str(count_fr))  
        
        # 取得したデータをjsonデータに追加
        for i in range(count_now):
            data_add = ret_json["data"][i]
            item_list_json["data"].append(data_add)      # itemデータ追加
            
        item_list_json["meta"]["pageInfo"]["resultCount"]  = count_total 
        print("[LOG] jsonデータのresultCount:  " + str(item_list_json["meta"]["pageInfo"]["resultCount"])) 
        
    return item_list_json
            



# ----------------------------------------------------
#             要件収集・変換処理
# ----------------------------------------------------
def jama_to_shm_main(event):
    
  
#    text_msg.set(str(event.widget["text"]) + ":  実行中")
    button1["text"] = "実行中"
    root.update()
    
    global item_type_id_FR      # Functional Requirement_STDPFのID
    global item_type_id_NFR     # Functional Requirement_STDPFのID 
    
    # ----------- 入力取得 -------------
    input_prj_name = en_prj.get()           # プロジェクト名の入力データ取得
    input_domain = en_filter1.get()         # 担当ドメイン（機能Gr）名の入力データ取得
    input_reqkind = en_filter2.get()        # 要求種別の入力データ取得
    input_product = en_filter3.get()        # 製品プロジェクト名の入力データ取得
    input_remarks = en_filter4.get()        # 備考(remarks)の入力データ取得
    input_keyword = en_filter5.get()        # 任意キーワードの入力データ取得
    
    print("[LOG] 入力 プロジェクト名: " + str(input_prj_name))
    print("[LOG] 入力 ドメイン（機能Gr）: " + str(input_domain))
    print("[LOG] 入力 要件種別: " + str(input_reqkind))
    print("[LOG] 入力 製品プロジェクト: " + str(input_product))
    print("[LOG] 入力 備考(remarks): " + str(input_remarks))
    print("[LOG] 入力 キーワード: " + str(input_keyword))
    


    # ---------- プロジェクト情報取得 -------------
    ret_prj_json = jama_rest.get_projects()
    #print(json.dumps(ret_prj_json, indent=4, sort_keys=True, separators=(',', ': ')))

    flag_prj_name_chk = False       # 初期設定: Jamaプロジェクト名 無効
    for curr_data in ret_prj_json["data"]:
        
        if curr_data["fields"]["name"] == str(input_prj_name):
            target_prj_name = curr_data["fields"]["name"]              # Jamaプロジェクト名 取得
            target_project_key = curr_data["fields"]["projectKey"]     # Project Key 取得
            target_prj_id = curr_data["id"]                            # ID 取得
            flag_prj_name_chk = True                                   # Jamaプロジェクト名 有効
            print("[LOG] 指定したプロジェクトの情報：   Project Key: " + target_project_key + "    ID: " + str(target_prj_id))
            
    if flag_prj_name_chk == False:
        print("[LOG] 入力したプロジェクト名が不一致")     # エラーメッセージ出力
    
    
    
    reqkind_id = 0          # 要求種別のID 初期設定
    product_id = 0          # 製品プロジェクトのID 初期設定
    domain_id = 0           # 担当ドメイン（機能Gr）のID 初期設定
    
    # ------------- 入力データチェック ---------------
    if os.path.isfile("./setinfo/picklist_ivi.json") == True:       #PickList定義ファイルの有無を確認
        with open('./setinfo/picklist_ivi.json', 'r', encoding='utf-8') as f:
            json_kind_load = json.load(f)
            
        # --- 要求種別の入力値チェック ---
        flag_reqkind_chk = False                  # 初期設定:  要件種別 無効 
        if input_reqkind != "":
            
            ret_target_id = check_input_word("要件種別_STDPF", str(input_reqkind))
            
            print("入力チェック結果: " + str(ret_target_id))    # [Debug] 入力チェック結果
            
            if ret_target_id != 0xFF:           # 無効値でない
                reqkind_id = ret_target_id
                flag_reqkind_chk = True         # 要求種別  有効
                print("[LOG] 要求種別ID:  " + str(reqkind_id)) 
            else:
                print("[LOG] 入力した要求種別が不一致")     # エラーメッセージ出力   
        else:
            print("[LOG] 要求種別の入力なし")           # エラーメッセージ出力   
                                                       
                    
        # --- 製品プロジェクトの入力値チェック ---
        flag_product_chk = False        # 初期設定:  製品プロジェクト 無効
        if input_product != "":
            
            ret_target_id = check_input_word("Project Name_STDPF", str(input_product))
            
            if ret_target_id != 0xFF:           # 無効値でない
                product_id = ret_target_id
                flag_product_chk = True         # 製品プロジェクト 有効
                print("[LOG] 製品プロジェクトのID:  " + str(product_id)) 
            else:
                print("[LOG] 入力した製品プロジェクトが不一致")     # エラーメッセージ出力        
        else:
            #msg_warning("製品プロジェクトの入力なし")           # エラーメッセージ出力
            print("[LOG] 製品プロジェクトの入力なし") 
              
            
        # --- 担当ドメインの入力値チェック ---
        flag_domain_chk = False         # 初期設定:  担当ドメイン（機能Gr）  無効
        if input_domain != "":
            
            ret_target_id = check_input_word("担当ドメイン_STDPF", str(input_domain))
            
            if ret_target_id != 0xFF:       # 無効値でない
                domain_id = ret_target_id
                flag_domain_chk = True          # 担当ドメイン（機能Gr） 有効
                print("[LOG] 担当ドメイン（機能Gr）のID:  " + str(domain_id)) 
            else:
                print("[LOG] 入力した担当ドメイン（機能Gr）が不一致")       # エラーメッセージ出力 
        else:
            print("[LOG] 担当ドメイン（機能Gr）の入力なし")                 # エラーメッセージ出力 
                        
    else:
        print("[LOG] warning: picklist_ivi.jsonファイルがありません")      # エラーメッセージ出力
 


    # ---- 入力データを保存する ----
    # if os.path.isfile("./setinfo/collect_init.json") == False:
    data = strvar_mode.get()
    ret_init_json = { "prj_name": str(input_prj_name), \
                        "domain": str(input_domain), \
                        "reqkind": str(input_reqkind), \
                        "product": str(input_product), \
                        "remarks": str(input_remarks), \
                        "keyword": str(input_keyword), \
                        "mode": str(data) }
    # 入力データをJSONファイルに保存
    with open('./setinfo/collect_init.json', 'w', encoding='UTF-8') as f:
        json.dump(ret_init_json, f, ensure_ascii=False, indent=4)    
            


    # ---- 入力データ（Jamaプロジェクト名・フィルタ条件）チェック結果の確認 ----
    if flag_reqkind_chk == True \
        and flag_domain_chk == True \
            and flag_product_chk == True \
            and flag_prj_name_chk == True:    # 必須入力項目が有効の場合のみ実施

        # --------- 機能要件（Functional Requirement_STDPF）の収集  ----------   
        item_json_FR = get_target_project_items(target_prj_id, item_type_id_FR)
        #pprint.pprint(item_json_FR)     # [Debug] JSON形式の出力データを表示
        
        # --------- 非機能要件（Functional Requirement_STDPF）の収集  ----------   
        item_json_NFR = get_target_project_items(target_prj_id, item_type_id_NFR)
        #pprint.pprint(item_json_NFR)     # [Debug] JSON形式の出力データを表示
                
        
        # item情報リストのJSONファイルに書込み 
        time = str(item_json_FR["meta"]["timestamp"])
        s = time.find(":")
        date = time[:s]
        #print(str(date))
        
        filename = "./data/itemlist_FR_" + str(target_prj_name) + "_" + str(input_domain) + "_" + str(date) + ".json"
        with open(str(filename), 'w', encoding='UTF-8') as f:
            json.dump(item_json_FR, f, ensure_ascii=False, indent=4)

        filename = "./data/itemlist_NFR_" + str(target_prj_name) + "_" + str(input_domain) + "_" + str(date) + ".json"
        with open(str(filename), 'w', encoding='UTF-8') as f:
            json.dump(item_json_NFR, f, ensure_ascii=False, indent=4)  
        
            
        item_json_all = item_json_FR
        
        
        num = int(item_json_NFR["meta"]["pageInfo"]["totalResults"]) + int(item_json_FR["meta"]["pageInfo"]["totalResults"])
        item_json_all["meta"]["pageInfo"]["totalResults"] = num             # 機能要求と非機能要求の合計データ数に更新
        
        for i in range(item_json_NFR["meta"]["pageInfo"]["totalResults"]):  # 非機能要求のデータを追加
            data_add = item_json_NFR["data"][i]
            item_json_all["data"].append(data_add)      # itemデータ追加
        
        filename = "./data/itemlist_all_" + str(target_prj_name) + "_" + str(input_domain) + "_" + str(date) + ".json"
        with open(str(filename), 'w', encoding='UTF-8') as f:
            json.dump(item_json_all, f, ensure_ascii=False, indent=4)  
     
        
        #text_msg.set("終了")
        button1["text"] = "終了"
        root.update()
        msg_end_info()
    else:
        warning_text = ""
        msg_text = ""
        
        if flag_prj_name_chk == False:
            warning_text = "入力値が不正値or不足しています"
            text_msg_prj.set("Jamaプロジェクト名: NG")   
        else:
            text_msg_prj.set("Jamaプロジェクト名: OK")   
            
        if flag_reqkind_chk == False:
            warning_text = "入力値が不正値or不足しています"
            text_msg_reqkind.set("要求種別: NG")   
        else:
            text_msg_reqkind.set("要求種別: OK")               
            
        if flag_domain_chk == False:
            warning_text = "入力値が不正値or不足しています"
            text_msg_domain.set("担当ドメイン（機能Gr）: NG")   
        else:
            text_msg_domain.set("担当ドメイン（機能Gr）: OK")               
        
        if flag_product_chk == False:
            warning_text = "入力値が不正値or不足しています"
            text_msg_product.set("製品プロジェクト: NG")   
        else:
            text_msg_product.set("製品プロジェクト: OK")  
                         
        button1["text"] = "停止"
        root.update()
        msg_warning(str(warning_text))
        
        



# ----------------------------------------------------
#             メイン処理
# ----------------------------------------------------
if __name__ == '__main__':        
    
    jama_rest = jama_restapi.JamaRest(auth_mode='BASIC', \
        url=jama_restapi.BASIC_URL,\
        user=jama_restapi.username1, \
        passwd=jama_restapi.password1)
    
    jama_rest.authenticate()
    
        
    #------ ウィジェット定義 ------   
    root = tk.Tk()
    root.title("Jama出力ファイルのSHMフォーマット変換")
    root.geometry("805x560")

    
    # -----------------------------------
    #     ウィジェット用 Style定数
    # -----------------------------------
    font_lb1 = ("Yu Gothic UI", 12)
    font_tytle = ("Yu Gothic UI", 14, "bold")
    font_lb3 = ("Yu Gothic UI", 14)
    font_bt1 = ("Yu Gothic UI", 14)
    font_run_msg = ("Yu Gothic UI", 10)
    style_bt = ttk.Style()
    style_bt.configure("bt1.TButton", font=("Yu Gothic UI", 14))

    
    # -- 構成するFrame定義 -- 
    frame1 = ttk.Frame(root,height=150, width=450, relief="ridge", borderwidth=3)
    frame2 = ttk.Frame(root,height=220, width=780, relief="ridge", borderwidth=3)
    frame3 = ttk.Frame(root,height=150, width=780, relief="flat", borderwidth=3)
    frame4 = ttk.Frame(root,height=150, width=310, relief="ridge", borderwidth=3)

    # -- Frameに配置する要素定義 --      
    lb_project_msg1 = tk.Label(frame1, text="要件抽出の対象プロジェクトの指定", font=font_tytle)
    lb_en_prj = tk.Label(frame1, text="Jamaプロジェクト名", font=font_lb1)
    en_prj = ttk.Entry(frame1, text="Jamaプロジェクト名入力", font=font_lb1)

    lb_filter_msg1 = tk.Label(frame2, text="要件のフィルタ条件の入力", font=font_tytle)
    lb_filter1 = tk.Label(frame2, text="担当ドメイン（機能Gr）", font=font_lb1)
    en_filter1 = ttk.Entry(frame2, text="担当ドメイン（機能Gr）入力", font=font_lb1)
    lb_filter2 = tk.Label(frame2, text="要件種別", font=font_lb1)
    en_filter2 = ttk.Entry(frame2, text="要件種別入力", font=font_lb1)
    lb_filter3 = tk.Label(frame2, text="製品プロジェクト", font=font_lb1)
    en_filter3 = ttk.Entry(frame2, text="製品プロジェクト入力", font=font_lb1)
    
    lb_filter4 = tk.Label(frame2, text="備考(remarks)", font=font_lb1)
    en_filter4 = ttk.Entry(frame2, text="備考(remarks)入力", font=font_lb1)
    lb_filter5 = tk.Label(frame2, text="任意キーワード", font=font_lb1)
    en_filter5 = ttk.Entry(frame2, text="任意キーワード入力", font=font_lb1)
    

    # Frame3
    button1 = ttk.Button(frame3, text="SHM形式ファイル生成", style="bt1.TButton", width=20, command=jama_to_shm_main)
    #button1.bind("<ButtonPress>", jama_to_shm_main)
    bt_userreset = ttk.Button(frame3, text="登録情報リセット", style="bt1.TButton", width=15, command=jama_rest.user_info_reset)
    
    text_msg_prj = tk.StringVar(frame3)
    text_msg_prj.set("") 
    lb_msg_prj = ttk.Label(frame3, textvariable=text_msg_prj, font=font_run_msg)
    
    text_msg_reqkind = tk.StringVar(frame3)
    text_msg_reqkind.set("")    
    lb_msg_reqkind = ttk.Label(frame3, textvariable=text_msg_reqkind, font=font_run_msg)
    
    text_msg_domain = tk.StringVar(frame3)
    text_msg_domain.set("")    
    lb_msg_domain = ttk.Label(frame3, textvariable=text_msg_domain, font=font_run_msg)
    
    text_msg_product = tk.StringVar(frame3)
    text_msg_product.set("")    
    lb_msg_product = ttk.Label(frame3, textvariable=text_msg_product, font=font_run_msg)
        
    #lb0 = tk.Label(frame3, text="『SHM形式ファイル生成』でJamaから要件収集し変換を実行します", font=font_lb1, foreground="red")
        
    
    # Frame4の定義
    lb_func_msg1 = tk.Label(frame4, text="モード選択", font=font_tytle)
    
    #strvar_mode = tk.StringVar()
    #strvar_mode.set({"jama→SHM新規生成", "jama変更のSHM反映", "SHM変更のjama反映"})
    strvar_mode = tk.StringVar()
    strvar_mode.set("")
    style_rb = ttk.Style()
    style_rb.configure("rb1.TRadiobutton", font=("Yu Gothic UI", 14), )
    rb_mode1 = ttk.Radiobutton(frame4, text="jama→SHM新規生成", style="rb1.TRadiobutton", value="new", variable=strvar_mode)
    rb_mode2 = ttk.Radiobutton(frame4, text="変更反映 jama→SHM", style="rb1.TRadiobutton", value="change_JtoS", variable=strvar_mode)
    rb_mode3 = ttk.Radiobutton(frame4, text="変更反映 SHM→jama", style="rb1.TRadiobutton", value="change_StoJ", variable=strvar_mode)


    # -- 画面の入力フォームの前回値取込み --
    if os.path.isfile("./setinfo/collect_init.json") == True:
        with open('./setinfo/collect_init.json', 'r', encoding='utf-8') as f:
            json_load = json.load(f)
        
        en_prj.insert(tk.END, str(json_load["prj_name"]))
        en_filter1.insert(tk.END, str(json_load["domain"]))
        en_filter2.insert(tk.END, str(json_load["reqkind"]))
        en_filter3.insert(tk.END, str(json_load["product"]))
        en_filter4.insert(tk.END, str(json_load["remarks"]))
        en_filter5.insert(tk.END, str(json_load["keyword"]))
        strvar_mode.set(str(json_load["mode"]))
    #    pprint.pprint(json_load)


    # -- Frame1 内の要素の配置 --
    lb_project_msg1.place(x=10, y=10)   
    lb_en_prj.place(x=20, y=60)
    en_prj.place(x=170, y=60)

    # -- Frame2 内の要素の配置 --
    lb_filter_msg1.place(x=10, y=10)
    lb_filter1.place(x=30, y=60)
    en_filter1.place(x=200, y=60)
    lb_filter2.place(x=400, y=60)
    en_filter2.place(x=530, y=60)

    lb_filter3.place(x=30, y=100)
    en_filter3.place(x=200, y=100)
    lb_filter4.place(x=400, y=100)
    en_filter4.place(x=530, y=100)
    lb_filter5.place(x=30, y=140)
    en_filter5.place(x=200, y=140)
    
    # -- Frame3内の要素の配置 --       
    button1.place(x=200, y=10)
    bt_userreset.place(x=600, y= 90)
    lb_msg_prj.place(x=60, y=60)
    lb_msg_reqkind.place(x=60, y=80)
    lb_msg_domain.place(x=60, y=100)
    lb_msg_product.place(x=60, y=120)
    
    
    # -- Frame4内の要素の配置 --         
    lb_func_msg1.place(x=10, y=10)
    rb_mode1.place(x=30, y= 40)
    rb_mode2.place(x=30, y= 70)
    rb_mode3.place(x=30, y= 100)
    

    # -- Frameの配置 -- 
    frame1.grid(row=0, column=0, pady=5, padx=5)
    frame4.grid(row=0, column=1, pady=5, padx=5)
    frame2.grid(row=1, columnspan=2, pady=5, padx=10)
    frame3.grid(row=2, columnspan=2, pady=5, padx=10)

    root.mainloop()
    
    
    

