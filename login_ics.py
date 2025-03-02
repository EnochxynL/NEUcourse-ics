import os
from datetime import datetime, timedelta
from http.cookiejar import CookieJar
from supwisdom.auth import login_via_supwisdom, login_via_tpass
from supwisdom.curriculum import fetch_courses, fetch_learn_week
from supwisdom.ics import generate_ics

def main():
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


    # 获取包含课程表的html源码
    try:
        html = fetch_courses(cookie_jar)
    except Exception as e:
        print(f"获取课程表失败: {e}")
        return


    # 获取当前教学周
    try:
        learn_week = fetch_learn_week(cookie_jar)
    except Exception as e:
        print(f"获取教学周失败: {e}")
        return


    # 计算校历第一周周日
    now = datetime.now()
    day_sum = now.weekday() + learn_week * 7 - 7
    school_start_day = now - timedelta(days=day_sum)
    school_start_day = school_start_day.replace(hour=0, minute=0, second=0, microsecond=0)
    print(f"\n当前为第 {learn_week} 教学周。")
    print(f"计算得到本学期开始于 {school_start_day.strftime('%Y-%m-%d')}")
    print("官方校历 http://www.neu.edu.cn/xl/list.htm")


    # 从html源码生成ics文件内容
    try:
        ics = generate_ics(html, school_start_day)
    except Exception as e:
        print(f"生成ics文件失败: {e}")
        return

    # 保存到文件
    file_path = "myCourses.ics"
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(ics)
    except Exception as e:
        print(f"保存文件失败: {e}")
        return

    # 提示文件路径
    try:
        abs_path = os.path.abspath(file_path)
        print(f"\n已保存为：{abs_path}")
    except Exception as e:
        print(f"获取文件路径失败: {e}")

if __name__ == "__main__":
    main()