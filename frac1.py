#https://github.com/danilobellini/fractal/blob/master/README.rst
#python -m frac1 julia -0.7 +0.27015 j --size=500x300 --depth=1024 --zoom=1 --show
#python -m frac1 mandelbrot --size=500x500 --depth=80 --zoom=0.8 --center=-0.75x0 --show
from __future__ import division, print_function
import pylab, argparse, collections, inspect, functools
from itertools import takewhile
import time
import multiprocessing

Point = collections.namedtuple("Point", ["x", "y"])

def pair_reader(dtype):
  return lambda data: Point(*map(dtype, data.lower().split("x")))


DEFAULT_SIZE = "512x512"
DEFAULT_DEPTH = "256"
DEFAULT_ZOOM = "1"
DEFAULT_CENTER = "0x0"
DEFAULT_COLORMAP = "cubehelix"


def repeater(f):

  @functools.wraps(f)
  def wrapper(n):
    val = n
    while True:
      yield val
      val = f(val)
  return wrapper


def amount(gen, limit=float("inf")):
  size = 0
  for unused in gen:
    size += 1
    if size >= limit:
      break
  return size


def in_circle(radius):
  return lambda z: z.real ** 2 + z.imag ** 2 < radius ** 2

def fractal_eta(z, func, limit, radius=2):
  return amount(takewhile(in_circle(radius), repeater(func)(z)), limit)


def cqp(c):
  return lambda z: z ** 2 + c


def get_model(model, depth, c):
  if model == "julia":
    func = cqp(c)
    return lambda x, y: fractal_eta(x + y * 1j, func, depth)
  if model == "mandelbrot":
    return lambda x, y: fractal_eta(0, cqp(x + y * 1j), depth)
  raise ValueError("Fractal not found")


def generate_fractal(model, c=None, size=pair_reader(int)(DEFAULT_SIZE),
                     depth=int(DEFAULT_DEPTH), zoom=float(DEFAULT_ZOOM),
                     center=pair_reader(float)(DEFAULT_CENTER)):
  num_procs = multiprocessing.cpu_count()
  print('CPU Count:', num_procs)
  start = time.time()

  pool = multiprocessing.Pool(num_procs)
  procs = [pool.apply_async(generate_row,
                            [model, c, size, depth, zoom, center, row])
           for row in range(size[1])]


  img = pylab.array([row_proc.get() for row_proc in procs])

  print('Time taken:', time.time() - start)
  return img


def generate_row(model, c, size, depth, zoom, center, row):
  func = get_model(model, depth, c)
  width, height = size
  cx, cy = center
  side = max(width, height)
  sidem1 = side - 1
  deltax = (side - width) / 2 # Centralize
  deltay = (side - height) / 2
  y = (2 * (height - row + deltay) / sidem1 - 1) / zoom + cy
  return [func((2 * (col + deltax) / sidem1 - 1) / zoom + cx, y)
          for col in range(width)]


def img2output(img, cmap=DEFAULT_COLORMAP, output=None, show=False):
  if output:
    pylab.imsave(output, img, cmap=cmap)
  if show:
    pylab.imshow(img, cmap=cmap)
    pylab.show()


def call_kw(func, kwargs):
  keys = inspect.getargspec(func).args
  kwfiltered = dict((k, v) for k, v in kwargs.items() if k in keys)
  return func(**kwfiltered)


def exec_command(kwargs):
  kwargs["img"] = call_kw(generate_fractal, kwargs)
  call_kw(img2output, kwargs)


def cli_parse_args(args=None, namespace=None):
  parser = argparse.ArgumentParser(
    description=__doc__,
    epilog="by Danilo J. S. Bellini",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
  )
  parser.add_argument("model", choices=["julia", "mandelbrot"],
                      help="Fractal type/model")
  parser.add_argument("c", nargs="*", default=argparse.SUPPRESS,
                      help="Single Julia fractal complex-valued constant "
                           "parameter (needed for julia, shouldn't appear "
                           "for mandelbrot), e.g. -.7102 + .2698j (with the "
                           "spaces), or perhaps with zeros and 'i' like "
                           "-0.6 + 0.4i. If the argument parser gives "
                           "any trouble, just add spaces between the numbers "
                           "and their signals, like '- 0.6 + 0.4 j'")
  parser.add_argument("-s", "--size", default=DEFAULT_SIZE,
                      type=pair_reader(int),
                      help="Size in pixels for the output file")
  parser.add_argument("-d", "--depth", default=DEFAULT_DEPTH,
                      type=int,
                      help="Iteration depth, the step count limit")
  parser.add_argument("-z", "--zoom", default=DEFAULT_ZOOM,
                      type=float,
                      help="Zoom factor, assuming data is shown in the "
                           "[-1/zoom; 1/zoom] range for both dimensions, "
                           "besides the central point displacement")
  parser.add_argument("-c", "--center", default=DEFAULT_CENTER,
                      type=pair_reader(float),
                      help="Central point in the image")
  parser.add_argument("-m", "--cmap", default=DEFAULT_COLORMAP,
                      help="Matplotlib colormap name to be used")
  parser.add_argument("-o", "--output", default=argparse.SUPPRESS,
                      help="Output to a file, with the chosen extension, "
                           "e.g. fractal.png")
  parser.add_argument("--show", default=argparse.SUPPRESS,
                      action="store_true",
                      help="Shows the plot in the default Matplotlib backend")

  # Process arguments
  ns_parsed = parser.parse_args(args=args, namespace=namespace)
  if ns_parsed.model == "julia" and "c" not in ns_parsed:
    parser.error("Missing Julia constant")
  if ns_parsed.model == "mandelbrot" and "c" in ns_parsed:
    parser.error("Mandelbrot has no constant")
  if "output" not in ns_parsed and "show" not in ns_parsed:
    parser.error("Nothing to be done (no output file name nor --show)")
  if "c" in ns_parsed:
    try:
      ns_parsed.c = complex("".join(ns_parsed.c).replace("i", "j"))
    except ValueError as exc:
      parser.error(exc)

  return vars(ns_parsed)

if __name__ == "__main__":
  exec_command(cli_parse_args())