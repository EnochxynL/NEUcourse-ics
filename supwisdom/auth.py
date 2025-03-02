import requests
import re
import time
import hashlib
from http.cookiejar import CookieJar

# 树维教务系统登录，参考https://gist.github.com/whoisnian/32b832bd55978fefa042d7c76f9d76c3
def login_via_supwisdom(username, password):
    print("\n树维教务系统登录中。。。")

    # 创建一个会话对象，用于保持cookies
    session = requests.Session()
    session.cookies = CookieJar()

    # 第一次请求：获取登录页面
    url1 = "http://219.216.96.4/eams/loginExt.action"
    response1 = session.get(url1)
    # 检查请求是否成功
    if response1.status_code != 200:
        raise Exception("登录页面打开失败，请检查 http://219.216.96.4/eams/loginExt.action")

    # 读取响应内容
    content = response1.text
    # 检查是否包含特定字符串
    if "CryptoJS.SHA1(" not in content:
        raise Exception("登录页面打开失败，未找到CryptoJS.SHA1")

    # 提取密码哈希的前缀
    temp = content[content.index("CryptoJS.SHA1(") + 15:content.index("CryptoJS.SHA1(") + 52]
    # 对密码进行SHA1哈希
    password = temp + password
    password_hash = hashlib.sha1(password.encode()).hexdigest()

    # 第二次请求：提交登录表单
    time.sleep(1)
    url2 = "http://219.216.96.4/eams/loginExt.action"
    form_data = {
        "username": username,
        "password": password_hash,
        "session_locale": "zh_CN"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0"
    }
    response2 = session.post(url2, data=form_data, headers=headers)
    # 检查请求是否成功
    if response2.status_code != 200:
        raise Exception("登录请求失败")

    # 读取响应内容
    content = response2.text
    # 检查是否包含特定字符串
    if "personal-name" not in content:
        raise Exception("登录失败，请检查用户名和密码")
    # 提取并打印用户信息
    temp = content[content.index("class=\"personal-name\">") + 23:content.index("class=\"personal-name\">") + 60]
    print(temp[:temp.index(")") + 1])

    print("树维教务系统登录完成。")
    return session.cookies

# 统一身份认证登录
def login_via_tpass(username, password):
    print("\n统一身份认证登录中。。。")

    # 创建一个会话对象，用于保持cookies
    session = requests.Session()
    session.cookies = CookieJar()

    # 第一次请求：获取登录页面
    url1 = "http://219.216.96.4/eams/localLogin!tip.action"
    response1 = session.get(url1)
    # 检查请求是否成功
    if response1.status_code != 200:
        raise Exception("第一次请求失败")

    # 第二次请求：获取统一身份认证页面
    url2 = "https://pass.neu.edu.cn/tpass/login?service=http%3A%2F%2F219.216.96.4%2Feams%2FhomeExt.action"
    response2 = session.get(url2)
    # 检查请求是否成功
    if response2.status_code != 200:
        raise Exception("第二次请求失败")

    # 读取响应内容
    content = response2.text
    # 检查是否包含特定字符串
    if "<form id=\"loginForm\" action=\"/tpass/login" not in content:
        raise Exception("登录页面打开失败，请检查 https://pass.neu.edu.cn")

    # 提取表单信息
    reg1 = re.compile(r'id="loginForm" action="(/tpass/login[^"]*)')
    form_action = "https://pass.neu.edu.cn" + reg1.search(content).group(1)
    reg2 = re.compile(r'id="lt" name="lt" value="([^"]*)')
    form_lt = reg2.search(content).group(1)
    reg3 = re.compile(r'name="execution" value="([^"]*)')
    form_execution = reg3.search(content).group(1)
    reg4 = re.compile(r'name="_eventId" value="([^"]*)')
    form__eventId = reg4.search(content).group(1)
    # 构造rsa参数
    form_rsa = username + password + form_lt
    form_ul = len(username)
    form_pl = len(password)

    # 第三次请求：提交登录表单
    time.sleep(1)
    form_data = {
        "rsa": form_rsa,
        "ul": str(form_ul),
        "pl": str(form_pl),
        "lt": form_lt,
        "execution": form_execution,
        "_eventId": form__eventId
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0"
    }
    response3 = session.post(form_action, data=form_data, headers=headers)
    # 检查请求是否成功
    if response3.status_code != 200:
        raise Exception("登录请求失败")

    # 读取响应内容
    content = response3.text
    # 检查是否包含特定字符串
    if "personal-name" not in content:
        raise Exception("登录失败，请检查用户名和密码")
    # 提取并打印用户信息
    temp = content[content.index("class=\"personal-name\">") + 23:content.index("class=\"personal-name\">") + 60]
    print(temp[:temp.index(")") + 1])

    print("统一身份认证登录完成。")
    return session.cookies

# 示例使用
if __name__ == "__main__":
    # 树维教务系统登录
    try:
        cookies = login_via_supwisdom("your_username", "your_password")
        print("登录成功，Cookies:", cookies)
    except Exception as e:
        print(f"树维教务系统登录失败: {e}")

    # 统一身份认证登录
    try:
        cookies = login_via_tpass("your_username", "your_password")
        print("登录成功，Cookies:", cookies)
    except Exception as e:
        print(f"统一身份认证登录失败: {e}")