import tkinter as tk
import tkinter.ttk as ttk
import json
import os


userinfo_set_result = False     # ユーザ情報登録の確認結果
userinput_wd_exist = False      # ユーザ情報入力画面の有無
       

def entry_get(en_user, en_pwd):
    global userinfo_set_result
    
    in_user = en_user
    in_pwd = en_pwd
    
    if in_user != "" and in_pwd != "":
        username = in_user
        password = in_pwd
        
        # 入力データをJSONファイルに保存   
        init_json = { "username": str(username), "password": str(password) }
        with open('./setinfo/jama_init.json', 'w', encoding='UTF-8') as f:
            json.dump(init_json, f, ensure_ascii=False, indent=4)  
        
        userinfo_set_result = True
    else:
        print("ユーザ名・パスワードの入力が不足しています")
    
 
def account_check(mode):
    #print("ユーザ名・パスワードの設定を実施")
    global userinput_wd_exist
    global userinfo_set_result
    
    # ユーザ名・パスワードの設定処理実施済みで、再設定する時の初期化
    if mode == "reset" and userinfo_set_result == True:
        userinfo_set_result = False
        
    # -------------------------------------------------
    # ユーザ名・パスワード入力用ウィジェット
    # -------------------------------------------------
    user_info_wd = tk.Tk()
    user_info_wd.title("Jamaのユーザ情報の設定")
    user_info_wd.geometry("460x300")

    frame1 = ttk.Frame(user_info_wd, height=200, width=400, relief="ridge", borderwidth=3)
    frame2 = ttk.Frame(user_info_wd, height=200, width=400, relief="flat", borderwidth=3)

    font_tytle_set = ("Yu Gothic UI", 14, "bold")
    font_set_lb1 = ("Yu Gothic UI", 14)
    style_set_bt = ttk.Style()
    style_set_bt.configure("bt_set1.TButton", font=("Yu Gothic UI", 12))

    lb_msg1 = tk.Label(frame1, text="Jamaのユーザ名とパスワードを入力してください", font=font_tytle_set)
    lb_username1 = tk.Label(frame1, text="ユーザ名:", font=font_set_lb1)
    en_username1 = ttk.Entry(frame1, text="ユーザ名入力", font=font_set_lb1) 
    lb_password1 = tk.Label(frame1, text="パスワード:", font=font_set_lb1)
    en_password1 = ttk.Entry(frame1, text="パスワード入力", font=font_set_lb1) 
    
    button1 = ttk.Button(frame2, text="設定", style="bt_set1.TButton", command= lambda:entry_get(en_username1.get(), en_password1.get()))
    button2 = ttk.Button(frame2, text="終了", style="bt_set1.TButton", command= user_info_wd.destroy)
    text_msg_input = tk.StringVar()
    text_msg_input.set("")    
    lb_msg_input = ttk.Label(frame2, textvariable=text_msg_input, font=font_set_lb1)

    #Frame内の要素配置
    lb_msg1.grid(row=0, columnspan=2, padx=5, pady=5)
    lb_username1.grid(row=1, column=0, padx=5, pady=5)
    en_username1.grid(row=1, column=1, padx=5, pady=5)
    lb_password1.grid(row=2, column=0, padx=5, pady=5)
    en_password1.grid(row=2, column=1, padx=5, pady=5)
    
    button1.grid(row=0, column=0, padx=5, pady=5)
    button2.grid(row=0, column=1, padx=50, pady=5)
    lb_msg_input.grid(row=1, columnspan=2, padx=5, pady=5)

    frame1.pack(padx=20, pady=20)
    frame2.pack(padx=10, pady=20) 
            
    user_info_wd.mainloop()    
        
    return userinfo_set_result      #入力完了/未完了状態をリターン
    

            


 

     
