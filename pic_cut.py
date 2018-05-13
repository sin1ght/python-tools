#   coding=utf-8
from PIL import Image
import os
import numpy as np
import sys
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import argparse


directs=[[-1,0],[0,-1],[1,0],[0,1]]#上左下右


class PicSlice(object):
    def __init__(self,file=None,dir_=None):
        self.file=file
        self.dir_=dir_
        self.is_single=True if self.file else False #是对单个文件分割还是对多个

        if self.is_single:
            if not os.path.isfile(file):
                print("文件:{}不存在".format(file))
                sys.exit(0)
            self.path = os.path.abspath(os.path.dirname(file))
        else:
            if not os.path.isdir(dir_):
                print("目录:{}不存在".format(file))
                sys.exit(0)
            self.path = os.path.abspath(dir_)

    @staticmethod
    def search(points,rect,point,im,px,array):
        queue=Queue()
        queue.put(point)
        array[point[0]][point[1]] = 1  # 标志访问过
        while not queue.empty():
            (i, j)=p = queue.get()
            points.append((i, j))
            if p[0] > rect[3]:
                rect[3] = p[0]
            if p[1] < rect[0]:
                rect[0] = p[1]
            if p[0] < rect[1]:
                rect[1] = p[0]
            if p[1] > rect[2]:
                rect[2] = p[1]
            for direct in directs:  # 四个方向
                m = i + direct[0]
                n = j + direct[1]
                if m < im.height and n < im.width and (not array[m][n]) \
                        and m > 0 and n > 0 and px[n, m][3] > 0:
                    queue.put((m,n))
                    array[m][n] = 1

    @staticmethod
    def search_pixel_and_rect(point,im,px,array):
        '''获取图像所有像素点 并得到最大矩形'''
        points = []
        rect=[point[1],point[0],point[1],point[0]]#top, left, bottom, right
        # self.bsf_search(points,rect, point,im,px,array)
        PicSlice.search(points,rect, point,im,px,array)
        return points,rect

    def _task(self,file_name):
        im = Image.open(os.path.join(self.path,file_name))
        if im.mode != "RGBA":
            im = im.convert('RGBA')
        px = im.load()  # 加载所有像素点
        array = np.zeros((im.height, im.width))  # 所有像素点标志位 是否访问过

        basename = os.path.basename(file_name)
        _dir = os.path.join(self.path, basename[:basename.find('.')]) #存储图片的目录
        if not os.path.exists(_dir):
            os.mkdir(_dir)

        num = 0
        for i in range(im.height):
            for j in range(im.width):
                if not array[i][j]:
                    array[i][j] = 1  # 标记已经访问
                    if px[j, i][3] > 0:
                        points, rect = PicSlice.search_pixel_and_rect((i, j),im,px,array)
                        if len(points) > 50:
                            # 排除和图像不连续的一些碎图
                            try:
                                im.crop(tuple(rect)).save(os.path.join(_dir, '{}.png'.format(num)))
                            except Exception:
                                print(rect)
                            num += 1

    def run(self):
        if self.is_single:
            self._task(os.path.basename(self.file))
        else:
            with ThreadPoolExecutor(5) as executor:
                executor.map(self._task,os.listdir(self.dir_))


if __name__=="__main__":
    usage=r'''pic_cut.py [-h] [-f FILE] [-d DIR]

Example:
    python36 pic_cut.py -f C:\Users\si\Desktop\1.png
    python36 pic_cut.py -f C:\Users\si\Desktop\1.png -f C:\Users\si\Desktop\5.png
    python36 pic_cut.py -d  C:/Users/si/Desktop/pic
'''

    parser=argparse.ArgumentParser(usage=usage)
    parser.add_argument('-f','--file',action='append',help="文件路径,可以用多个-f指定多个文件,文件太多建议用-d指定目录")
    parser.add_argument('-d','--dir',help="目录路径")
    args=parser.parse_args()

    if args.file:
        for item in args.file:
            PicSlice(file=item).run()
        print("[*]分割完成")
    elif args.dir:
        PicSlice(dir_=args.dir).run()
        print("[*]分割完成")
    else:
        print(usage)






