import sys
import time
import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox, QInputDialog, QGridLayout, QVBoxLayout, QTableView
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from pyecharts.charts import Bar, Pie
from pyecharts import options as opts
# from PyQt5.QtSql import QSqlDatabase, QSqlQueryModel, QSqlQuery
import cv2
import mediapipe as mp
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from scipy.spatial import distance as disct
import os
import face_recognition
import pymysql

from md.teacher import Ui_Form as A
from md.student import Ui_Form as B

from md.web import Ui_Form as web
from md.mainview import Ui_Form as mainv
from md.score import Ui_Form as score


# 主页
class main_Window(QWidget,mainv):
    def __init__(self):
        super(main_Window, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.atten_bt)
        self.pushButton_2.clicked.connect(self.web_bt)
        self.pushButton_3.clicked.connect(self.score_bt)
        self.pushButton_4.clicked.connect(self.sql_bt)
        self.label.setText("主页")
        self.label_2.setText("公告："
                             "数据库需要自己安装并创建名为attendance，"
                             "密码为123456的数据库")





    def atten_bt(self):
        pass
    def web_bt(self):
        pass
    def score_bt(self):
        pass
    def sql_bt(self):
        # 连接数据库
        db = pymysql.connect(host="localhost", user="root", password="123456", database="attendance")
        cursor = db.cursor()

        # 创建的表的列表
        tables = ['atten', 'class_num', 'class_sit', 'score', 'student']

        # 为每个表检查并创建
        for table in tables:
            # 检查表是否存在
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            result = cursor.fetchone()

            # 如果表不存在，创建它
            if not result:
                if table == 'atten':
                    cursor.execute("""
                       CREATE TABLE `atten`  (
                         `stu_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
                         `state` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
                         `att_pal` varchar(6) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
                         `att_date` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
                         `stu_class` int(11) NOT NULL,
                         INDEX `stu_id`(`stu_id`) USING BTREE,
                         INDEX `fk_stu_class`(`stu_class`) USING BTREE,
                         CONSTRAINT `atten_ibfk_1` FOREIGN KEY (`stu_id`) REFERENCES `student` (`stu_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
                         CONSTRAINT `fk_stu_class` FOREIGN KEY (`stu_class`) REFERENCES `class_num` (`stu_class`) ON DELETE RESTRICT ON UPDATE RESTRICT
                       ) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;
                       """)
                elif table == 'class_num':
                    cursor.execute("""
                       CREATE TABLE `class_num`  (
                         `stu_class` int(11) NOT NULL,
                         `stu_num` int(11) NULL DEFAULT NULL,
                         PRIMARY KEY (`stu_class`) USING BTREE
                       ) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;
                       """)
                elif table == 'class_sit':
                    cursor.execute("""
                       CREATE TABLE `class_sit`  (
                         `stu_class` int(11) NOT NULL,
                         `actual` int(11) NOT NULL,
                         `att_date` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
                         INDEX `stu_class`(`stu_class`) USING BTREE,
                         CONSTRAINT `class_sit_ibfk_1` FOREIGN KEY (`stu_class`) REFERENCES `class_num` (`stu_class`) ON DELETE RESTRICT ON UPDATE RESTRICT
                       ) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;
                       """)
                elif table == 'score':
                    cursor.execute("""
                       CREATE TABLE `score`  (
                         `stu_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
                         `stu_sco` int(11) NOT NULL,
                         INDEX `stu_id`(`stu_id`) USING BTREE,
                         CONSTRAINT `score_ibfk_1` FOREIGN KEY (`stu_id`) REFERENCES `student` (`stu_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
                       ) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;
                    """)
                elif table == 'student':
                    cursor.execute("""
                    CREATE TABLE `student`  (
                      `stu_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
                      `stu_name` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
                      `stu_sex` varchar(4) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT '男',
                      `stu_class` int(11) NOT NULL,
                      `stu_bir` date NULL DEFAULT NULL,
                      `stu_pic` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
                      PRIMARY KEY (`stu_id`) USING BTREE,
                      INDEX `stu_class`(`stu_class`) USING BTREE,
                      CONSTRAINT `student_ibfk_1` FOREIGN KEY (`stu_class`) REFERENCES `class_num` (`stu_class`) ON DELETE RESTRICT ON UPDATE RESTRICT
                    ) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;
                    """)

            # 如果表已经存在，输出一个消息
            else:
                print(f"The table '{table}' already exists.")

        # 关闭数据库连接
        db.close()



# 可视化主页
class webWindow(QWidget,web):
    def __init__(self):
        super(webWindow, self).__init__()
        self.setupUi(self)
        self.title.setText("课堂情况")
        self.layout = QGridLayout(self)

        self.view1 = QWebEngineView(self)
        self.view2 = QWebEngineView(self)
        self.view3 = QWebEngineView(self)

        # 设置视图位置
        self.layout.addWidget(self.view2, 0, 0, 2, 1)
        self.layout.addWidget(self.view1, 0, 1)
        self.layout.addWidget(self.view3, 1, 1)

        self.setLayout(self.layout)  # 应用图表函数

        self.update_charts()

    def update_charts(self):
        # 连接数据库
        db = pymysql.connect(host="localhost", user="root", password="123456", database="attendance")

        try:
            with db.cursor() as cursor:
                # 获取成绩数据
                cursor.execute("SELECT stu_id, stu_sco FROM score")
                data_bar = cursor.fetchall()

                # 获取考勤数据
                cursor.execute("SELECT stu_class, actual FROM class_sit")
                data_pie_solid = cursor.fetchall()

                # 获取状态数据
                cursor.execute("SELECT state, COUNT(*) FROM atten GROUP BY state")
                data_pie_hollow = cursor.fetchall()

        finally:
            db.close()

        # 创建柱状图
        bar = (
            Bar()
                .add_xaxis([item[0] for item in data_bar])
                .add_yaxis("Scores", [item[1] for item in data_bar])
                .set_global_opts(title_opts=opts.TitleOpts(title="Student Scores"))
        )

        # 创建饼图
        pie_solid = (
            Pie()
                .add("",
                     [list(z) for z in zip([item[0] for item in data_pie_solid], [item[1] for item in data_pie_solid])])
                .set_global_opts(title_opts=opts.TitleOpts(title="Class Attendance"))
                .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        )

        # 创建环形图
        pie_hollow = (
            Pie()
                .add(
                "",
                [list(z) for z in zip([item[0] for item in data_pie_hollow], [item[1] for item in data_pie_hollow])],
                radius=["40%", "75%"],
            )
                .set_global_opts(
                title_opts=opts.TitleOpts(title="Attendance State"),
                legend_opts=opts.LegendOpts(
                    orient="vertical", pos_top="15%", pos_left="2%"
                ),
            )
                .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        )

        # 蒋图表转化为html页面
        html_bar = bar.render_embed()
        html_pie_solid = pie_solid.render_embed()
        html_pie_hollow = pie_hollow.render_embed()

        # 蒋html展示在页面
        self.view1.setHtml(html_bar)
        self.view2.setHtml(html_pie_solid)
        self.view3.setHtml(html_pie_hollow)


        # 页面设为百分之80
        self.view1.setZoomFactor(0.8)
        self.view2.setZoomFactor(0.8)
        self.view3.setZoomFactor(0.8)

# 评分主页
class scoreWindow(QWidget,score):
    def __init__(self):
        super(scoreWindow, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.load_data)  # 载入数据
        self.pushButton_2.clicked.connect(self.on_pushButton_2_clicked)  # 扣分
        self.pushButton_3.clicked.connect(self.on_pushButton_upload_clicked)  # 载入数据
        # self.md = QStandardItemModel(self)
        # 初始化表格模型
        self.model = QStandardItemModel()

        # 将模型与tableview关联
        self.tableView.setModel(self.model)


    # 获取学生数据
    def get_students(self, class_num):
        db = pymysql.connect(host="localhost", user="root", password="123456", database="attendance")
        cursor = db.cursor()
        cursor.execute(f"SELECT stu_name, stu_id FROM student WHERE stu_class = {class_num}")
        students = cursor.fetchall()
        db.close()
        return students
    # 更新表格，计算分数
    def update_total(self, item):
        if item.column() in (2, 3, 4):  # 如果分数、扣除或增加被改变
            row = item.row()
            score = self.model.item(row, 2).data(Qt.DisplayRole)

            item = self.model.item(row, 3)
            if item:
                deductions = item.data(Qt.DisplayRole)
            else:
                # 处理无效的item（比如设置为0或其他默认值）
                deductions = 0

            item = self.model.item(row, 4)
            if item:
                additions = item.data(Qt.DisplayRole)
            else:
                # 处理无效的item（比如设置为0或其他默认值）
                additions = 0

            # 确保有效数据
            if not (score and deductions and additions):
                return

            try:
                total = float(score) - float(deductions) + float(additions)
            except ValueError:
                return  # 浮点数预判

            self.model.setItem(row, 5, QStandardItem(str(total)))

    def load_data(self):
        class_num = self.comboBox.currentText()  # 获取班级数据
        students = self.get_students(class_num)
        self.model = QStandardItemModel(len(students), 6)  # 6表头:"Name", "ID", "Score", "Deductions", "Additions", "Total"
        self.model.setHorizontalHeaderLabels(["Name", "ID", "Score", "Deductions", "Additions", "Total"])
        self.model.itemChanged.connect(self.update_total)

        for row, (name, id_) in enumerate(students):
            self.model.setItem(row, 0, QStandardItem(name))
            self.model.setItem(row, 1, QStandardItem(id_))
            self.model.setItem(row, 2, QStandardItem(""))  # 平时分
            self.model.setItem(row, 3, QStandardItem(""))  # 扣分
            self.model.setItem(row, 4, QStandardItem(""))  # 加分
            self.model.setItem(row, 5, QStandardItem(""))  # 总计

        self.tableView.setModel(self.model)

    def on_pushButton_2_clicked(self):
        class_num = self.comboBox.currentText()  # 获取班级数据

        students_deduction_data = self.get_students_deduction_data(class_num)

        for row in range(self.model.rowCount()):
            student_id = self.model.item(row, 1).text()

            if student_id in students_deduction_data:
                deductions = students_deduction_data[student_id]
                self.model.setItem(row, 3, QStandardItem(str(deductions)))

    def get_students_deduction_data(self, class_num):
        # 查询数据库
        db = pymysql.connect(host="localhost", user="root", password="123456", database="attendance")
        cursor = db.cursor()

        state_2_query = "SELECT stu_id, COUNT(*) as count FROM atten WHERE stu_class = %s AND state = 2 GROUP BY stu_id"
        state_3_query = "SELECT stu_id, COUNT(*) as count FROM atten WHERE stu_class = %s AND state = 3 GROUP BY stu_id"

        # State为2的数据
        cursor.execute(state_2_query, (class_num,))
        results_state_2 = cursor.fetchall()

        # State为3的数据
        cursor.execute(state_3_query, (class_num,))
        results_state_3 = cursor.fetchall()

        # 记得关闭游标
        cursor.close()

        # Student deduction data dictionary
        students_deduction_data = {}

        # 处理state为2的数据
        for result in results_state_2:
            student_id, count = result
            students_deduction_data[student_id] = count // 3

        # 处理state为3的数据并更新学生扣分信息
        for result in results_state_3:
            student_id, count = result
            if student_id in students_deduction_data:
                students_deduction_data[student_id] += count
            else:
                students_deduction_data[student_id] = count

        return students_deduction_data

    def on_pushButton_upload_clicked(self):
        db = pymysql.connect(host="localhost", user="root", password="123456", database="attendance")
        cursor = db.cursor()

        # 遍历tableview的模型数据并提取学号和总分
        for row in range(self.model.rowCount()):
            student_id = self.model.item(row, 1).text()
            total_score = self.model.item(row, 5).text()

            # 将提取到的学号和总分插入到数据库的分数表（score）中
            sql_query = "INSERT INTO score (stu_id, stu_sco) VALUES (%s, %s) ON DUPLICATE KEY UPDATE stu_sco = %s;"
            cursor.execute(sql_query, (student_id, total_score, total_score))

        # 提交更改到数据库并关闭游标
        db.commit()
        cursor.close()
        QMessageBox.information(self, "提示", "上传成功！")



# 考勤主页
class mainWindow(QWidget, A):
    def __init__(self):

        super(mainWindow, self).__init__()
        self.setupUi(self)
        self.title.setText('人脸考勤系统')
        # 相机
        self.cap_url = 0
        # 初始化相机
        self.cap = cv2.VideoCapture()
        # 考勤
        self.switch_bt = True

        self.img_name = []
        self.face_encoding = []
        self.count_eye = {}

        # self.messag_text.append(self.class_box.currentText())
        # 太早了
        # self.read_img(self.class_box.currentText())

        dataTime = QDateTime.currentDateTime().toString()
        self.newtime.setText(dataTime)
        # 查询情况
        self.inquire_box.clicked.connect(self.inquire_bt)
        # 请假登记
        self.ask_off_bot.clicked.connect(self.ask_off_bt)
        # 漏签补签
        self.Retroactive_bot.clicked.connect(self.retroactive_bt)
        # 查看结果
        self.result_bot.clicked.connect(self.result_bt)
        # 退出页面
        self.exit_box.clicked.connect(self.exit_bt)
        # 打开相机
        self.open_camre.clicked.connect(self.showCarme)
        # 考勤
        self.check_bot.clicked.connect(self.check_bt)
        # 随机点名
        self.red_name_bot.clicked.connect(self.redam_name)
        # 提示删除内容
        self.ask_off_Edit.setClearButtonEnabled(True)
        self.Retroactive.setClearButtonEnabled(True)

        self.class_box.activated.connect(self.abc)

        self.infor_bot.clicked.connect(self.close_croma)

        now = datetime.datetime.now().time()
        self.start_time.setTime(now)
        self.end_time.setTime(now)

        self.mp_face_dect = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_dete = self.mp_face_dect.FaceDetection(min_detection_confidence=0.5)

        self.video_label = QtWidgets.QLabel(self)
        self.video_label.setGeometry(QtCore.QRect(20, 20, 640, 480))
        # self.setCentralWidget(self.video_label)

    def redam_name(self):
        self.messag_text.append("随机点名")
        directory = os.path.join(os.getcwd(), 'face_dataset', self.class_box.currentText())
        file_list = os.listdir(directory)
        image_list = [file for file in file_list if file.endswith('.png')]
        if len(image_list) > 0:
            # 随机选择一张图片
            image_file = np.random.choice(image_list)
            image_path = os.path.join(directory, image_file)
            pixmap = QtGui.QPixmap(image_path)
            self.video_label.setPixmap(
                pixmap.scaled(self.video_label.size(), aspectRatioMode=QtCore.Qt.KeepAspectRatio))

            print(image_file)
        else:
            print('No images found in directory: ', directory)



    def abc(self):
        self.messag_text.append(self.class_box.currentText())
        print(self.class_box.currentText())
        self.read_img(self.class_box.currentText())


    def close_croma(self):
        self.close()
        if self.cap.isOpened() == True:
            self.cap.release()



    # 补签漏签功能模块
    def retroactive_bt(self):
        self.messag_text.append('补签漏签')
        self.ask_text.append(self.Retroactive.text())
        db = pymysql.connect(host="localhost", user="root", password="123456", database="attendance")
        cursor = db.cursor()

        # 查询学生信息
        retroactive_id = self.Retroactive.text()
        query = "SELECT stu_name, stu_class FROM student WHERE stu_id = %s"
        cursor.execute(query, (retroactive_id,))
        result = cursor.fetchone()
        if result:
            stu_name = result[0]
            stu_class = result[1]

            # 将补签信息写入考勤表
            # 获取当前年月日
            current_date = datetime.date.today()
            current_date_str = current_date.strftime("%Y-%m-%d")
            att_date = current_date_str + ' ' + self.start_time.time().toString("HH:mm:ss")
            att_pal = self.add_box.currentText()
            insert_query = "INSERT INTO atten (stu_id, state, att_pal, att_date, stu_class) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (retroactive_id, 1, att_pal, att_date, stu_class))
            db.commit()

            self.messag_text.append(f'{stu_name}({retroactive_id})已成功补签')
        else:
            self.messag_text.append('该学号不存在')

        # 关闭数据库连接
        db.close()


    # 请假登记模块
    def ask_off_bt(self):
        self.messag_text.append("请假登记")
        # 获取学生学号
        student_id = self.ask_off_Edit.text()

        # 获取打卡状态，考勤地，考勤时间，班级
        state = 2
        att_pal = self.add_box.currentText()
        # 获取当前年月日
        current_date = datetime.date.today()

        # 将日期转换为字符串并以"yyyy-MM-dd"格式表示
        current_date_str = current_date.strftime("%Y-%m-%d")
        att_date = current_date_str + ' ' + self.start_time.time().toString("HH:mm:ss")
        stu_class = self.class_box.currentText()

        # 连接数据库
        db = pymysql.connect(host="localhost", user="root", password="123456", database="attendance")
        cursor = db.cursor()

        # 插入请假考勤数据的SQL语句
        sql = f"""
        INSERT INTO atten (stu_id, state, att_pal, att_date, stu_class)
        VALUES (%s, %s, %s, %s, %s)
        """

        # 执行SQL语句并提交
        try:
            cursor.execute(sql, (student_id, state, att_pal, att_date, stu_class))
            db.commit()
            print("请假考勤数据插入成功")
        except Exception as e:
            print(f"插入请假考勤数据出错: {e}")
            db.rollback()

        # 关闭数据库连接
        cursor.close()
        db.close()
        self.ask_text.append(self.ask_off_Edit.text())

    # 查看结果模块
    def result_bt(self):

        self.messag_text.append("查看结果")
        # 获取你的变量
        stu_class = self.class_box.currentText()
        stu_add = self.add_box.currentText()

        # 获取当前日期并设置开始和结束时间
        current_date = datetime.date.today()
        current_date_str = current_date.strftime("%Y-%m-%d")
        start_date = current_date_str + ' ' + self.start_time.time().toString("HH:mm:ss")
        end_date = current_date_str + ' ' + self.end_time.time().toString("HH:mm:ss")

        # 连接到数据库
        db = pymysql.connect(host="localhost", user="root", password="123456", database="attendance")

        try:
            with db.cursor() as cursor:
                # 查询在考勤时间段内考勤状态为2的学生名字
                sql = f"""
                   SELECT stu_name FROM student
                   WHERE stu_id IN (
                       SELECT stu_id FROM atten
                       WHERE att_date >= %s AND att_date <= %s AND state = 2
                   ) AND stu_class = %s
                   """
                cursor.execute(sql, (start_date, end_date, stu_class))
                students_attended = cursor.fetchall()
                for student in students_attended:
                    self.ask_text.append(student[0])

                sql_count = f"""
                               SELECT COUNT(*) FROM student
                               WHERE stu_id IN (
                                   SELECT stu_id FROM atten
                                   WHERE att_date >= %s AND att_date <= %s  AND state = 2  AND state = 1
                               ) AND stu_class = %s
                               """
                cursor.execute(sql_count, (start_date, end_date, stu_class))
                count = cursor.fetchone()[0]

                sql_insert = f"""
                               INSERT INTO class_sit (stu_class, actual)
                               VALUES (%s, %s)
                               """
                cursor.execute(sql_insert, (stu_class, count))

                # 判断当前时间是否超过了结束时间，如果是，将未打卡学生的状态设置为3
                now = datetime.datetime.now()
                if now > datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S'):
                    # 查询未打卡的学生并插入考勤表
                    sql = f"""
                                   SELECT stu_id, stu_class, stu_name FROM student
                                   WHERE stu_id NOT IN (
                                       SELECT stu_id FROM atten
                                       WHERE att_date >= %s AND att_date <= %s
                                   ) AND stu_class = %s
                                   """
                    cursor.execute(sql, (start_date, end_date, stu_class))
                    students_not_attended = cursor.fetchall()

                    for student_id, student_class, student_name in students_not_attended:
                        # 插入未打卡学生的考勤数据
                        sql = f"""
                                       INSERT INTO atten (stu_id, state, att_pal, att_date, stu_class)
                                       VALUES (%s, 3, %s, NOW(), %s)
                                       """
                        try:
                            cursor.execute(sql, (student_id, stu_add, student_class))
                            db.commit()
                            print(f"{student_id}未打卡，考勤数据插入成功")
                            self.wei_text.append(student_name)
                        except Exception as e:
                            print(f"插入未打卡考勤数据出错: {e}")
                            db.rollback()
        finally:
            db.close()

    # 查询班级情况模块
    def inquire_bt(self):
        self.messag_text.append("查询情况")
        db = pymysql.connect(host="localhost", user="root", password="123456", database="attendance")

        # 获取班级人数
        class_name = self.class_box.currentText()  # 获取选中的班级
        cursor = db.cursor()
        query = "SELECT COUNT(*) FROM class_num WHERE stu_num=%s"
        cursor.execute(query, (class_name,))
        result = cursor.fetchone()
        num_students = result[0] if result is not None else 0
        # 获取考勤人数
        # 获取当前年月日
        current_date = datetime.date.today()

        # 将日期转换为字符串并以"yyyy-MM-dd"格式表示
        current_date_str = current_date.strftime("%Y-%m-%d")
        start_time =current_date_str+ '' + self.start_time.time().toString("HH:mm:ss")
        end_time =current_date_str+ " " + self.end_time.time().toString("HH:mm:ss")
        query = "SELECT COUNT(*) FROM atten WHERE state=1 AND att_date BETWEEN %s AND %s AND stu_class=%s"
        cursor.execute(query, (start_time, end_time, class_name))
        result = cursor.fetchone()
        num_atten = result[0] if result is not None else 0

        self.shi_num.display(num_students)
        self.wei_num.display(num_atten)

        # 关闭数据库连接
        db.close()

    # 打开相机模块
    def showCarme(self):
        if self.cap.isOpened() == False:
            self.cap.open(self.cap_url)
            self.opCarme()
        elif self.cap.isOpened() == True:
            self.cap.release()
            self.voide.clear()
            self.open_camre.setText("打开相机")


    def opCarme(self):
        self.messag_text.append("已打开相机")
        start_time = self.start_time.time().toString()
        end_time = self.end_time.time().toString()
        message = f"{start_time}-{end_time}"
        self.messag_text.append(message)
        self.open_camre.setText("关闭相机")
        if self.switch_bt == True:
            pTime = time.time()
            while self.cap.isOpened():
                success, frame = self.cap.read()
                QApplication.processEvents()

                self.img = QImage(frame.data,frame.shape[1], frame.shape[0], QImage.Format_BGR888)
                self.voide.setPixmap(QPixmap.fromImage(self.img))
            self.voide.clear()
            self.messag_text.append("已关闭相机")
        elif self.switch_bt == False:
            self.messag_text.append("考勤还没写")
            while self.cap.isOpened():
                success, frame = self.cap.read()
                farme_bgr = frame[:, :, ::-1]

                QApplication.processEvents()
                # print('sdhdifhdif')
                face_locat = face_recognition.face_locations(farme_bgr)
                face_encod1 = face_recognition.face_encodings(farme_bgr, face_locat)
                face_lemk = face_recognition.face_landmarks(frame)
                # for (top, right, bottom, left), face_en, j in zip(face_locat, face_encod1, range(len(face_lemk))):
                # 获取当前年月日
                current_date = datetime.date.today()

                # 将日期转换为字符串并以"yyyy-MM-dd"格式表示
                current_date_str = current_date.strftime("%Y-%m-%d")
                start_date = current_date_str + ' ' + self.start_time.time().toString("HH:mm:ss")
                end_date = current_date_str + ' ' + self.end_time.time().toString("HH:mm:ss")


                for face_en, j in zip(face_encod1, range(len(face_lemk))):
                    for i, v in enumerate(self.face_encoding):
                        mout = face_recognition.compare_faces(v, face_en, tolerance=0.4)
                        self.name = "未知"
                        print(mout)
                        if mout[0]:
                            left_eye = face_lemk[j]['left_eye']
                            right_eye = face_lemk[j]['right_eye']
                            ear_left = self.get_ear(left_eye)
                            ear_right = self.get_ear(right_eye)
                            try:
                                if self.count_eye[self.img_name[i]] >= 2:
                                    self.count_eye[self.img_name[i]] = 0

                                    # 获取学生学号
                                    student_id = self.img_name[i]

                                    # 获取打卡状态，考勤地，班级
                                    state = 1
                                    att_pal = self.add_box.currentText()
                                    stu_class = self.class_box.currentText()

                                    # 连接数据库
                                    db = pymysql.connect(host="localhost", user="root", password="123456",
                                                         database="attendance")
                                    cursor = db.cursor()

                                    # 插入考勤数据的SQL语句
                                    sql = f"""
                                    INSERT INTO atten (stu_id, state, att_pal, att_date, stu_class)
                                    VALUES (%s, %s, %s, NOW(), %s)
                                    """

                                    # 执行SQL语句并提交
                                    try:
                                        cursor.execute(sql, (student_id, state, att_pal, stu_class))
                                        db.commit()
                                        print("考勤数据插入成功")
                                    except Exception as e:
                                        print(f"插入考勤数据出错: {e}")
                                        db.rollback()

                                    # 关闭数据库连接
                                    cursor.close()
                                    db.close()
                                    msg_box = QMessageBox(QMessageBox.Information, '标题', self.img_name[i] + '打卡成功', QMessageBox.Ok)
                                    msg_box.button(QMessageBox.Ok).animateClick(1000)
                                    msg_box.exec_()
                                    self.messag_text.append(self.img_name[i])
                                    self.check_bt()

                                    break
                            except:
                                    self.count_eye[self.img_name[i]] = 0
                            if ear_right < 0.25 and ear_left < 0.25:
                                self.name = self.img_name[i]
                                self.count_eye[self.name] += 1
                            # print(self.count_eye)
                            # print(name)
                            break

                stu_class = self.class_box.currentText()
                stu_add = self.add_box.currentText()

                self.img = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
                self.voide.setPixmap(QPixmap.fromImage(self.img))
            self.voide.clear()



    def check_bt(self):
        if self.switch_bt == True:
            self.messag_text.append("开始考勤")
            self.switch_bt = False
            self.check_bot.setText('关闭考勤')
            self.opCarme()
        elif self.switch_bt == False:
            self.messag_text.append("关闭考勤")
            self.switch_bt = True
            self.check_bot.setText('开启考勤')
            self.opCarme()

    # def redam_name(self):
    #     self.messag_text.append("随机点名")
    #     print(self.class_box.currentText())

    def exit_bt(self):
        # 退出整个程序
        # QApplication.instance().quit()
        self.close()
        self.cap.release()

    def cv2AddChineseText(self,img, text, position, textColor=(0, 255, 0), textSize=30):
        if (isinstance(img, np.ndarray)):  # 判断是否OpenCV图片类型
            img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        # 创建一个可以在给定图像上绘图的对象
        draw = ImageDraw.Draw(img)
        # 字体的格式
        fontStyle = ImageFont.truetype(
            "simsun.ttc", textSize, encoding="utf-8")
        # 绘制文本
        draw.text(position, text, textColor, font=fontStyle)
        # 转换回OpenCV格式
        return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

    def get_ear(self,eye):
        A = disct.euclidean(eye[1], eye[5])
        B = disct.euclidean(eye[2], eye[4])
        C = disct.euclidean(eye[0], eye[3])
        ear = (A + B) / (2.0 * C)
        return ear

    def read_img(self,text):

        path = './face_dataset/'+ text+'/'


        for fn in os.listdir(path):
            print(fn)
            face_loc = face_recognition.load_image_file(path + fn)
            face_encod = face_recognition.face_encodings(face_loc)
            self.face_encoding.append(face_encod)
            # print(face_encoding)
            name = fn.split(".")[0]
            self.img_name.append(name)

        self.messag_text.append("Success!")


class studentWindow(QWidget,B):
    def __init__(self):
        super(studentWindow, self).__init__()
        self.setupUi(self)
        global frame,bboxC
        self.cap_url = 0
        # 初始化相机
        self.cap = cv2.VideoCapture()
        self.previou_bot.clicked.connect(self.close_camare)


        # 开始采集信息
        self.gather_bot.clicked.connect(self.open_carme)
        self.zhuangtai = False
        # 拍照
        self.camare_bot.clicked.connect(self.carme_state)
        #录入信息
        self.amend_bot.clicked.connect(self.amend_bt)
        #查询信息
        self.quer_bot.clicked.connect(self.quer_bt)

        self.mp_face_dect = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_dete = self.mp_face_dect.FaceDetection(min_detection_confidence=0.5)


        self.swith_state = True


    def open_carme(self):
        if self.cap.isOpened() == True:
            self.cap.release()

            self.gather_bot.setText('打开相机')
        elif self.cap.isOpened() == False:
            self.text, self.ok = QInputDialog.getText(self, '创建个人图像数据库', '请输入学号:')
            if self.ok and self.text != '':
                self.gather_bot.setText('关闭相机')
                self.gather_bt()

    def gather_bt(self):
        self.infor_text.append('采集信息')
        # self.zhuangtai = True
        if self.cap.isOpened() == False:
            self.cap.open(self.cap_url)
            while self.cap.isOpened():
                img, frame = self.cap.read()
                QApplication.processEvents()
                results = self.face_dete.process(frame)
                if results.detections:
                    for index, detection in enumerate(results.detections):
                        bboxC = detection.location_data.relative_bounding_box
                        ih, iw, ic = frame.shape
                        self.bbox = (int(bboxC.xmin * iw) - 50, int(bboxC.ymin * ih) - 100, int(bboxC.width * iw) + 100,
                                     int(bboxC.height * ih) + 200)

                        cv2.rectangle(frame, self.bbox, (225, 225, 0), 2)
                self.img = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
                self.voide_pr.setPixmap(QPixmap.fromImage(self.img))
            self.voide_pr.clear()


    def camare_bt(self):
        # self.cap.release()
        self.infor_text.append('拍照')
        if not os.path.exists("./face_dataset/"):
            os.mkdir("./face_dataset/")
        self.filename = "./face_dataset/{}/".format(self.text[6:8])
        self.mkdir(self.filename)
        photo_save_path = os.path.join(os.path.dirname(os.path.abspath('__file__')), '{}'.format(self.filename))
        self.img.save(photo_save_path + self.text + ".png")
        # self.cap.release()

        print(photo_save_path + self.text + ".png")
        self.voide_pr.setPixmap(QPixmap(self.text + ".png"))



    def carme_state(self):
        if self.swith_state == True:
            self.swith_state = False
            self.camare_bot.setText('关闭采集')
            self.infor_text.append(self.text + "采集成功！")
            self.camare_bt()
        elif self.swith_state == False:
            self.swith_state = True
            self.camare_bot.setText('开始采集')
            self.gather_bot.setText("打开相机")
            self.cap.release()

    def amend_bt(self):
        self.infor_text.append('录入信息')

        # 获取学生信息
        stu_id = self.id_inpot.text()
        stu_name = self.name_inpot.text()
        stu_sex = self.sex_inpot.text()
        stu_class = self.class_input.text()
        stu_bir = self.birth_inpot.text()

        # 构建学生图片路径
        path = str(os.path.join(os.getcwd(),'face_dataset', stu_id[6:8], f"{stu_id}.jpg"))
        print(str(path))

        # 连接数据库并执行插入语句
        db = pymysql.connect(host="localhost", user="root", password="123456", database="attendance")
        cursor = db.cursor()
        sql = f"INSERT INTO student (stu_id, stu_name, stu_sex, stu_class, stu_bir, stu_pic) VALUES ('{stu_id}', '{stu_name}', '{stu_sex}', '{stu_class}', '{stu_bir}', '{path}')"
        cursor.execute(sql)
        db.commit()

        # 关闭游标和数据库连接
        cursor.close()
        db.close()

        # 输出提示信息
        print("学生信息已添加到数据库")
        print(f"学生图片路径已更新为 {path}")
#

    def quer_bt(self):
        self.infor_text.append('查询信息')

        # 弹出输入对话框获取学号
        text, ok = QInputDialog.getText(self, '查询个人信息', '请输入学号:')
        if ok and text != '':
            # 连接数据库并查询指定学号的学生信息
            db = pymysql.connect(host="localhost", user="root", password="123456", database="attendance")
            cursor = db.cursor()
            sql = f"SELECT * FROM student WHERE stu_id = '{text}'"
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            db.close()

            # 判断是否查询到学生信息，并将信息格式化输出到self.infor_text中
            if results:
                info = f"学号：{results[0][0]}\n姓名：{results[0][1]}\n性别：{results[0][2]}\n班级：{results[0][3]}\n生日：{results[0][4]}\n图片地址：{results[0][5]}"
                print(info)
                self.infor_text.append(info)
            else:
                QMessageBox.warning(self, "查询结果", f"未找到学号为 {text} 的学生信息！", QMessageBox.Ok)


    def close_camare(self):
        if self.cap.isOpened() == True:
            self.cap.release()
            self.gather_bot.setText('打开相机')
        self.close()




    def closeEvent(self, event):  # 函数名固定不可变
        # reply = QtWidgets.QMessageBox.question(self, u'警告', u'确认退出?', QtWidgets.QMessageBox.Yes,
        #                                        QtWidgets.QMessageBox.No)
        # QtWidgets.QMessageBox.question(self,u'弹窗名',u'弹窗内容',选项1,选项2)
        if QtWidgets.QMessageBox.Yes:
            event.accept()  # 关闭窗口
            if self.cap.isOpened() == True:
                self.cap.release()
        else:
            event.ignore()  # 忽视点击X事件


#
    # 创建文件夹
    def mkdir(self, path):
        # 去除首位空格
        path = path.strip()
        # 去除尾部 \ 符号
        path = path.rstrip("\\")
        # 判断路径是否存在, 存在=True; 不存在=False
        isExists = os.path.exists(path)
        # 判断结果
        if not isExists:
            # 如果不存在则创建目录
            os.makedirs(path)
            return True

if __name__ == '__main__':
    app = QApplication(sys.argv)
    from_test = mainWindow()

    student_test = studentWindow()
    # from_test.infor_bot.clicked.connect(from_test.close)
    from_test.infor_bot.clicked.connect(student_test.show)
    # student_test.previou_bot.clicked.connect(student_test.close)
    student_test.previou_bot.clicked.connect(from_test.show)

    main_win = main_Window()
    web_win = webWindow()
    score_win = scoreWindow()
    main_win.pushButton.clicked.connect(from_test.show)

    main_win.pushButton_2.clicked.connect(web_win.show)
    main_win.pushButton_3.clicked.connect(score_win.show)
    main_win.show()
    # from_test.show()
    sys.exit(app.exec_())

