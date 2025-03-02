import os
from datetime import datetime, timedelta
from http.cookiejar import CookieJar
from supwisdom.auth import login_via_supwisdom, login_via_tpass

def login():
    # 选择登录方式
    print("1.树维教务系统登录: http://219.216.96.4/eams/loginExt.action")
    print("2.东大统一身份认证: https://pass.neu.edu.cn")
    choice = input("\n请选择登录方式（1 或 2）：")
    if choice not in ["1", "2"]:
        print("无效的选择")
        return

    # 获取帐号和密码
    username = input("帐号: ")
    password = input("密码: ")

    # 登录
    cookie_jar = CookieJar()
    try:
        if choice == "1":
            cookie_jar = login_via_supwisdom(username, password)
        else:
            cookie_jar = login_via_tpass(username, password)
    except Exception as e:
        print(f"登录失败: {e}")
        return
    
    return cookie_jar

import requests

if __name__ == "__main__":
    print(requests.utils.dict_from_cookiejar(login()))