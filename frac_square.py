from PIL import Image
import numpy

im=Image.open("white.jpg")
np_im=numpy.array(im)

for x in range(730):
    for y in range(730):
        np_im[x][y]=[255,255,255]

np_im[729][729] = [0,0,0]
for i in range(6):
    print("iteration"+str(i+1))
    for x in range(730):
        for y in range(730):
            if np_im[x][y][0] == 0:
                np_im[x-(1*(3**i))] [y] = [0,0,0]
                np_im[x] [y-(1*(3**i))]= [0,0,0]
                np_im[x-(2*(3**i))] [y] = [0,0,0]
                np_im[x] [y-(2*(3**i))] = [0,0,0]
                np_im[x-(1*(3**i))] [y-(2*(3**i))] = [0,0,0]
                np_im[x-(2*(3**i))] [y-(1*(3**i))] = [0,0,0]
                np_im[x-(2*(3**i))] [y-(2*(3**i))] = [0,0,0]


new_im= Image.fromarray(np_im)
new_im.save("fractal.jpg")
