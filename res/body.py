import cv2
import mediapipe as mp
import time
#
# 导入姿态跟踪方法
mpPose = mp.solutions.pose  # 姿态识别方法
pose = mpPose.Pose(static_image_mode=False,  # 静态图模式，False代表置信度高时继续跟踪，True代表实时跟踪检测新的结果
                   # upper_body_only=False,  # 是否只检测上半身
                   smooth_landmarks=True,  # 平滑，一般为True
                   min_detection_confidence=0.5,  # 检测置信度
                   min_tracking_confidence=0.5)  # 跟踪置信度
# 检测置信度大于0.5代表检测到了，若此时跟踪置信度大于0.5就继续跟踪，小于就沿用上一次，避免一次又一次重复使用模型

# 导入绘图方法
mpDraw = mp.solutions.drawing_utils

# （1）导入视频
cap = cv2.VideoCapture(0)

pTime = 0  # 设置第一帧开始处理的起始时间

# （2）处理每一帧图像
while True:

    # 接收图片是否导入成功、帧图像
    success, img = cap.read()

    # 将导入的BGR格式图像转为RGB格式
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 将图像传给姿态识别模型
    results = pose.process(imgRGB)

    # 查看体态关键点坐标，返回x,y,z,visibility
    # print(results.pose_landmarks)

    # 如果检测到体态就执行下面内容，没检测到就不执行
    if results.pose_landmarks:
        # 绘制姿态坐标点，img为画板，传入姿态点坐标，坐标连线
        mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)

    # 查看FPS
    cTime = time.time()  # 处理完一帧图像的时间
    fps = 1 / (cTime - pTime)
    pTime = cTime  # 重置起始时间

    # 在视频上显示fps信息，先转换成整数再变成字符串形式，文本显示坐标，文本字体，文本大小
    cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    # 显示图像，输入窗口名及图像数据
    cv2.imshow('image', img)
    if cv2.waitKey(10) & 0xFF == 27:
        cv2.destroyAllWindows()# 每帧滞留15毫秒后消失，ESC键退出
        break

# 释放视频资源
cap.release()
# cv2.destroyAllWindows()
