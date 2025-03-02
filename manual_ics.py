import os
from datetime import datetime, timedelta
from supwisdom.ics import generate_ics

def main():
    # 手动从浏览器保存课程表html
    html_file = open('./courseTableForStd!courseTable.action', 'r')
    html = html_file.read()


    # 手动输入当前教学周
    learn_week = eval(input("教学周: "))


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