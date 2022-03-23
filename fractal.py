import pygame
from pygame.locals import *
import pygame.freetype
from math import *
import numpy as np
import time
import socket
import sys
import json
import threading

BG_COLOR = [0,0,0]
ip = "0.0.0.0"
port = 5005

med = 0
at = 0
sig = 0

go = True




def startServer():
    global at, sig, med
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind the socket to the port
    server_address = (ip, port)
    s.bind(server_address)
    while True:
        data, address = s.recvfrom(4096)
        neural = json.loads(data.decode('utf-8'))
        med = neural['meditation']
        at = neural['attention']
        sig = neural['quality']
        print(neural)

def tree(dim, iterations):
    s = ['X']
    deg = 22.5
    size = 1.2
    pos = dim[0]/2.,dim[1]
    for i in range(iterations):
        X_make = ['F', '-', '[', '[', 'X', ']', '+', 'X', ']', '+', 'F', '[', '+', 'F', 'X', ']', '-', 'X']
        F_make = ['F','F']
        j = 0
        while j<len(s):
            if s[j] == 'X':
                s.pop(j)
                for item in X_make[::-1]: s.insert(j,item)
                j+=len(X_make)-1
            elif s[j] == 'F':
                s.pop(j)
                for item in F_make[::-1]: s.insert(j,item)
                j+=len(F_make)-1
            j+=1
    return s, deg, size, pos

def tree2(dim, iterations):
    s = ['F']
    pos = dim[0]/2.,dim[1]
    for i in range(iterations):
        #X -> F-[[X]+X]+F[+FX]-X
        #F- > FF
        deg = 22.5
        size = 3.3
        X_make = ['F', '-', '[', '[', 'X', ']', '+', 'X', ']', '+', 'F', '[', '+', 'F', 'X', ']', '-', 'X']
        F_make = ['F','F','+','[','+','F','-','F','-','F',']','-','[','-','F','+','F','+','F',']']
        j = 0
        while j<len(s):
            if s[j] == 'X':
                s.pop(j)#replace X with our X_make list
                for item in X_make[::-1]: s.insert(j,item)
                j+=len(X_make)-1#bump j up to skip over added items
            elif s[j] == 'F':
                s.pop(j)
                for item in F_make[::-1]: s.insert(j,item)
                j+=len(F_make)-1
            j+=1
    return s, deg, size, pos


def main(dim):
    pygame.init()
    screen = pygame.display.set_mode((dim[0], dim[1]))
    s,deg,size, pos_init = tree2(dim, 5)

    while(1):
        while(sig < 100):
            font = pygame.freetype.Font('/home/whitefox/Documents/Work/fractal/OpenSans-Regular.ttf', 30)
            pygame.draw.rect(screen, (0,0,0), pygame.Rect(10, 10, 250, 250))
            font.render_to(screen, (10, 10), 'Low Signal: ' + str(sig) +'%', (255, 0, 0))
            pygame.display.update()
            time.sleep(1)
        screen.fill(BG_COLOR)
        if(go):
            pos = pos_init
            angle = -120
            saved_angles = []
            saved_poses = []
            tam  = len(s)
            font = pygame.freetype.Font('/home/whitefox/Documents/Work/fractal/OpenSans-Regular.ttf', 15)
            i = 0
            for letter in s:
                if letter == 'F':
                    unit = 2
                    dx = cos(radians(angle))*unit*size
                    dy = sin(radians(angle))*unit*size
                    f = (at/100.)
                    #da = np.random.uniform(-deg*f,deg*f)
                    da = deg + np.random.uniform(-deg*f,deg*f)
                    a = abs(angle)
                    if(sig < 100):
                        color = pygame.Color(0, 128, 128, 0)
                    else:
                        color = pygame.Color(int(180.*(1.-(med/100.)))+40, 0, int(180. * (med/100.) )+40, 0)
                    pygame.draw.line(screen,color,pos,(pos[0]+dx,pos[1]+dy),1+int(2*(1.0-i/tam)))
                    pygame.draw.rect(screen, (0,0,0), pygame.Rect(10, 10, 150, 80))
                    font.render_to(screen, (10, 10), 'Signal: ' + str(sig) +'%', (255, 0, 0))
                    font.render_to(screen, (10, 30), 'Attention: ' + str(at) + '%', (255, 0, 0))
                    font.render_to(screen, (10, 50), 'Meditation: ' + str(med) + '%', (255, 0, 0))
                    pygame.display.update()
                    time.sleep(0.01)
                    pos = (pos[0]+dx, pos[1]+dy)

                elif letter == '+':
                    angle += da
                elif letter == '-':
                    angle -= da
                elif letter == '[':
                    saved_poses.append(pos)
                    saved_angles.append(angle)
                elif letter == ']':
                    #pygame.draw.circle(screen,(50,205,50),(int(pos[0]),int(pos[1])),2)
                    pos = saved_poses.pop()
                    angle = saved_angles.pop()
                i += 1



if __name__ == '__main__':
    threading.Thread(target=startServer).start()
    main((int(2*770),int(770)))
