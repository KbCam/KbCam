import cv2
import numpy as np
from pynput.mouse import Button, Controller
import wx
mouse=Controller()

app=wx.App(False)

#sx, sy sont la résolution de l'écran
(sx,sy)=wx.GetDisplaySize()
(camx,camy)=(320,240)

#seuil de reconnaissance des couleurs
borneMin=np.array([33,80,40])
borneMax=np.array([102,255,255])

cam= cv2.VideoCapture(0)

kernelOpen=np.ones((5,5))
kernelClose=np.ones((20,20))
pinchFlag=0

while True:
    ret, img=cam.read() 
    img=cv2.resize(img,(340,220))

    #convertir BGR à HSV
    imgHSV= cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    # create the Mask
    mask=cv2.inRange(imgHSV,borneMin,borneMax)
    #morphology
    maskOpen=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)
    maskClose=cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)

    maskFinal=maskClose
    conts,h=cv2.findContours(maskFinal.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    
    # condition de départ, notre tableau contient bien 2 objets 
    if(len(conts)==2):
        #si pince, activer clique gauche de la souris
        if(pinchFlag==1):
            pinchFlag=0
            mouse.release(Button.left)
        #récupérer les coordonnés des objets 
        x1,y1,w1,h1=cv2.boundingRect(conts[0])
        x2,y2,w2,h2=cv2.boundingRect(conts[1])

        #dessiner rectangle bleu autours des objets 

        cv2.rectangle(img,(x1,y1),(x1+w1,y1+h1),(255,0,0),2)
        cv2.rectangle(img,(x2,y2),(x2+w2,y2+h2),(255,0,0),2)

        #calculer le centre des objets 
        cx1=int(x1+w1/2)
        cy1=int(y1+h1/2)
        cx2=int(x2+w2/2)
        cy2=int(y2+h2/2)

        #calcul du point moyen reliant les 2 objets

        cx=int((cx1+cx2)/2)
        cy=int((cy1+cy2)/2)

        #dessin de la ligne reliant les 2 objets
        cv2.line(img, (cx1,cy1),(cx2,cy2),(255,0,0),2)

        #dessin du point moyen
        cv2.circle(img, (cx,cy),2,(0,0,255),2)

        #calcul de la position de la souris(conversion de taille caméra à taille écran)
        mouseLoc=(sx-(cx*sx/camx), cy*sy/camy)
        mouse.position=mouseLoc


        #attente pour éviter les latences
        while mouse.position!=mouseLoc:
            pass
    elif(len(conts)==1):
        x,y,w,h=cv2.boundingRect(conts[0])
        if(pinchFlag==0):
            pinchFlag=1
            mouse.press(Button.left)
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        cx=int(x+w/2)
        cy=int(y+h/2)
        cv2.circle(img,(cx,cy),int((w+h)/4),(0,0,255),2)
        mouseLoc=(sx-(cx*sx/camx), cy*sy/camy)
        mouse.position=mouseLoc
        while mouse.position!=mouseLoc:
            pass
    cv2.imshow("cam",img)
    cv2.waitKey(5)