import math
import os
import struct
import time
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
layout = [[sg.Text("Controlls")],
          [sg.Text("X-Pos:  "), sg.InputText()],
          [sg.Text("Y-Pos:  "), sg.InputText()],
          [sg.Text("Z-Pos:  "), sg.InputText()],
          [sg.Text("X-Rot:  "), sg.Slider(range=(-180, 180), default_value=0, orientation='horizontal')],
          [sg.Text("Y-Rot:  "), sg.Slider(range=(-180, 180), default_value=0, orientation='horizontal')],
          [sg.Text("Z-Rot:  "), sg.Slider(range=(-180, 180), default_value=0, orientation='horizontal')],
          [sg.Text("Scale:  "), sg.Button(button_text="   -   "), sg.Button(button_text="   +   ")],
          [sg.Button(button_text="OK")]]
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
        return self.x, self.y, self.z
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
    verticesDict = {}
    model = []

    def get_triangles(self):
        if self.model:
            for face in self.model:
                yield face
    def draw(self):
        glUseProgram(program)
        glBegin(GL_TRIANGLES)
        for tri in self.get_triangles():
            curVertex = Vertex(tri.points[0].x, tri.points[0].y, tri.points[0].z)
            cur = self.verticesDict.get(curVertex)
            nb = cur[0]
            if (nb > 8):
                glNormal3f(1, 0.0, 0)
            elif (nb > 6):
                glNormal3f(0, 1.0, 0)
            else:
                glNormal3f(0, 0.0, 1)
            glVertex3f(tri.points[0].x, tri.points[0].y, tri.points[0].z)
            curVertex = Vertex(tri.points[1].x, tri.points[1].y, tri.points[1].z)
            cur = self.verticesDict.get(curVertex)
            nb = cur[0]
            if (nb > 12):
                glNormal3f(1, 0.0, 0)
            elif (nb > 10):
                glNormal3f(0, 1.0, 0)
            else:
                glNormal3f(0, 0.0, 1)
            glVertex3f(tri.points[1].x, tri.points[1].y, tri.points[1].z)
            curVertex = Vertex(tri.points[2].x, tri.points[2].y, tri.points[2].z)
            cur = self.verticesDict.get(curVertex)
            nb = cur[0]
            if (nb > 8):
                glNormal3f(1, 0.0, 0)
            elif (nb > 6):
                glNormal3f(0, 1.0, 0)
            else:
                glNormal3f(0, 0.0, 1)
            glVertex3f(tri.points[2].x, tri.points[2].y, tri.points[2].z)

        glEnd()
        glUseProgram(0)

    # load stl file detects if the file is a text file or binary file
    def load_stl(self, filename):
        # read start of file to determine if its a binay stl file or a ascii stl file
        fp = open(filename, 'rb')
        h = fp.read(80)
        type = h[0:5]
        fp.close()

        if type == 'solid':
            print("reading text file" + str(filename))
        else:
            print("reading binary stl file " + str(filename, ))
            self.load_binary_stl(filename)

    # load binary stl file check wikipedia for the binary layout of the file
    # we use the struct library to read in and convert binary data into a format we can use
    def load_binary_stl(self, filename):
        fp = open(filename, 'rb')
        h = fp.read(80)  # read header

        l = struct.unpack('I', fp.read(4))[0]
        while True:
            try:
                n = [0, 0, 0]
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
                        self.verticesDict.update({curVertex: [1, n]})
                    # self.verticesDict.update({curVertex: [1, [n]]})
                    else:
                        newNormal = [cur[1][0] + n[0], cur[1][1] + n[1], cur[1][2] + n[2]]
                        # curNormal = cur[1]
                        # curNormal.append(n)
                        # self.verticesDict.update({curVertex: [1 + cur[0], curNormal]})
                        self.verticesDict.update({curVertex: [1 + cur[0], newNormal]})

                p = fp.read(12)
                if len(p) == 12:
                    p2 = struct.unpack('f', p[0:4])[0], struct.unpack('f', p[4:8])[0], struct.unpack('f', p[8:12])[0]
                    curVertex = Vertex(p2[0], p2[1], p2[2])
                    cur = self.verticesDict.get(curVertex)
                    if cur == None:
                        self.verticesDict.update({curVertex: [1, n]})
                        # self.verticesDict.update({curVertex: [1, [n]]})
                    else:
                        newNormal = [cur[1][0] + n[0], cur[1][1] + n[1], cur[1][2] + n[2]]
                        # curNormal = cur[1]
                        # curNormal.append(n)
                        # self.verticesDict.update({curVertex: [1 + cur[0], curNormal]})
                        self.verticesDict.update({curVertex: [1 + cur[0], newNormal]})

                p = fp.read(12)
                if len(p) == 12:
                    p3 = struct.unpack('f', p[0:4])[0], struct.unpack('f', p[4:8])[0], struct.unpack('f', p[8:12])[0]
                    curVertex = Vertex(p3[0], p3[1], p3[2])
                    cur = self.verticesDict.get(curVertex)
                    if cur == None:
                        self.verticesDict.update({curVertex: [1, n]})
                        # self.verticesDict.update({curVertex: [1, [n]]})
                    else:
                        newNormal = [cur[1][0] + n[0], cur[1][1] + n[1], cur[1][2] + n[2]]
                        # curNormal = cur[1]
                        # curNormal.append(n)
                        # self.verticesDict.update({curVertex: [1 + cur[0], curNormal]})
                        self.verticesDict.update({curVertex: [1 + cur[0], newNormal]})
                new_tri = (n, p1, p2, p3)
                if len(new_tri) == 4:
                    tri = createtriangle(p1, p2, p3, n)
                    self.model.append(tri)

                fp.read(2)


            except EOFError:
                break
        fp.close()

class draw_scene:
    def __init__(self, style=1):
        # create a model instance and
        self.model1 = loader()
        self.model1.load_stl(os.path.abspath('') + '/Lower.stl')
        # self.model1.load_stl(os.path.abspath('') + '/Upper.stl')
        # self.model1.load_stl(os.path.abspath('') + '/test_cube.stl')
        self.init_shading()
        self.BETA = 0
        self.ALPHA = 0
        self.GAMMA = 0
        self.SCALE = 1.0
        self.xPos = 0
        self.yPos = 0
        self.zPos = -100

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
        # glShadeModel(GL_SMOOTH)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        # glShadeModel(GL_SMOOTH)
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

        self.model1.draw()
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

    def set_scale(self, val):
        if val == "-":
            self.SCALE -= .1
        else:
            self.SCALE += .1

# main program loop
def main():
    start_time = time.time()
    model = loader()
    model.load_stl(os.path.abspath('') + '/Lower.stl')
    print("done in " + str(time.time() - start_time) + "s")
    print("DONE")

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
            print(values)
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
