# -*- coding:utf-8 -*-
__author__ = 'Threedog'
__Date__ = '2018/6/4 11:16'

# 窗体标题  用于定位游戏窗体
WINDOW_TITLE = "QQ游戏 - 连连看角色版"
# 时间间隔  间隔多少秒连一次
TIME_INTERVAL = 0.3
HESITATE = 0.05
# 游戏区域距离顶点的长度
MARGIN_LEFT = 28
# 游戏区域距离顶点的高度
MARGIN_HEIGHT = 364
# 横向的方块数量
H_NUM = 19
# 纵向的方块数量
V_NUM = 11
# 方块宽度 (on 4K)
SQUARE_WIDTH = 62
# 方块高度 (on 4K)
SQUARE_HEIGHT = 70
# 方块宽度 (1080P)
SQUARE_WIDTH_1080P = 31
# 方块高度 (1080P)
SQUARE_HEIGHT_1080P = 35
# 切片处理时候的左上、右下坐标：
# 注意  这里要么保证是21*25，要么，如果不是（比如四个数据是10,10,50,50；也就是40*40像素），name就把empty.png图片替换成对应大小的一张图片（比如40*40），图片可以没用，但程序中不能
SUB_LT_X = 15
SUB_LT_Y = 15
SUB_RB_X = 36
SUB_RB_Y = 40
