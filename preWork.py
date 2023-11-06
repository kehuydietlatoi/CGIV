import os
import struct
from typing import Tuple, Any

from typing import Tuple, Any

import keyboard
import math
import time
import json

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLU import *
import pygame
from pygame.locals import *

import PySimpleGUI as sg

pos_delta = 0.000001

class cornerNormal:
    def __init__(self, pos, normal) -> None:
        self.x = pos.x
        self.y = pos.y
        self.z = pos.z
        self.adjacent = 1
        self.normal = normal

    def is_point_in_range(self, pos):
        if pos.x < (self.x + pos_delta) and pos.x > (self.x - pos_delta):
            if pos.y < (self.y + pos_delta) and pos.y > (self.y - pos_delta):
                if pos.z < (self.z + pos_delta) and pos.z > (self.z - pos_delta):
                    #print(str(pos.x) + "," + str(pos.y) + "," + str(pos.z) + " is in Range of " + str(self.x) + "," + str(self.y) + "," + str(self.z))
                    return True
        #print(str(pos.x) + "," + str(pos.y) + "," + str(pos.z) + " is NOT in Range of " + str(self.x) + "," + str(self.y) + "," + str(self.z))
        return False

    def add_adjacent(self, normal):
        self.adjacent += 1
        self.normal.x += normal.x #TODO am ende noch alles durch adjacent normalisieren!!!!
        self.normal.y += normal.y #TODO am ende noch alles durch adjacent normalisieren!!!!
        self.normal.z += normal.z #TODO am ende noch alles durch adjacent normalisieren!!!!


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

    cornerNormals = []
    # return the faces of the triangles
    def get_triangles(self):
        if self.model:
            for face in self.model:
                yield face
        
    def list_triangles(self):
        list = []
        if self.model:
            for face in self.model:
                list.append(face)
        return list
    
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
        tri_counter = 0 #counter of all triangles in model
        start_time = time.time()
        triangles = self.list_triangles()    #all triangles for inner for loop
        for tri in self.get_triangles():    #for all triangles in model
            if tri.points[0].x != triangles[0].points[0].x and tri.points[1].x != triangles[0].points[1].x and tri.points[2].x != triangles[0].points[2].x:
                if tri.points[0].y != triangles[0].points[0].y and tri.points[1].y != triangles[0].points[0].y and tri.points[2].y != triangles[0].points[2].y:
                    if tri.points[0].z != triangles[0].points[0].z and tri.points[1].z != triangles[0].points[0].z and tri.points[2].z != triangles[0].points[2].z:
                        print("ERROR !!!!!!!!!!!!!!!!!!!")  #checking if pop(0) is legitimate
            triangles.pop(0)    #pop first triangle, because that is the triangle beeing used as 'tri'
            tri_counter += 1       #test to check if all triangles are checked
            if tri_counter % 100 == 0:
                end_time = time.time() - start_time
                print(str(tri_counter) + " Faces checked in " + str(end_time) + "s")
                #print(str(tri_counter) + " Faces checked")
            #print(str(tri_counter) + ": [" + str(tri.points[0].x) + ", " + str(tri.points[0].y) + ", " + str(tri.points[0].z) + 
            #      "],[" + str(tri.points[1].x) + ", " + str(tri.points[1].y) + ", " + str(tri.points[1].z) + 
            #      "],[" + str(tri.points[2].x) + ", " + str(tri.points[2].y) + ", " + str(tri.points[2].z) + "]")
            for pos in tri.points:      #for all 3 points of triangle('tri')
                counter = 0
                already_saved = False
                if len(self.cornerNormals) < 3:     #if no Points have been saved (first triangle):
                    newNormal = cornerNormal(pos, tri.normal)
                    self.cornerNormals.append(newNormal)    #save them
                else:   #cornerNormals is not empty
                    for normal in reversed(self.cornerNormals):   #chek all saved Normals #check reversed!
                        if normal.is_point_in_range(pos):   #if point has been saved before
                            normal.add_adjacent(tri.normal)     #add normal to saved
                            already_saved = True
                            break
                    #show number of adjacent triangles to point
                    #print(str(counter) + " : " + str(pos.x) + "," + str(pos.y) + ","+ str(pos.z))                        
                    if not already_saved:               # if it hasn't been saved
                        newNormal = cornerNormal(pos, tri.normal)
                        self.cornerNormals.append(newNormal)    #save them
                        if len(self.cornerNormals) % 100 == 0:
                            end_time = time.time() - start_time
                            print(str(len(self.cornerNormals)) + " Points found in " + str(end_time) + "s")
                    else:
                        already_saved = False

        end_time = time.time() - start_time
        print(str(tri_counter) + " Faces and ")
        print(str(len(self.cornerNormals)) + " Points found in " + str(end_time/3600 )+ " h")

    def add_corner_normals(self, triangle):
        if len(self.cornerNormals) == 0:    #First triangle doesn't need a check
            for point in triangle.points:
                self.cornerNormals.append(cornerNormal(point,triangle.normal))
        else:
            for point in triangle.points:   #For all three corners in triangle
                corner_found = False
                for normal in self.cornerNormals:       #check all corners in cornerNormals
                    if normal.is_point_in_range(point):     #if its corners are saved in CornerNormals
                        normal.add_adjacent(triangle.normal)    # add the triangles normal to the CornerNormal
                        corner_found = True
                        break                                   # don't check this corner of the triangle anymore
                if not corner_found:
                    self.cornerNormals.append(cornerNormal(point, triangle.normal))    #else add the corner to the CornerNormals


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
                        tri = createtriangle(triangle[0], triangle[1], triangle[2], normal)
                        self.model.append(tri)
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

    
    # load stl file detects if the file is a text file or binary file
    def load_and_count_stl(self, filename):
        # read start of file to determine if its a binay stl file or a ascii stl file
        fp = open(filename, 'rb')
        h = fp.read(80)
        type = h[0:5]
        fp.close()

        if type == 'solid':
            print
            "reading text file" + str(filename)
            self.load_and_count_text_stl(filename)
        else:
            print
            "reading binary stl file " + str(filename, )
            self.load_and_count_binary_stl(filename)

    # read text stl match keywords to grab the points to build the model
    def load_and_count_text_stl(self, filename):
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
                        tri = createtriangle(triangle[0], triangle[1], triangle[2], normal)
                        self.model.append(tri)
                        self.add_corner_normals(tri)
                        if len(self.cornerNormals) % 100 == 0:
                            print(str(len(self.cornerNormals)) + " Corners found")
                        #hier Punkte speichern & Anliegende Dreiecke zählen!
        fp.close()

    def load_and_count_binary_stl(self, filename):
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
                    self.add_corner_normals(tri)
                    if len(self.cornerNormals) % 100 > 3:
                        print(str(len(self.cornerNormals)) + " Corners found")
                count += 1
                fp.read(2)

                
            except EOFError:
                break
        fp.close()
    
def saveCornerNormals(mod):
    with open('cornerData.json', 'w', encoding='utf-8') as file:
        json.dump(mod.cornerNormals, file, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

def readCornerNormals():
    with open('cornerData.json', 'r', encoding='utf-8') as file:
        return json.load(file)
    

# main program loop
def main():
    start_time = time.time()
    model = loader()
    model.load_stl(os.path.abspath('') + '/Lower.stl')
    #model.load_stl(os.path.abspath('') + '/Upper.stl')
    #model.load_stl(os.path.abspath('') + '/test_cube.stl')
    model.count_adjacent()
    #model.load_and_count_stl(os.path.abspath('') + '/test_cube.stl')
    saveCornerNormals(model)
    print("done in " + str(time.time() - start_time) + "s")
    savedNormals = readCornerNormals()
    print("DONE")


if __name__ == '__main__':
    main()
