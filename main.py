import pygame, sys
from pygame.locals import *
import time
import random
import colorsys
from math import *

#constants
window_size = 700
height = window_size
width = int(window_size*1.5)
size = window_size//12 + 1
gain = .001
MOUSE_DOWN = 5
MOUSE_UP = 6
MOUSE_MOVE = 4
SPACE = 32
pressed = False

# set up the colors
BLACK = (0, 0, 0)
GRAY = (127, 127, 127)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 127, 0)
YELLOW = (255,255,0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (255,0,255)
PINK = (255, 56, 215)

class Hex:
    def __init__(self, pos, i):
        self.name = str(i)
        #pos = [horz, vert]
        self.pos = pos
        self.size = size
        self.color = GRAY
        self.button_color = WHITE
        self.light = 0 #goes from 0 to 1
        self.start = millis()
        self.timer = millis()
        self.tic = .1
        self.power = random.randint(0,int(self.tic*12000))
        #self.power = 0
        self.update_verts()
        return
    def update_verts(self):
        pos = self.pos
        pi2 = 2*3.14
        self.all_verts= [(int(cos(i / 6 * pi2) * size + pos[0]), int(sin(i / 6 * pi2) * size + pos[1])) for i in range(0, 6)]
        self.button_verts= [(int(cos(i / 6 * pi2) * size/5 + pos[0]), int(sin(i / 6 * pi2) * size/5 + pos[1])) for i in range(0, 6)]
        #get the led points
        self.led_points = []
        scale = 1.35
        shortened_verts= [(int(cos(i / 6 * pi2) * size/scale + pos[0]), int(sin(i / 6 * pi2) * size/scale + pos[1])) for i in range(0, 6)]
        temp = [vert for vert in shortened_verts]
        temp.append(temp[0])
        for i in range(len(shortened_verts)):
            x1 = temp[i][0]
            y1 = temp[i][1]
            x2 = temp[i+1][0]
            y2 = temp[i+1][1]
            new_x = (x1+x2)//2
            new_y = (y1+y2)//2
            self.led_points.append((new_x, new_y))
        return

    def update(self, hexes):
        if (millis() - self.timer) > self.tic:
            #print("updating")
            #print(self.power)
            if self.light > 0:
                if (millis() - self.start) > self.tic*10000:
                    self.light = 0
                else:
                    self.light = self.light - .001
            else:
                self.power = self.power + 1
                if self.power > self.tic*12000:
                    self.power = 0
                    self.light = 1
                    #print(self.name, millis() - self.start)
                    self.start = millis()
                self.timer = millis()
        self.check_near(hexes)
        return

    def draw(self):
        #draw the base
        pygame.draw.polygon(windowSurface, self.color, self.all_verts)
        #draw the button to reset
        pygame.draw.polygon(windowSurface, self.button_color, self.button_verts)
        #draw the LEDS
        led_color = (0,int(255*self.light),0)
        for led in self.led_points:
            pygame.draw.circle(windowSurface, led_color, led, size//5, 0)
        return

    def handle_click(self, pos):
        if self.is_inside(pos, self.button_verts):
            self.power = 0
            self.light = 1
            self.timer = millis()
            self.start = millis()
        return

    def move_to(self, pos):
        self.pos = pos
        self.update_verts()

    def is_inside(self, pos, poly = None):
        if poly is None:
            poly = self.all_verts
        x = pos[0]
        y = pos[1]
        n = len(poly)
        inside = False

        p1x,p1y = poly[0]
        for i in range(n+1):
            p2x,p2y = poly[i % n]
            if y > min(p1y,p2y):
                if y <= max(p1y,p2y):
                    if x <= max(p1x,p2x):
                        if p1y != p2y:
                            xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or x <= xints:
                            inside = not inside
            p1x,p1y = p2x,p2y

        return inside

    def check_near(self, hexes):
        radius = int(size*2)
        near = False
        for hex in hexes:
            if self.distance_between_points(self.pos, hex.pos) < radius and (self.name != hex.name):
                if hex.light > 0:
                    self.power = self.power * (1+gain*hex.light)
                    #print(self.name, "gaining")
                near = True
        if near:
            self.button_color = PINK
        else:
            self.button_color = WHITE

    def distance_between_points(self, pos1, pos2):
        x1 = pos1[0]
        y1 = pos1[1]
        x2 = pos2[0]
        y2 = pos2[1]
        return sqrt((x1-x2)**2 + (y1-y2)**2)



def millis():
    return time.time()*1000


# set up pygame
pygame.init()

# set up the window
windowSurface = pygame.display.set_mode((width, height), 0, 32)
pygame.display.set_caption('blinky-blinky')

# draw the background onto the surface
windowSurface.fill(BLACK)
height_scalar = height//7
width_scalar = width//7
hex0 = Hex((2*width_scalar,1*height_scalar),0)
hex1 = Hex((4*width_scalar,1*height_scalar),1)
hex2 = Hex((2*width_scalar,3*height_scalar),2)
hex3 = Hex((4*width_scalar,3*height_scalar),3)
hex4 = Hex((2*width_scalar,5*height_scalar),4)
hex5 = Hex((4*width_scalar,5*height_scalar),5)

hexes = []
hexes.append(hex0)
hexes.append(hex1)
hexes.append(hex2)
hexes.append(hex3)
hexes.append(hex4)
hexes.append(hex5)
moving = -1

# draw the window onto the screen
pygame.display.update()

# run the game loop
while True:
    windowSurface.fill(BLACK)
    for hex in hexes:
        hex.update(hexes)
    for event in pygame.event.get():
        if event.type == 2:
            if event.key == SPACE:
                for i in range(len(hexes)):
                    hexes[i].power = random.randint(0,int(hexes[i].tic*12000))
        if event.type == MOUSE_DOWN:
            pressed = True
            moving = -1
            for i in range(len(hexes)):
                inside = hexes[i].is_inside(event.pos)
                if inside:
                    hexes[i].handle_click(event.pos)
                    moving = i

        if event.type == MOUSE_UP:
            pressed = False
            moving = -1

        if event.type == MOUSE_MOVE and pressed:
            hexes[moving].move_to(event.pos)

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    for hex in hexes:
        hex.draw()
    pygame.display.update()

# draw a circle onto the surface
#pygame.draw.circle(windowSurface, BLUE, (300, 50), 20, 0)
