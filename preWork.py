import os
import struct
from typing import Tuple, Any

from typing import Tuple, Any

import keyboard
import math
import time

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLU import *
import pygame
from pygame.locals import *

import PySimpleGUI as sg

pos_delta = 0.1

#check if pos1 is in "pos_delta" range of pos 2
def is_in_range(pos1, pos2):
    if pos1.x < (pos2.x + pos_delta) and pos1.x > (pos2.x - pos_delta):
        if pos1.y < (pos2.y + pos_delta) and pos1.y > (pos2.y - pos_delta):
            if pos1.z < (pos2.z + pos_delta) and pos1.z > (pos2.z - pos_delta):
                return True
    return False

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

    # return the faces of the triangles
    def get_triangles(self):
        if self.model:
            for face in self.model:
                yield face

    # draw the models faces
    def draw(self):
        glUseProgram(program)
        glBegin(GL_TRIANGLES)
        for tri in self.get_triangles():
            glNormal3f(tri.normal.x, tri.normal.y, tri.normal.z)
            glVertex3f(tri.points[0].x, tri.points[0].y, tri.points[0].z)
            glVertex3f(tri.points[1].x, tri.points[1].y, tri.points[1].z)
            glVertex3f(tri.points[2].x, tri.points[2].y, tri.points[2].z)
            
        glEnd()
        glUseProgram(0)

    #count all adjacent triangles to all points of all triangles
    def count_adjacent(self):
        positions = []  #list of registered positions
        tri_counter = 0 #counter of all triangles in model
        #start_time = time.time()
        for tri in self.get_triangles():    #for all triangles in model
            tri_counter += 1       #test to check if all triangles are checked
            if tri_counter % 100 == 0:
                #end_time = time.time() - start_time
                #print(str(tri_counter) + " Faces checked in " + str(end_time) + "s")
                print(str(tri_counter) + " Faces checked")
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
                    #show number of adjacent triangles to point
                    #print(str(counter) + " : " + str(pos.x) + "," + str(pos.y) + ","+ str(pos.z))
                for savedPosition in positions:     #chek if point has been saved before
                    if is_in_range(pos, savedPosition):
                        already_saved = True
                if not already_saved:               # if it hasn't been saved, count adjacent and save
                    positions.append(pos)
                    if len(positions) % 100 == 0:
                        print(str(len(positions)) + " Points found")
                    for triangle in self.get_triangles():
                        for point in triangle.points:
                            if is_in_range(point, pos):
                                counter += 1
                    #show number of adjacent triangles to point
                    #print(str(counter) + " : " + str(pos.x) + "," + str(pos.y) + ","+ str(pos.z))
                else:
                    already_saved = False
        print(str(tri_counter) + " Faces")
        print(str(len(positions)) + " Points")

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

# main program loop
def main():
    model = loader()
    model.load_stl(os.path.abspath('') + '/Lower.stl')
    #model.load_stl(os.path.abspath('') + '/Upper.stl')
    #model.load_stl(os.path.abspath('') + '/test_cube.stl')
    model.count_adjacent()


if __name__ == '__main__':
    main()
