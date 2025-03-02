曾经使用 https://github.com/whoisnian/getMyCourses 时候发现密码是明文输入的，因此分析源代码顺便使用python重写。

自动导入：运行login-ics.py
手动导入：从教务系统用浏览器F12抓取到courseTableForStd!courseTable.action后放在项目目录，运行manual-ics.py