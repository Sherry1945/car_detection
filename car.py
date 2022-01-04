# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 20:14:02 2020

@author: sherry
"""

import cv2

import numpy as np
class Car:
    def __init__(self,c_id,c_x,c_y,derection,c_count):
        self.c_id = c_id
        self.c_x=c_x
        self.c_y=c_y
        self.c_count = c_count

def  three_frame_differencing(videopath):
    count_down=0
    cap = cv2.VideoCapture(videopath)
    width =int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height =int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    one_frame = np.zeros((height,width),dtype=np.uint8)
    two_frame = np.zeros((height,width),dtype=np.uint8)
    three_frame = np.zeros((height,width),dtype=np.uint8)
    cars=[]
    pid=0  
    maxid=-1
    while cap.isOpened():
        
        ret,frame = cap.read()
        if not ret:
            break
        frame=cv2.GaussianBlur(frame, (5,5), 0)
        frame_gray =cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)  
        one_frame,two_frame,three_frame = two_frame,three_frame,frame_gray
        
        abs1 = cv2.absdiff(one_frame,two_frame)#相减
        _,thresh1 = cv2.threshold(abs1,10,255,cv2.THRESH_BINARY)#二值，大于40的为255，小于0
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(4,4))
        erode1 = cv2.erode(thresh1,kernel)#腐蚀
        dilate1 =cv2.dilate(erode1,kernel)#膨胀
        dilate1 =cv2.dilate(dilate1,kernel)#膨胀
        
        
        
        abs2 =cv2.absdiff(two_frame,three_frame)
        _,thresh2 =cv2.threshold(abs2,10,255,cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(4,4))
        erode2 = cv2.erode(thresh2,kernel)#腐蚀
        dilate2 =cv2.dilate(erode2,kernel)#膨胀
        dilate2=cv2.dilate(dilate2,kernel)#膨胀
        
        
        binary =cv2.bitwise_and(dilate1,dilate2)#与运算
        
        
        kernel = np.ones((14,14), np.uint8)
        dilate = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
                
        dilate = cv2.morphologyEx(dilate, cv2.MORPH_CLOSE, kernel)
        #gauss_image = cv2.GaussianBlur(dilate, (3, 3), 0)
        
        #kernel = np.ones((12,12), np.uint8)
        
        #dilate = cv2.morphologyEx(gauss_image, cv2.MORPH_OPEN, kernel)

        #dilate = cv2.morphologyEx(dilate, cv2.MORPH_CLOSE, kernel)
        

        img,contours,hei = cv2.findContours(dilate.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_TC89_L1)#寻找轮廓
        cv2.line(frame, (0, 125), (1920, 125), (0, 255, 0), 2)
        cv2.line(frame, (0, 350), (1920, 350), (0, 255, 0), 2)
        cv2.putText(frame, "down:" + str(count_down),(100, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
        for contour in contours:
            x,y,w,h =cv2.boundingRect(contour)#找方框
            if cv2.contourArea(contour)<40000 and  w > 66 and h >66 and w*h>2500:
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
                cx = int(x+(w/2))
                cy = int(y+(h/2))
                new = True
                
                for i in cars:
                   
                    if abs(cx - i.c_x)<w/2 and abs(cy - i.c_y)<h/2 :#找到这辆车与上一帧中最近的车
                        new = False
                       
                       
                        i.c_x = cx
                        i.c_y = cy
                        
                        if  i.c_count ==False and maxid<i.c_id  and cy>125 and cy<350:
                            print( i.c_id,i.c_x,i.c_y) 
                            count_down=count_down+1
                            i.c_count=True
                        #if (i.c_count == False):
                         #   print(i.c_y,i.derection,i.c_count)
                          #  count_up+=1
                           # i.c_count=True
                       # if i.c_id<maxid:
                        #    cars.remove(i)
                        #if i.c_y>0.9*height:
                         #   cars.remove(i)
                for i in cars[::-1]:
                    if i.c_y>350:
                        if maxid<i.c_id :
                            maxid=i.c_id
                        cars.remove(i)
                    
                
                if new == True and cy<350:
                    p=Car(pid, cx, cy, 'unknow', False)
                    #print( p.c_id,p.c_x,p.c_y)
                    cars.append(p)
                    pid=pid+1
                    
        cv2.namedWindow("binary",cv2.WINDOW_NORMAL)
        cv2.namedWindow("dilate",cv2.WINDOW_NORMAL)
        cv2.namedWindow("frame",cv2.WINDOW_NORMAL)

        cv2.imshow("binary",binary)     
        cv2.imshow("dilate",dilate)
        cv2.imshow("frame",frame)
        if cv2.waitKey(50)&0xFF==ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()
    print(count_down)
if __name__ == '__main__':
    
    three_frame_differencing("E:/code/TESTVIDIODATA/22.avi")