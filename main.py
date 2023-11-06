import os
import struct
from typing import Tuple, Any

from typing import Tuple, Any

import keyboard
import math
import numpy as np

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLU import *
import pygame
from pygame.locals import *

import PySimpleGUI as sg

vertex_shader = """
varying vec3 vN;
varying vec3 v;
varying vec4 color;
void main(void)
{
   v = vec3(gl_ModelViewMatrix * gl_Vertex);
   vN = normalize(gl_NormalMatrix * gl_Normal);
   color = vec4(vN,1.0);
   gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}
"""

fragment_shader = """
varying vec4 color;
#define MAX_LIGHTS 1 
void main (void) 
{ 
   gl_FragColor = color; 
}
"""

class Vertex:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):
        if isinstance(other, Vertex):
            return self.x == other.x and self.y == other.y and self.z == other.z
        return NotImplemented

    def __hash__(self):
        return hash((self.x, self.y, self.z))
    def getXYZ(self):
        return self.x,self.y,self.z

layout = [[sg.Text("Controlls")],
          [sg.Text("X-Pos:  "), sg.InputText()],
          [sg.Text("Y-Pos:  "), sg.InputText()],
          [sg.Text("Z-Pos:  "), sg.InputText()],
          [sg.Text("X-Rot:  "), sg.Slider(range=(-180, 180), default_value=0, orientation='horizontal')],
          [sg.Text("Y-Rot:  "), sg.Slider(range=(-180, 180), default_value=0, orientation='horizontal')],
          [sg.Text("Z-Rot:  "), sg.Slider(range=(-180, 180), default_value=0, orientation='horizontal')],
          [sg.Text("Scale:  "), sg.Button(button_text="   -   "), sg.Button(button_text="   +   ")],
          [sg.Text("Flat-Shading"), sg.Radio('', 'RAD1', default=True, key='Flat')],
          [sg.Text("Gouraud-Shading"), sg.Radio('', 'RAD1', default=False, key='Gouraud')],
          [sg.Text("Mixed-Shading"), sg.Radio('', 'RAD1', default=False, key='Mixed')],
          [sg.Button(button_text="OK")]]

pos_delta = 0.1

#check if pos1 is in "pos_delta" range of pos 2
def is_in_range(pos1, pos2):
    if pos1.x < (pos2.x + pos_delta) and pos1.x > (pos2.x - pos_delta):
        if pos1.y < (pos2.y + pos_delta) and pos1.y > (pos2.y - pos_delta):
            if pos1.z < (pos2.z + pos_delta) and pos1.z > (pos2.z - pos_delta):
                return True
    return False

def angle_between(v1, v2):
    angle = np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    return angle/np.pi * 180




# class for a 3d point
class createpoint:
    def __init__(self, p, c=(1, 0, 0)):
        self.point_size = 0.5
        self.color = c
        self.x = p[0]
        self.y = p[1]
        self.z = p[2]

    def glvertex(self):
        glVertex3f(self.x, self.y, self.z)


# class for a 3d face on a model
class createtriangle:
    points = None
    normal = None

    def __init__(self, p1, p2, p3, n=None):
        # 3 points of the triangle
        self.points = createpoint(p1), createpoint(p2), createpoint(p3)

        # triangles normal
        self.normal = createpoint(self.calculate_normal(self.points[0], self.points[1], self.points[2]))  # (0,1,0)#

    # calculate vector / edge
    def calculate_vector(self, p1, p2):
        return -p1.x + p2.x, -p1.y + p2.y, -p1.z + p2.z

    def calculate_normal(self, p1, p2, p3):
        a = self.calculate_vector(p3, p2)
        b = self.calculate_vector(p3, p1)
        # calculate the cross product returns a vector
        return self.cross_product(a, b)

    def cross_product(self, p1, p2):
        return (p1[1] * p2[2] - p2[1] * p1[2]), (p1[2] * p2[0]) - (p2[2] * p1[0]), (p1[0] * p2[1]) - (p2[0] * p1[1])


class loader:
    model = []
    verticesDict = {}

    # return the faces of the triangles
    def get_triangles(self):
        if self.model:
            for face in self.model:
                yield face

    #Check if Triangle is part of a Corner
    def is_triangle_corner(self,triangle):
        for point in triangle.points:
            cur = self.verticesDict.get(Vertex(point.x, point.y, point.z))
            if cur[3]:
                return True
        return False
    
    # draw the models faces
    def draw(self,mode):
        glUseProgram(program)
        if mode == 1: # Flat-Shading
            glBegin(GL_TRIANGLES)
            for tri in self.get_triangles():
                glNormal3f(-tri.normal.x, -tri.normal.y, -tri.normal.z)
                glVertex3f(tri.points[0].x, tri.points[0].y, tri.points[0].z)
                glVertex3f(tri.points[1].x, tri.points[1].y, tri.points[1].z)
                glVertex3f(tri.points[2].x, tri.points[2].y, tri.points[2].z)
            
            glEnd()
        elif mode == 2: #Gouraud-Shading
            glBegin(GL_TRIANGLES)  #https://docs.gl/gl3/glBegin
            for tri in self.get_triangles():
                for point in tri.points:
                    curVertex = Vertex(point.x, point.y, point.z)
                    cur = self.verticesDict.get(curVertex)
                    glNormal3f(cur[1][0],cur[1][1],cur[1][2])
                    glVertex3f(point.x,point.y,point.z)
            glEnd()
        elif mode == 3: #Mixed-Shading
            glBegin(GL_TRIANGLES)
            for tri in self.get_triangles():
                isCorner = self.is_triangle_corner(tri)
                for point in tri.points:
                    curVertex = Vertex(point.x, point.y, point.z)
                    cur = self.verticesDict.get(curVertex)
                    glNormal3f(cur[1][0],cur[1][1],cur[1][2])
                    glVertex3f(point.x,point.y,point.z)
                if isCorner:
                    glNormal3f(-tri.normal.x, -tri.normal.y, -tri.normal.z)
                    glVertex3f(tri.points[0].x, tri.points[0].y, tri.points[0].z)
                    glVertex3f(tri.points[1].x, tri.points[1].y, tri.points[1].z)
                    glVertex3f(tri.points[2].x, tri.points[2].y, tri.points[2].z)
            glEnd()

        glUseProgram(0)

    #count all adjacent triangles to all points of all triangles
    def count_adjacent(self):
        positions = []  #list of registered positions
        #tri_counter = 0 #
        for tri in self.get_triangles():    #for all triangles in model
            #tri_counter += 1       #test to check if all triangles are checked
            #print(str(tri_counter) + ": [" + str(tri.points[0].x) + ", " + str(tri.points[0].y) + ", " + str(tri.points[0].z) + 
            #      "],[" + str(tri.points[1].x) + ", " + str(tri.points[1].y) + ", " + str(tri.points[1].z) + 
            #      "],[" + str(tri.points[2].x) + ", " + str(tri.points[2].y) + ", " + str(tri.points[2].z) + "]")
            for pos in tri.points:      #for all 3 points of triangle
                counter = 0
                already_saved = False
                if len(positions) == 0:     #if no points saved, count adjacent and save
                    positions.append(pos)
                    for triangle in self.get_triangles():
                        for point in triangle.points:
                            if is_in_range(point, pos):
                                counter += 1
                    print(str(counter) + " : " + str(pos.x) + "," + str(pos.y) + ","+ str(pos.z))
                for savedPosition in positions:     #chek if point has been saved before
                    if is_in_range(pos, savedPosition):
                        already_saved = True
                if not already_saved:               # if it hasn't been saved, count adjacent and save
                    positions.append(pos)
                    for triangle in self.get_triangles():
                        for point in triangle.points:
                            if is_in_range(point, pos):
                                counter += 1
                    #show number of adjacent triangles to point
                    print(str(counter) + " : " + str(pos.x) + "," + str(pos.y) + ","+ str(pos.z))
                else:
                    already_saved = False

    # load stl file detects if the file is a text file or binary file
    def load_stl(self, filename):
        # read start of file to determine if its a binay stl file or a ascii stl file
        fp = open(filename, 'rb')
        h = fp.read(80)
        type = h[0:5]
        fp.close()

        if type == 'solid':
            print
            "reading text file" + str(filename)
            self.load_text_stl(filename)
        else:
            print
            "reading binary stl file " + str(filename, )
            self.load_binary_stl(filename)
            self.load_binary_stl_cornerNormals(filename)

    # read text stl match keywords to grab the points to build the model
    def load_text_stl(self, filename):
        fp = open(filename, 'r')

        for line in fp.readlines():

            triangle = []
            normal: tuple[Any, Any, Any] = (1, 2, 3)  # dummy init
            words = line.split()
            if len(words) > 0:
                if words[0] == 'solid':
                    self.name = words[1]

                if words[0] == 'facet':
                    center = [0.0, 0.0, 0.0]
                    normal: tuple[Any, Any, Any] = (eval(words[2]), eval(words[3]), eval(words[4]))
                    print(normal)

                if words[0] == 'vertex':
                    triangle.append((eval(words[1]), eval(words[2]), eval(words[3])))

                if words[0] == 'endloop':
                    # make sure we got the correct number of values before storing
                    if len(triangle) == 3:
                        self.model.append(createtriangle(triangle[0], triangle[1], triangle[2], normal))
        fp.close()
    
    def load_binary_stl_cornerNormals(self, filename):
        fp = open(filename, 'rb')
        h = fp.read(80)

        l = struct.unpack('I', fp.read(4))[0]
        count = 0
        while True:
            try:
                n = [0, 0 ,0]
                p = fp.read(12)
                if len(p) == 0:  # moved to here, otherwise the last triangle is added tiwce!
                    break
                if len(p) == 12:
                    n = struct.unpack('f', p[0:4])[0], struct.unpack('f', p[4:8])[0], struct.unpack('f', p[8:12])[0]

                p = fp.read(12)
                if len(p) == 12:
                    p1 = struct.unpack('f', p[0:4])[0], struct.unpack('f', p[4:8])[0], struct.unpack('f', p[8:12])[0]
                    curVertex = Vertex(p1[0], p1[1], p1[2])
                    cur = self.verticesDict.get(curVertex)
                    if cur is None:
                         self.verticesDict.update({curVertex: [1, n, [n], False]}) 
                        # self.verticesDict.update({curVertex: [1, [n]]})
                    else:
                        newNormal = [cur[1][0] + n[0], cur[1][1] + n[1], cur[1][2] + n[2]]
                        normals = cur[2]
                        isCorner = False
                        for vector in normals:
                            if 80 < angle_between(vector,n) < 100:
                                isCorner = True
                                break
                        normals.append(n)
                        # curNormal = cur[1]
                        # curNormal.append(n)
                        # self.verticesDict.update({curVertex: [1 + cur[0], curNormal]})
                        if isCorner:
                            self.verticesDict.update({curVertex: [1 + cur[0], newNormal, normals, True]})
                        else:
                            self.verticesDict.update({curVertex: [1 + cur[0], newNormal, normals, cur[3]]})

                p = fp.read(12)
                if len(p) == 12:
                    p2 = struct.unpack('f', p[0:4])[0], struct.unpack('f', p[4:8])[0], struct.unpack('f', p[8:12])[0]
                    curVertex = Vertex(p2[0], p2[1], p2[2])
                    cur = self.verticesDict.get(curVertex)
                    if cur == None:
                        self.verticesDict.update({curVertex: [1, n, [n], False]})
                        # self.verticesDict.update({curVertex: [1, [n]]})
                    else:
                        newNormal = [cur[1][0] + n[0], cur[1][1] + n[1], cur[1][2] + n[2]]
                        normals = cur[2]
                        isCorner = False
                        for vector in normals:
                            if 80 < angle_between(vector,n) < 100:
                                isCorner = True
                                break
                        normals.append(n)
                        # curNormal = cur[1]
                        # curNormal.append(n)
                        # self.verticesDict.update({curVertex: [1 + cur[0], curNormal]})                        
                        if isCorner:
                            self.verticesDict.update({curVertex: [1 + cur[0], newNormal, normals, True]})
                        else:
                            self.verticesDict.update({curVertex: [1 + cur[0], newNormal, normals, cur[3]]})

                p = fp.read(12)
                if len(p) == 12:
                    p3 = struct.unpack('f', p[0:4])[0], struct.unpack('f', p[4:8])[0], struct.unpack('f', p[8:12])[0]
                    curVertex = Vertex(p3[0], p3[1], p3[2])
                    cur = self.verticesDict.get(curVertex)
                    if cur == None:
                        self.verticesDict.update({curVertex: [1, n, [n], False]})
                        # self.verticesDict.update({curVertex: [1, [n]]})
                    else:
                        newNormal = [cur[1][0] + n[0], cur[1][1] + n[1], cur[1][2] + n[2]]
                        normals = cur[2]
                        isCorner = False
                        for vector in normals:
                            if 80 < angle_between(vector,n) < 100:
                                isCorner = True
                                break
                        normals.append(n)
                        # curNormal = cur[1]
                        # curNormal.append(n)
                        # self.verticesDict.update({curVertex: [1 + cur[0], curNormal]})                        
                        if isCorner:
                            self.verticesDict.update({curVertex: [1 + cur[0], newNormal, normals, True]})
                        else:
                            self.verticesDict.update({curVertex: [1 + cur[0], newNormal, normals, cur[3]]})

                fp.read(2)


            except EOFError:
                break
        normalized_vector =[[],[],[]]
        for key in self.verticesDict.keys():
            values = self.verticesDict.get(key)
            res = values[1]
            #magnitude = math.sqrt(sum(x ** 2 for x in res))
            normalized_vector = res / np.linalg.norm(res)
            
            #print(str(math.sqrt(sum(i**2 for i in normalized_vector))))
            #check for 90°
            self.verticesDict.update({key: [values[0],normalized_vector,values[2], values[3]]})
            #print(str(key.getXYZ()) + str(normalized_vector))
        fp.close()

    # load binary stl file check wikipedia for the binary layout of the file
    # we use the struct library to read in and convert binary data into a format we can use
    def load_binary_stl(self, filename):
        fp = open(filename, 'rb')
        h = fp.read(80)

        l = struct.unpack('I', fp.read(4))[0]
        count = 0
        while True:
            try:
                p = fp.read(12)
                if len(p) == 0: #moved to here, otherwise the last triangle is added tiwce!
                    break
                if len(p) == 12:
                    n = struct.unpack('f', p[0:4])[0], struct.unpack('f', p[4:8])[0], struct.unpack('f', p[8:12])[0]

                p = fp.read(12)
                if len(p) == 12:
                    p1 = struct.unpack('f', p[0:4])[0], struct.unpack('f', p[4:8])[0], struct.unpack('f', p[8:12])[0]

                p = fp.read(12)
                if len(p) == 12:
                    p2 = struct.unpack('f', p[0:4])[0], struct.unpack('f', p[4:8])[0], struct.unpack('f', p[8:12])[0]

                p = fp.read(12)
                if len(p) == 12:
                    p3 = struct.unpack('f', p[0:4])[0], struct.unpack('f', p[4:8])[0], struct.unpack('f', p[8:12])[0]

                new_tri = (n, p1, p2, p3)

                if len(new_tri) == 4:
                    tri = createtriangle(p1, p2, p3, n)
                    self.model.append(tri)
                count += 1
                fp.read(2)

                
            except EOFError:
                break
        fp.close()


class draw_scene:
    def __init__(self, style=1):
        # create a model instance and
        self.model1 = loader()
        self.model1.load_stl(os.path.abspath('') + '/Lower.stl')
        #self.model1.load_stl(os.path.abspath('') + '/Upper.stl')
        #self.model1.load_stl(os.path.abspath('') + '/test_cube.stl')
        self.init_shading()
        self.BETA = 0
        self.ALPHA = 0
        self.GAMMA = 0
        self.SCALE = 1.0
        self.xPos = 0
        self.yPos = 0
        self.zPos = -100
        self.mode = 1

    # solid model with a light / shading
    def init_shading(self):
        glShadeModel(GL_SMOOTH)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLight(GL_LIGHT0, GL_POSITION, (0, 1, 1, 0))
        glMatrixMode(GL_MODELVIEW)

    def resize(self, width, height):
        if height == 0:
            height = 1
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 1.0 * width / height, 0.1, 100.0)
        glTranslatef(0.0, 0.0, -105.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def init(self):
        #glShadeModel(GL_SMOOTH)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        #glShadeModel(GL_SMOOTH)
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

        glEnable(GL_COLOR_MATERIAL)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLight(GL_LIGHT0, GL_POSITION, (0, 1, 1, 0))

        glMatrixMode(GL_MODELVIEW)

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glLoadIdentity()
        glRotatef(self.BETA, 0, 1, 0)  # Rotation along the y axis, with the x_mouse_position
        glRotatef(self.ALPHA, 1, 0, 0)  # Rotation along the x axis, with the y_mouse_position
        glRotatef(self.GAMMA, 0, 0, 1)
        glTranslatef(self.xPos, self.yPos, self.zPos)
        # glTranslatef(self.xPos, self.yPos, self.zPos)

        glScalef(self.SCALE, self.SCALE, self.SCALE)

        self.model1.draw(self.mode)
        glDisable(GL_LIGHT0)
        glDisable(GL_LIGHTING)
        glDisable(GL_COLOR_MATERIAL)

    def rotate(self, alpha, beta):
        self.ALPHA += alpha
        self.BETA += beta
        print("Alpha = " + str(self.ALPHA) + " ; Beta = " + str(self.BETA))

    def scale(self, factor):
        self.SCALE += factor  # or = self.Scale* factor ??
        print("Scale = " + str(self.SCALE))

    def set_trans_rot_values(self, values):
        if not values[0] == "":
            self.xPos = float(values[0])
        else:
            self.xPos = 0
        if not values[1] == "":
            self.yPos = float(values[1])
        else:
            self.yPos = 0
        if not values[2] == "":
            self.zPos = float(values[2])
        else:
            self.zPos = 0
        self.ALPHA = values[3]
        self.BETA = values[4]
        self.GAMMA = values[5]
        if values['Flat']:
            self.mode = 1
        elif values['Gouraud']:
            self.mode = 2
        elif values['Mixed']:
            self.mode = 3
        

    def set_scale(self,val):
        if val == "-":
            self.SCALE -= .1
        else:
            self.SCALE += .1

# main program loop
def main():
    global program
    # initalize pygame
    pygame.init()
    screen = pygame.display.set_mode((1280, 960), OPENGL | DOUBLEBUF)
    # setup the open gl scene
    scene = draw_scene()
    # scene.resize(640, 480)
    scene.resize(1280, 960)

    frames = 0
    ticks = pygame.time.get_ticks()
    program = compileProgram(
        compileShader(vertex_shader, GL_VERTEX_SHADER),
        compileShader(fragment_shader, GL_FRAGMENT_SHADER))

    window = sg.Window("InputWindow", layout)

    while 1:
        print("Test")

        # GUI
        # parameter: x -20 z 65
        guiEvent, values = window.read()
        if guiEvent == sg.WIN_CLOSED:
            break
        elif guiEvent == "OK":
            #print(values)
            scene.set_trans_rot_values(values)
            glClear(GL_COLOR_BUFFER_BIT)
            # draw the scene
            scene.draw()
            pygame.display.flip()
            frames = frames + 1
        elif guiEvent == "   -   ":
            scene.set_scale("-")
        elif guiEvent == "   +   ":
            scene.set_scale("+")



            

        # events = pygame.event.get()
        # for event in events:
        #    if event.type == pygame.MOUSEMOTION:
        #        if pygame.mouse.get_pressed()[0]:
        #            scene.rotate(event.rel[1],event.rel[0])#

        #            print("Rotating")
        #    elif event.type == pygame.MOUSEWHEEL:
        #        scale = event.y / 1 + 1  # +1.something, -1.something
        #        scene.scale(scale)
        #        #glScale(scale, scale, scale)
        #        print("Scaling")

        glClear(GL_COLOR_BUFFER_BIT)
        # draw the scene
        scene.draw()
        pygame.display.flip()
        frames = frames + 1
        # Slider
        # root.mainloop()
    window.close()


if __name__ == '__main__':
    main()
