from PIL import Image, ImageDraw
HEIGHT = 400
WIDTH = 600
MAX_ITER = 80
# Plot window
RE_START = -2
RE_END = 1
IM_START = -1
IM_END = 1


im = Image.new('HSV', (WIDTH, HEIGHT), (0, 0, 0))
draw = ImageDraw.Draw(im)


def mandelbrot(c):
    z = 0
    n = 0
    while abs(z) <= 2 and n < MAX_ITER:
        z = z*z + c
        n += 1
    return n


for x in range(0, WIDTH):
    for y in range(0, HEIGHT):
        c = complex(RE_START + (x / WIDTH) * (RE_END - RE_START),
                    IM_START + (y / HEIGHT) * (IM_END - IM_START))
        m = mandelbrot(c)
        hue = int(255 * m / MAX_ITER)
        saturation = 255
        value = 255 if m < MAX_ITER else 0
        draw.point([x, y], (hue, saturation, value))

#im.convert('RGB').save('output.png', 'PNG')
im.show()
