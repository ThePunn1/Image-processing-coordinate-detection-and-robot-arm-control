from pyfirmata import Arduino, SERVO     #Arduino ile haberleşme kütüphanesi
from time import sleep                   #Delay kütüphanesi      
from win32api import GetKeyState, Sleep  #Tuş kütüphanesi
import cv2                               #Görüntü işleme kütüphanesi
import numpy as np                       #Diziler için numpy kütüphanesi

port='COM3'
pin = 8               # Y ekseni hareket pini (0-140) Max:140
pin_2=9               # Z ekseni hareket pini (80-180) Max: 180 (Yukarı)
pin_3=7               # X ekseni hareket pini (0-180) (0:Sol 180:Sağ)
pin_4=10              # Gripper  (130-180) (130:Kapalı,180:Açık) 
board = Arduino(port) # Arduino port ile baglantı sağlanılıyor
 
board.digital[pin].mode = SERVO           # Bağlanan pinler servolara atanıyor
board.digital[pin_2].mode = SERVO
board.digital[pin_3].mode = SERVO
board.digital[pin_4].mode = SERVO

def rotateServo(pin, angle):              # Servo 1 derece donme yaptıgında oluşacak olan             
        board.digital[pin].write(angle)   # delay ayarlanıyor
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

def Tiklama(tus):                  # Bu Tiklama fonksuyonun kullanım amacı sistem çalışırken 
    state=GetKeyState(tus)         # bekleme işlemi ortadan kaldırmak için kullanılıyor   
    if (state!=0) and (state !=1): # "f" tusuna basarak tetikleniyor
        return print("Fotograf Alınıyor")    

kamera=cv2.VideoCapture(0)                 # Kamera bağlantısı yapılıyor dışardan oldugu için
                                           # 0 değerini alıyor dahili olsaydı 1 olurdu.

while True:                                # Ana while döngümüz
    try:
        renk_tespit=0                      # renk_tespit renklere göre değer alıyor 
        while True:                        # Bu while döngüsünde arduino servoları ana 
                rotateServo(pin, 30)       # ana pozisyona yolluyor.
                rotateServo_2(pin_2, 170) 
                rotateServo_3(pin_3, 0)   
                rotateServo_4(pin_4, 130) 
                sleep(1)
                break

        kontrol,frame=kamera.read()                           # Kameradan gelen görüntüyü okuma
        cut_kamera=frame[100:550,100:550]                     # Kamera gelen görüntüyü kirpma 
        ters_gor = cv2.rotate(cut_kamera, cv2.cv2.ROTATE_180) # Gelen görüntüyü ters çevirme
        cv2.imshow("Orjinal",ters_gor)                        # Gelen görüntüyü ekrana çıktı verme
        
        hsv_frame=cv2.cvtColor(ters_gor,cv2.COLOR_BGR2HSV)        # Görüntüyü HSV renk uzayına dönüştürüyor        
        Lower_red=np.array([1, 30, 20])                           # Kırmızı için en düşük renk degeri belirliyoruz
        Upper_red=np.array([10, 255, 255])                        # Yeşil için en düşük renk degeri belirliyoruz
        red_mask=cv2.inRange(hsv_frame,Lower_red,Upper_red)       # Girilen değerler arasında renk seçmeye yarar
        red=cv2.bitwise_and(ters_gor , ters_gor , mask = red_mask)# Pikselleri sadeleştiriyor
        
        Lower_green=np.array([38, 100, 100])
        Upper_green=np.array([75, 255, 255])
        green_mask=cv2.inRange(hsv_frame,Lower_green,Upper_green)
        
        #------------------Renk tespit-------------------------
        kernal = np.ones((5, 5), "uint8")                                                       # 5x5 bir filtreoluşturuyoruz
        red_mask = cv2.dilate(red_mask, kernal)                                                 # Filtreyi uyguluyoruz
        res_red=cv2.bitwise_and(ters_gor,ters_gor,mask=red_mask)                                
        contours, hierarchy = cv2.findContours(red_mask,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # Şekilleri tespit etmek için
        for pic, contour in enumerate(contours):                                                # Tespit edilen pikseller dongude sayılıyor
            area = cv2.contourArea(contour)                                                     # Pikselleri birleştirmek için kullanılıyor
            if (area>300):                                                                      # Toplam piksellere gore tespit yapıyor
                x,y,w,h=cv2.boundingRect(contour)                                               # Cizmin olduğu bölge tespit ediliyor
                ters_gor=cv2.rectangle(ters_gor,(x,y),(x+w,y+h),(0,0,255),2)                    # Kare çizmek için kullanıyoruz
                renk_tespit=1                                                                   # Kırmızı olduğu tespit ediliyor
                cv2.putText(ters_gor,"Kirmizi Renk",(x,y),cv2.FONT_HERSHEY_SIMPLEX,1.0,(0,0,255)) # Görüntünün üstüne renk yazmak için kullanılıyor
        cv2.imshow("Renk_tespit", ters_gor)                                                     # Renk tespit edilen görüntü ekrana veriliyor

        green_mask = cv2.dilate(green_mask, kernal)                                             #Kırmızı için yapılan olayların aynısı 
        res_green=cv2.bitwise_and(ters_gor,ters_gor,mask=green_mask)                            # yeşil içinde uygulanıyor.
        contours, hierarchy = cv2.findContours(green_mask,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for pic, contour in enumerate(contours):
            area = cv2.contourArea(contour) 
            if (area>300):
                x,y,w,h=cv2.boundingRect(contour)
                frame=cv2.rectangle(ters_gor,(x,y),(x+w,y+h),(0,255,0),2)
                renk_tespit=2
                cv2.putText(ters_gor,"Yesil Renk",(x,y),cv2.FONT_HERSHEY_SIMPLEX,1.0,(0,255,0))
        cv2.imshow("Renk_tespit", ters_gor)

        #------------------Kordinat Tespit--------------------
        if renk_tespit==1:                                   # Kırmızı renk için hesaplanıyor
            ret,thresh = cv2.threshold(red_mask,127,255,0)   # Eşlik değerleri ayarlanıyor
            cv2.imshow("Siyah-Beyaz",red_mask)               # Siyah beyaz goruntu ekrana geliyor
            cv2.imshow("Kirmizi",red)                        # Kırmızı görüntü ekrana geliyor
        elif renk_tespit==2:
            ret,thresh = cv2.threshold(green_mask,127,255,0)
            cv2.imshow("Siyah-Beyaz",green_mask)
            cv2.imshow("Yesil",res_green)
        contours,hierarchy = cv2.findContours(thresh, 1, 2)  # Yan yan bütün olan pikselleri tespit ediyor.
        cnt = contours[0]                                    # Bütün olan pikseller toplanıp ortalama değer alınır.
        M = cv2.moments(cnt)                                 # Bu piksellerin yogunluk ortalması 
        print( M )

        cx = int(M['m10']/M['m00'])                          # X ekseninde piksellerin orta noktasını tespit eder
        cy = int(M['m01']/M['m00'])                          # Y ekseninde piksellerin orta noktasını tespit eder   
        area = cv2.contourArea(cnt)                            
        print("Kamera Kordinat:"+str(cx))                    # X çıktısı
        print("Kamera Kordinat:"+str(cy))                    # Y çıktısı

        #-----------------Robot kol derece hesaplama--------------------
        robot_x = 0                              # Robot X eksen değeri 0 lanıyor
        robot_y = 0                              # Robot Y eksen değeri 0 lanıyor

        kor_x = cx                               # Tespit edilen kordinat aktarılıyor
        kor_y = cy

        y_katsayi=5.65                           # Y ekseni için hesaplanmış katsayı
        x_katsayi = (kor_x*0.2)                  # X ekseni için oluşturulmuş denklem

        if kor_x<250:
            robot_x = x_katsayi + 45
        else:
            robot_x = x_katsayi + 30

        robot_y=int((kor_y/y_katsayi)+25)        #Robot servo dereceleri hesaplanıyor ve gönderiliyor
        robot_x=int(robot_x)
        print("Robot Kol X Deger:"+str(robot_x))
        print("Robot Kol Y Deger:"+str(robot_y))
        #-------------------Robot_kol_kodları-------------------------
        while True:                                 # Bu while dögüsünde robot kol X ve Y eksenide gelen dereceye 
               for i in range(0,180):               # yönelip parçayı alma işlemi gerçekleşiyor ardından
                   if i<robot_x:                    # tespit edilen renge göre sağ yada sola bırakma işlemi gerçekleşiyor
                           rotateServo_3(pin_3,i)   # ve tekrar ana pozisyona dönüyor
               sleep(1)
               board.digital[pin_4].write(180)    
               sleep(1)
               for i in range(0,140):
                       if i<robot_y:
                               rotateServo(pin,i)
               sleep(1)
               for i in range(170,90,-1):
                       rotateServo_2(pin_2,i)
               sleep(2)
               board.digital[pin_4].write(130)
               sleep(1)   
               for i in range(90,170):
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
        #----------------Tuş------------------------
        if Tiklama(0x46)== True: #F tusu basılınca hızlandırma
            print(Tiklama(0x46))
            sleep(0.5)
        #---------------------------------------
        if cv2.waitKey(100000) & 0xFF == ord("q"): # Kaç saniyede bir goruntu alınacgını belirliyoruz 
          break
    except ZeroDivisionError:                      #Cisim tespit edilemediginde tekra tespit etmeye çalışıyor
        print("\n \x1b[41;31;1m Yeterli Isik yok veya nesne tespit edilemiyor\x1b[0m \n")#ansicolor

kamera.relase()           #Kamera ve ekranda açık olan görüntüler kapatılıyor
cv2.destroyAllWindows()