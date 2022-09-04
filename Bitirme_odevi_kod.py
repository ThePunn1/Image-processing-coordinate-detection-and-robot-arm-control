from pyfirmata import Arduino, SERVO
from time import sleep
from win32api import GetKeyState, Sleep  #tus kutuphnesi
import cv2
import numpy as np

port='COM3' #Arduino Com belirleme
pin = 8 #ileri geri (0-140) en uzak 140 y
pin_2=9 # yukarı aşşagı servo (80-180) arası  180 yukarıda z
pin_3=7 #sağ sola dönme (0-180) 0 sol 180 sağ x
pin_4=10 #gripper (120-180) kapalı 120 açık 180 
board = Arduino(port)
 
board.digital[pin].mode = SERVO      #Pinleri servolara atama
board.digital[pin_2].mode = SERVO
board.digital[pin_3].mode = SERVO
board.digital[pin_4].mode = SERVO

def rotateServo(pin, angle):            #Servonun 1 derece oluşturacagı gecikme ayarlama
        board.digital[pin].write(angle)
        sleep(0.025)
def rotateServo_2(pin, angle):
        board.digital[pin_2].write(angle)
        sleep(0.025)
def rotateServo_3(pin, angle):
        board.digital[pin_3].write(angle)
        sleep(0.025)
def rotateServo_4(pin, angle):
        board.digital[pin_4].write(angle)
        sleep(0.025) 

def Tiklama(tus):                       #Bu kod blogu genel olarak gecikmeyi beklememek için eklenmiştir.
    state=GetKeyState(tus)
    if (state!=0) and (state !=1):
        return print("Fotograf Alınıyor")    

kamera=cv2.VideoCapture(0)

while True:
    try:
        renk_tespit=0
        while True:
                rotateServo(pin, 30)       #board.digital[pin].write(0)
                rotateServo_2(pin_2, 170) #board.digital[pin_2].write(170)
                rotateServo_3(pin_3, 0)   #board.digital[pin_3].write(0)
                rotateServo_4(pin_4, 130) #board.digital[pin_4].write(120)
                sleep(1)
                break
        kontrol,frame=kamera.read()
        cut_kamera=frame[100:550,100:550] #kamera goruntu kırpma  
        ters_gor = cv2.rotate(cut_kamera, cv2.cv2.ROTATE_180)# goruntu ters cevirme
        cv2.imshow("Orjinal",ters_gor)
        hsv_frame=cv2.cvtColor(ters_gor,cv2.COLOR_BGR2HSV)
        
        Lower_red=np.array([1, 30, 20])#1 30 20/0 100 20
        Upper_red=np.array([10, 255, 255])#10 255 255 /40 255 255
        red_mask=cv2.inRange(hsv_frame,Lower_red,Upper_red)
        red=cv2.bitwise_and(ters_gor , ters_gor , mask = red_mask)
        
        Lower_green=np.array([50, 70, 100])#38 100 100
        Upper_green=np.array([75, 255, 255])#75 255 255
        green_mask=cv2.inRange(hsv_frame,Lower_green,Upper_green)

        #cv2.imshow("Siyah-Beyaz",red_mask)
        #cv2.imshow("Kirmizi",red)
         #------------------renk tespit-------------------------
        kernal = np.ones((5, 5), "uint8")
        red_mask = cv2.dilate(red_mask, kernal) 
        res_red=cv2.bitwise_and(ters_gor,ters_gor,mask=red_mask)
        contours, hierarchy = cv2.findContours(red_mask,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for pic, contour in enumerate(contours):
            area = cv2.contourArea(contour) 
            if (area>300):
                x,y,w,h=cv2.boundingRect(contour)
                ters_gor=cv2.rectangle(ters_gor,(x,y),(x+w,y+h),(0,0,255),2)
                renk_tespit=1
                cv2.putText(ters_gor,"Kirmizi Renk",(x,y),cv2.FONT_HERSHEY_SIMPLEX,1.0,(0,0,255))
        cv2.imshow("Renk_tespit", ters_gor)

        green_mask = cv2.dilate(green_mask, kernal) 
        res_green=cv2.bitwise_and(ters_gor,ters_gor,mask=green_mask)
        contours, hierarchy = cv2.findContours(green_mask,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for pic, contour in enumerate(contours):
            area = cv2.contourArea(contour) 
            if (area>300):
                x,y,w,h=cv2.boundingRect(contour)
                frame=cv2.rectangle(ters_gor,(x,y),(x+w,y+h),(0,255,0),2)
                renk_tespit=2
                cv2.putText(ters_gor,"Yesil Renk",(x,y),cv2.FONT_HERSHEY_SIMPLEX,1.0,(0,255,0))
        cv2.imshow("Renk_tespit", ters_gor)

        #------------------kordinat--------------------
        if renk_tespit==1:
            ret,thresh = cv2.threshold(red_mask,127,255,0)
            cv2.imshow("Siyah-Beyaz",red_mask)
            cv2.imshow("Kirmizi",red)
        elif renk_tespit==2:
            ret,thresh = cv2.threshold(green_mask,127,255,0)
            cv2.imshow("Siyah-Beyaz",green_mask)
            cv2.imshow("Yesil",res_green)
        contours,hierarchy = cv2.findContours(thresh, 1, 2)
        cnt = contours[0]
        M = cv2.moments(cnt)
        print( M )

        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        area = cv2.contourArea(cnt)
        print("Kamera Kordinat:"+str(cx))
        print("Kamera Kordinat:"+str(cy))

        #-----------------robot_kol_dereceleri--------------------
        robot_x = 0
        robot_y = 0

        kor_x = cx
        kor_y = cy

        y_katsayi=5.5#5,65
        x_katsayi = (kor_x*0.2) #500 değişken

        if kor_x<250:
            robot_x = x_katsayi + 48#50
        else:
            robot_x = x_katsayi + 40

        robot_y=int((kor_y/y_katsayi)+20)
        robot_x=int(robot_x)
        print("Robot Kol X Deger:"+str(robot_x))
        print("Robot Kol Y Deger:"+str(robot_y))
        #-------------------Robot_kol_kodları-------------------------
        while True:
               for i in range(0,180):     
                   if i<robot_x:
                           rotateServo_3(pin_3,i)
               sleep(1)
               board.digital[pin_4].write(180)    
               sleep(1)
               for i in range(0,140):
                       if i<robot_y:
                               rotateServo(pin,i)
               sleep(1)
               for i in range(170,85,-1):
                       rotateServo_2(pin_2,i)
               sleep(2)
               board.digital[pin_4].write(130)
               sleep(1)   
               for i in range(85,170):
                        rotateServo_2(pin_2,i) 
               sleep(1)          
               for i in range(0,140):                       
                       if i==robot_y-1:
                               for j in range(robot_y,30,-1):
                                       if j<robot_y:
                                               rotateServo(pin,j)
               sleep(1)
               rotateServo_2(pin_2,180)
               rotateServo(pin,20)
               sleep(1)
               #Ayirma islemi
               if renk_tespit==1:
                        for i in range(robot_x,0,-1):
                                rotateServo_3(pin_3,i)
                        sleep(1)        
                        for i in range(180,100,-1):
                                rotateServo_2(pin_2,i)
                        sleep(1)
                        for i in range(20,70):
                                rotateServo(pin,i) 
                        sleep(1)                                  
                        board.digital[pin_4].write(180) 
                        sleep(1)
                        for i in range(100,180):
                                rotateServo_2(pin_2,i)
                        for i in range(70,20,-1):
                                rotateServo(pin,i)
                        #Hom Pos
                        sleep(1)
                        board.digital[pin_4].write(130)
                        sleep(1)
                        rotateServo_3(pin_3,0)
                        sleep(1)
                        rotateServo(pin,30)

               elif renk_tespit==2:
                        for i in range(robot_x,180):
                                rotateServo_3(pin_3,i)
                        sleep(1)        
                        for i in range(180,100,-1):
                                rotateServo_2(pin_2,i)
                        sleep(1)
                        for i in range(20,70):
                                rotateServo(pin,i) 
                        sleep(1)                                   
                        board.digital[pin_4].write(180) 
                        sleep(1)
                        for i in range(100,180):
                                rotateServo_2(pin_2,i)
                        for i in range(70,20,-1):
                                rotateServo(pin,i) 

                        #Hom Pos
                        sleep(1)
                        board.digital[pin_4].write(130)
                        sleep(1)
                        for i in range(180,0,-1):
                                rotateServo_3(pin_3,i) 
                        sleep(1)
                        for i in range(20,30):
                                rotateServo(pin,i)
            
               break
        #----------------Tuş deneme------------------------
        if Tiklama(0x46)== True: #f tusu
            print(Tiklama(0x46))
            sleep(0.5)
        #---------------------------------------
        if cv2.waitKey(100000) & 0xFF == ord("q"): #cv2.waitkey(x) x kaç saniyede bir fotograf çekecegini belirliyoruz
          break
    except ZeroDivisionError:
        print("\n \x1b[41;31;1m Yeterli Isik yok veya nesne tespit edilemiyor\x1b[0m \n")#ansicolor

kamera.relase()
cv2.destroyAllWindows()