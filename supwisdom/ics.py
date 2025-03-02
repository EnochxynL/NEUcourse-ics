import re
import uuid
from datetime import datetime, timedelta

# 课程具体时间，周几第几节
class CourseTime:
    def __init__(self, day_of_the_week, time_of_the_day):
        self.day_of_the_week = day_of_the_week
        self.time_of_the_day = time_of_the_day

# 课程信息
class Course:
    def __init__(self, course_id, course_name, room_id, room_name, weeks, course_times):
        self.course_id = course_id
        self.course_name = course_name
        self.room_id = room_id
        self.room_name = room_name
        self.weeks = weeks
        self.course_times = course_times

# 作息时间表，浑南上课时间
class_start_time_hunnan = [
    "083000", "093000", "104000", "114000", "140000", "150000",
    "161000", "171000", "183000", "193000", "203000", "213000"
]

# 作息时间表，浑南下课时间
class_end_time_hunnan = [
    "092000", "102000", "113000", "123000", "145000", "155000",
    "170000", "180000", "192000", "202000", "212000", "222000"
]

# 作息时间表，南湖上课时间
class_start_time_nanhu = [
    "080000", "090000", "101000", "111000", "140000", "150000",
    "161000", "171000", "183000", "193000", "203000", "213000"
]

# 作息时间表，南湖下课时间
class_end_time_nanhu = [
    "085000", "095000", "110000", "120000", "145000", "155000",
    "170000", "180000", "192000", "202000", "212000", "222000"
]

# ics文件用到的星期几简称
day_of_week = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]

# 从html源码生成ics文件内容
def generate_ics(html, school_start_day):
    print("\n生成ics文件中。。。")

    # 利用正则匹配有效信息
    my_courses = []
    reg1 = re.compile(r'TaskActivity\(actTeacherId.join\(\',\'\),actTeacherName.join\(\',\'\),"(.*)","(.*)\(.*\)","(.*)","(.*)","(.*)",null,null,assistantName,"",""\);((?:\s*index =\d+\*unitCount\+\d+;\s*.*\s)+)')
    reg2 = re.compile(r'\s*index =(\d+)\*unitCount\+(\d+);\s*')
    courses_str = reg1.findall(html)

    for course_str in courses_str:
        course_id = course_str[0]
        course_name = course_str[1]
        room_id = course_str[2]
        room_name = course_str[3]
        weeks = course_str[4]
        course_times = []

        for index_str in course_str[5].split("table0.activities[index][table0.activities[index].length]=activity;"):
            if "unitCount" not in index_str:
                continue
            match = reg2.search(index_str)
            day_of_the_week = int(match.group(1))
            time_of_the_day = int(match.group(2))
            course_times.append(CourseTime(day_of_the_week, time_of_the_day))

        my_courses.append(Course(course_id, course_name, room_id, room_name, weeks, course_times))

    # 生成ics文件头
    ics_data = """BEGIN:VCALENDAR
PRODID:-//nian//getMyCourses 20190522//EN
VERSION:2.0
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:myCourses
X-WR-TIMEZONE:Asia/Shanghai
BEGIN:VTIMEZONE
TZID:Asia/Shanghai
X-LIC-LOCATION:Asia/Shanghai
BEGIN:STANDARD
TZOFFSETFROM:+0800
TZOFFSETTO:+0800
TZNAME:CST
DTSTART:19700101T000000
END:STANDARD
END:VTIMEZONE
"""

    num = 0
    for course in my_courses:
        week_day = course.course_times[0].day_of_the_week
        st = 12
        en = -1

        # 课程上下课时间
        for course_time in course.course_times:
            if st > course_time.time_of_the_day:
                st = course_time.time_of_the_day
            if en < course_time.time_of_the_day:
                en = course_time.time_of_the_day

        # debug信息
        num += 1
        print(f"\n{num}")
        print(course.course_name)
        print(f"周{week_day + 1} 第{st + 1}-{en + 1}节")

        # 统计要上课的周
        periods = []
        start_week = []
        byday = day_of_week[week_day]

        i = 0
        while i < 53:
            if course.weeks[i] != '1':
                i += 1
                continue

            if i + 1 >= 53:
                start_week.append(i)
                periods.append(f"RRULE:FREQ=WEEKLY;WKST=SU;COUNT=1;INTERVAL=1;BYDAY={byday}")
                print(f"第{i}周")
                i += 1
                continue

            if course.weeks[i + 1] == '1':
                # 连续周合并
                j = i + 1
                while j < 53 and course.weeks[j] == '1':
                    j += 1
                start_week.append(i)
                periods.append(f"RRULE:FREQ=WEEKLY;WKST=SU;COUNT={j - i};INTERVAL=1;BYDAY={byday}")
                print(f"第{i}-{j - 1}周")
                i = j
            else:
                # 单双周合并
                j = i + 1
                while j + 1 < 53 and course.weeks[j] == '1' and course.weeks[j + 1] == '0':
                    j += 2
                start_week.append(i)
                periods.append(f"RRULE:FREQ=WEEKLY;WKST=SU;COUNT={(j + 1 - i) // 2};INTERVAL=2;BYDAY={byday}")
                if i % 2 == 0:
                    print("双", end="")
                else:
                    print("单", end="")
                print(f"{i}-{j - 1}周")
                i = j

        # 生成ics文件中的EVENT
        for i in range(len(periods)):
            event_data = "BEGIN:VEVENT\n"
            start_date = school_start_day + timedelta(days=(start_week[i] - 1) * 7 + week_day)

            if "浑南" in course.room_name:
                event_data += f"DTSTART;TZID=Asia/Shanghai:{start_date.strftime('%Y%m%dT')}{class_start_time_hunnan[st]}\n"
                event_data += f"DTEND;TZID=Asia/Shanghai:{start_date.strftime('%Y%m%dT')}{class_end_time_hunnan[en]}\n"
            else:
                event_data += f"DTSTART;TZID=Asia/Shanghai:{start_date.strftime('%Y%m%dT')}{class_start_time_nanhu[st]}\n"
                event_data += f"DTEND;TZID=Asia/Shanghai:{start_date.strftime('%Y%m%dT')}{class_end_time_nanhu[en]}\n"

            event_data += periods[i] + "\n"
            event_data += f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}\n"
            event_data += f"UID:{uuid.uuid4()}\n"
            event_data += f"CREATED:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}\n"
            event_data += "DESCRIPTION:\n"
            event_data += f"LAST-MODIFIED:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}\n"
            event_data += f"LOCATION:{course.room_name}\n"
            event_data += "SEQUENCE:0\nSTATUS:CONFIRMED\n"
            event_data += f"SUMMARY:{course.course_name}\n"
            event_data += "TRANSP:OPAQUE\nEND:VEVENT\n"

            ics_data += event_data

    ics_data += "END:VCALENDAR"
    print("\n生成ics文件完成。")
    return ics_data

# 示例使用
if __name__ == "__main__":
    # 假设的HTML内容和开学日期
    html_content = """
    TaskActivity(actTeacherId.join(','),actTeacherName.join(','),"C001","课程A(理论)","R001","教室A","11111111111111111111111111111111111111111111111111111",null,null,assistantName,"","");
    index =0*unitCount+1;
    table0.activities[index][table0.activities[index].length]=activity;
    index =1*unitCount+2;
    table0.activities[index][table0.activities[index].length]=activity;
    """
    school_start_day = datetime(2023, 9, 4)  # 假设开学日期为2023年9月4日

    try:
        ics_content = generate_ics(html_content, school_start_day)
        print(ics_content)
    except Exception as e:
        print(f"生成ics文件失败: {e}")