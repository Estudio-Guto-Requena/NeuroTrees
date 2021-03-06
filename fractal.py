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

dim = (2*770,770)

med = 0
at = 0
sig = 0

go = True
start = False

Tserver = 0
Tmonitor = 0
Tmain = 0

def monitor():
    global go
    print('monitor')
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print('Close')
                go = False
                Tserver.join()
                Tmain.join()
                pygame.quit()
                exit()
        time.sleep(0.01)


def startServer():
    global at, sig, med, go
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(2)
    # Bind the socket to the port
    server_address = (ip, port)
    s.bind(server_address)
    while go:
        try:
            data, address = s.recvfrom(4096)
            start = True
            neural = json.loads(data.decode('utf-8'))
            med = neural['meditation']
            at = neural['attention']
            sig = neural['quality']
            print(neural)
        except socket.timeout as e:
            start = False
            print(e)

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


def main():
    global go
    infoObject = pygame.display.Info()
    screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h))
    s,deg,size,pos_init = tree2((infoObject.current_w, infoObject.current_h), 5)
    print("main")
    while(go):

        if(sig < 100):
            font = pygame.freetype.Font('./OpenSans-Regular.ttf', 30)
            pygame.draw.rect(screen, (0,0,0), pygame.Rect(10, 10, 250, 250))
            font.render_to(screen, (10, 10), 'Low Signal: ' + str(sig) +'%', (255, 0, 0))
            pygame.display.update()
            time.sleep(1)

        elif(start and sig >=100):
            screen.fill(BG_COLOR)
            pos = pos_init
            angle = -120
            saved_angles = []
            saved_poses = []
            tam  = len(s)
            font = pygame.freetype.Font('./OpenSans-Regular.ttf', 15)
            i = 0

            for letter in s:
                if (not go):
                    break
                if (letter == 'F'):
                    unit = 2
                    dx = cos(radians(angle))*unit*size
                    dy = sin(radians(angle))*unit*size
                    f = (at/100.)
                    da = deg + np.random.uniform(-deg*f,deg*f)
                    if(sig < 100):
                        color = pygame.Color(0, 128, 128, 0)
                    else:
                        color = pygame.Color(int(180.*(1.-(med/100.)))+40, 0, int(180. * (med/100.) )+40, 0)
                    pygame.draw.line(screen, color, pos, (pos[0]+dx,pos[1]+dy), 1+int(2*(1.0-i/tam)))
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
    pygame.init()
    Tserver = threading.Thread(target=startServer)
    Tmonitor = threading.Thread(target=monitor)
    Tmain = threading.Thread(target=main)
    Tserver.start()
    Tmonitor.start()
    Tmain.start()
