'''
python 版本：3.5
opencv 下载链接： 
https://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv
选择版本：opencv_python‑3.4.1‑cp35‑cp35m‑win_amd64.whl
pywin32 下载链接：
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pywin32
选择版本：pywin32-223-cp35-cp35m-win_amd64.whl 
'''

import matching
import cv2
import numpy as np
import win32api
import win32gui
import win32con
from PIL import ImageGrab
import time
import random
from config import *


# 获取窗体坐标位置(左上)
def getGameWindowPosition():
    # FindWindow(lpClassName=None, lpWindowName=None)  窗口类名 窗口标题名
    window = win32gui.FindWindow(None,WINDOW_TITLE)
    # 没有定位到游戏窗体
    while not window:
        print('定位游戏窗体失败，5秒后重试...')
        time.sleep(5)
        window = win32gui.FindWindow(None,WINDOW_TITLE)
    # 定位到游戏窗体
    win32gui.SetForegroundWindow(window) # 将窗体顶置
    pos = win32gui.GetWindowRect(window)
    print("定位到游戏窗体：" + str(pos))
    return (pos[0], pos[1])

# 获取一张完整的屏幕截图
def getScreenImage():
    print('捕获屏幕截图...')
    scim = ImageGrab.grab()  # 屏幕截图，获取到的是Image类型对象
    scim.save('screen.png')
    return cv2.imread("screen.png") # opencv 读取，拿到的是ndarray存储的图像

# 从屏幕截图中识别
def getAllSquare(screen_image,game_pos):
    print('图像切片处理...')
    # 通过游戏窗体，找到连连看连接的区域：
    game_x = game_pos[0] + MARGIN_LEFT
    game_y = game_pos[1] + MARGIN_HEIGHT
    # 从连接区域左上开始，把图像切割成一个一个的小块，切割标准是按照小块的横纵坐标。
    all_square = []

    # DEBUG
    image_with_boxes = screen_image.copy()

    for x in range(H_NUM):
        for y in range(V_NUM):
            # 获取小块的坐标
            top_left = (game_x + x * SQUARE_WIDTH, game_y + y * SQUARE_HEIGHT)
            bottom_right = (game_x + (x+1) * SQUARE_WIDTH, game_y + (y+1) * SQUARE_HEIGHT)
            
            # 在原图副本上绘制边界
            cv2.rectangle(image_with_boxes, top_left, bottom_right, (0, 255, 0), 2)

    cv2.imwrite("screen_debug.png", image_with_boxes)

    for x in range(0,H_NUM):
        # line_square = []
        for y in range(0,V_NUM):
            # ndarray的切片方法，[纵坐标起始位置：纵坐标结束为止，横坐标起始位置：横坐标结束位置]
            square = screen_image[game_y + y * SQUARE_HEIGHT :game_y + (y+1) * SQUARE_HEIGHT,game_x + x * SQUARE_WIDTH:game_x + (x+1) * SQUARE_WIDTH]
            all_square.append(square)
    # 因为有些图片的边缘不一致造成干扰（主要是空白区域的切图），所以把每张小方块向内缩小一部分再
    # 对所有的方块进行处理屏蔽掉外边缘 然后返回
    # return list(map(lambda square : square[SUB_LT_Y:SUB_RB_Y,SUB_LT_X:SUB_RB_X],all_square))
    return [square[SUB_LT_Y:SUB_RB_Y, SUB_LT_X:SUB_RB_X] for square in all_square]
    # 上面这行相当于下面这4行
    # new_all_square = []
    # for square in all_square:
    #     s = square[SUB_LT_Y:SUB_RB_Y, SUB_LT_X:SUB_RB_X]
    #     new_all_square.append(s)
    # return new_all_square

# 判断图像是否与已经在列表中的图像相同，如果是返回True
def isImageExist(img,img_list):
    for existed_img in img_list:
        b = np.subtract(existed_img,img) # 图片数组进行比较，返回的是两个图片像素点差值的数组，
        if not np.any(b):   # 如果全部是0，说明两图片完全相同。
            return True
        else:
            continue
    return False

# 获取所有的方块类型
def getAllSquareTypes(all_square):
    print("将图像矩阵按类型归入类型列表...")
    types = []
    # 先把空白添加到数组中，作为0号
    empty_img = cv2.imread('empty.png')
    types.append(empty_img)
    for square in all_square:
        # 如果这个图像不存在的话将图像保存起来
        if not isImageExist(square,types):
            types.append(square)
    return types

def concatenate_images(types):
    # 初始化一个空图像，用于拼接
    concatenated_image = None
    
    # 按照类型数量计算需要多少行和列来拼接图像
    num_images = len(types)
    rows = num_images 
    cols = 1 
    
    # 拼接图像
    for i in range(rows):
        # 创建一个空的行图像
        row_images = []
        for j in range(cols):
            index = i * cols + j
            if index < num_images:
                # 添加图像到行
                row_images.append(types[index])
        # 水平拼接当前行的图像
        row_concatenated = cv2.hconcat(row_images)
        # 将当前行添加到最终的拼接图像
        if concatenated_image is None:
            concatenated_image = row_concatenated
        else:
            concatenated_image = cv2.vconcat([concatenated_image, row_concatenated])

    # 保存拼接后的图像
    cv2.imwrite('concatenated_types.png', concatenated_image)

# 将所有的方块与类型进行比较，转置成数字
def getAllSquareRecord(all_square_list,types):
    print("将所有的方块与类型进行比较，转置成数字矩阵...")
    record = []  # 整个记录的二维数组
    line = []   # 记录一行
    for square in all_square_list:   # 把所有的方块和保存起来的所有类型做对比
        num = 0
        for type in types:    # 所有类型
            res = cv2.subtract(square,type) # 作比较
            if not np.any(res):     # 如果两个图片一样
                line.append(num)    # 将类型的数字记录进这一行
                break               # 并且跳出循环
            num += 1                # 如果没有匹配上，则类型数加1

        if len(line) == V_NUM:         # 如果校验完这一行已经有了11个数据，则另起一行
            record.append(line)
            line = []
    print(record)
    return record

# 自动消除
def autoRelease(result,game_x,game_y):
    print("game_x: {}, game_y: {}".format(game_x, game_y))
    for i in range(0,len(result)):
        for j in range(0,len(result[0])):
            # 以上两个for循环，定位第一个选中点
            if result[i][j] != 0:
                for m in range(0,len(result)):
                    for n in range(0,len(result[0])):
                        if result[m][n] != 0:
                            # 后两个for循环定位第二个选中点
                            if matching.canConnect(i,j,m,n,result):
                            # 执行消除算法并返回
                                result[i][j] = 0
                                result[m][n] = 0
                                print('可消除点：'+ str(i+1) + ',' + str(j+1) + '和' + str(m+1) + ',' + str(n+1))
                                x1 = game_x + j*SQUARE_WIDTH_1080P + 2
                                y1 = game_y + i*SQUARE_HEIGHT_1080P + 3
                                x2 = game_x + n*SQUARE_WIDTH_1080P + 2
                                y2 = game_y + m*SQUARE_HEIGHT_1080P + 3
                                print("({}, {}), ({}, {})".format(x1, y1, x2, y2))
                                # win32api.SetCursorPos((game_x, game_y))
                                win32api.SetCursorPos((x1, y1))
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x1, y1, 0, 0)
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x1, y1, 0, 0)
                                time.sleep(TIME_INTERVAL)

                                win32api.SetCursorPos((x2, y2))
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x2, y2, 0, 0)
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x2, y2, 0, 0)
                                time.sleep(TIME_INTERVAL)
                                return True
    return False

def autoRemove(squares, game_pos):
    # 每次消除一对儿，QQ的连连看最多105对儿
    game_x = game_pos[0] + int(MARGIN_LEFT / 2)
    game_y = game_pos[1] + int(MARGIN_HEIGHT / 2)
    # 判断是否消除完了？如果没有的话，点击重列后继续消除
    # for i in range(0,1):
    for i in range(0,60):
        random_t = random.uniform(1, 15) * HESITATE
        time.sleep(random_t)
        autoRelease(squares,game_x,game_y)

def drawTypeDebugImage(record, game_pos):
    img = cv2.imread("screen_debug.png")
    game_x = game_pos[0] + MARGIN_LEFT
    game_y = game_pos[1] + MARGIN_HEIGHT

    for x in range(H_NUM):
        for y in range(V_NUM):
            # 获取小块的坐标
            top_left = (game_x + x * SQUARE_WIDTH, game_y + y * SQUARE_HEIGHT)
            bottom_right = (game_x + (x+1) * SQUARE_WIDTH, game_y + (y+1) * SQUARE_HEIGHT)

            type_num = record[y][x]
            if type_num > 0:
                cv2.putText(img, str(type_num), (top_left[0] + 5, top_left[1] + 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    cv2.imwrite("screen_type_debug.png", img)

if __name__ == '__main__':
    # 1、定位游戏窗体
    # 这里接口拿到的是假设 1080p 的坐标，但是截图是 4K 的
    game_pos = getGameWindowPosition()
    time.sleep(1)
    # 2、从屏幕截图一张，通过opencv读取
    screen_image = getScreenImage()
    # 3、图像切片，把截图中的连连看切成一个一个的小方块，保存在一个数组中
    all_square_list = getAllSquare(screen_image, (game_pos[0] * 2, game_pos[1] * 2))
    # 4、切片处理后的图片，相同的作为一种类型，放在数组中。
    types = getAllSquareTypes(all_square_list)
    print("# Types: {}".format(len(types)))
    concatenate_images(types)
    # 5、将切片处理后的图片，转换成相对应的数字矩阵。注意 拿到的数组是横纵逆向的，转置一下。
    result = np.transpose(getAllSquareRecord(all_square_list,types))
    drawTypeDebugImage(result, (game_pos[0] * 2, game_pos[1] * 2))
    # 6、执行自动消除
    autoRemove(result,game_pos)
    # 7、消除完成，释放资源。
    cv2.waitKey(0)
    cv2.destroyAllWindows()
