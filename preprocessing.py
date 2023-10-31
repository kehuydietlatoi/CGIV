import math
import os
import struct

import time


pos_delta = 0.001


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

class loader:
    verticesDict = {}
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
            print( "reading binary stl file " + str(filename, ))
            self.load_binary_stl(filename)


    # load binary stl file check wikipedia for the binary layout of the file
    # we use the struct library to read in and convert binary data into a format we can use
    def load_binary_stl(self, filename):
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

                fp.read(2)


            except EOFError:
                break
        for key in self.verticesDict.keys():
            res = (self.verticesDict.get(key)[1])
            magnitude = math.sqrt(sum(x ** 2 for x in res))
            normalized_vector = [x / magnitude for x in res]
            print(key.getXYZ())
        fp.close()






# main program loop
def main():
    start_time = time.time()
    model = loader()
    model.load_stl(os.path.abspath('') + '/Lower.stl')
    print("done in " + str(time.time() - start_time) + "s")
    print("DONE")


if __name__ == '__main__':
    main()
