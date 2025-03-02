import requests
import re
import time
from http.cookiejar import CookieJar

# 获取课程表所在页面源代码
def fetch_courses(cookie_jar, semester_offset=0):
    print("\n获取课表详情中。。。")

    # 创建一个会话对象，用于保持cookies
    session = requests.Session()
    session.cookies = cookie_jar

    # 第一次请求：请求ids
    time.sleep(1)
    url1 = "http://219.216.96.4/eams/courseTableForStd.action"
    response1 = session.get(url1)
    # 检查请求是否成功
    if response1.status_code != 200:
        raise Exception("请求ids失败")

    # 读取响应内容
    content = response1.text
    # 检查是否包含特定字符串
    if "bg.form.addInput(form,\"ids\",\"" not in content:
        raise Exception("获取ids失败")
    # 提取ids
    temp = content[content.index("bg.form.addInput(form,\"ids\",\"") + 29:content.index("bg.form.addInput(form,\"ids\",\"") + 50]
    ids = temp[:temp.index("\");")]
    # 获取semesterId
    semester_id = int(response1.cookies.get_dict().get("semester.id")) + semester_offset

    # 第二次请求：请求课表
    time.sleep(1)
    url2 = "http://219.216.96.4/eams/courseTableForStd!courseTable.action"
    form_data = {
        "ignoreHead": "1",
        "showPrintAndExport": "1",
        "setting.kind": "std",
        "startWeek": "",
        "semester.id": semester_id,
        "ids": ids
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0"
    }
    response2 = session.post(url2, data=form_data, headers=headers)
    # 检查请求是否成功
    if response2.status_code != 200:
        raise Exception("请求课表失败")

    # 读取响应内容
    content = response2.text
    # 检查是否包含特定字符串
    if "课表格式说明" not in content:
        raise Exception("获取课表失败")
    print("获取课表详情成功：" + content)
    return content

# 获取当前教学周
def fetch_learn_week(cookie_jar):
    print("\n获取当前教学周中。。。")

    # 创建一个会话对象，用于保持cookies
    session = requests.Session()
    session.cookies = cookie_jar

    url = "http://219.216.96.4/eams/homeExt.action"
    response = session.get(url)
    # 检查请求是否成功
    if response.status_code != 200:
        raise Exception("请求教学周失败")

    # 读取响应内容
    content = response.text
    # 检查是否包含特定字符串
    if "教学周" not in content:
        raise Exception("获取教学周失败")
    # 使用正则表达式提取教学周
    temp = content[content.index("id=\"teach-week\">"):content.index("教学周") + 10]
    reg = re.compile(r'学期\s*<font size="\d+px">(\d+)<\/font>\s*教学周')
    res = reg.findall(temp)
    if not res:
        raise Exception(temp + " 中未匹配到教学周")

    print("获取当前教学周成功：" + res[0])
    return int(res[0])

# 示例使用
if __name__ == "__main__":
    # 创建一个CookieJar对象
    cookie_jar = CookieJar()

    # 获取课程表
    try:
        courses = fetch_courses(cookie_jar)
        print(courses)
    except Exception as e:
        print(f"获取课程表失败: {e}")

    # 获取当前教学周
    try:
        week = fetch_learn_week(cookie_jar)
        print(f"当前教学周: {week}")
    except Exception as e:
        print(f"获取教学周失败: {e}")