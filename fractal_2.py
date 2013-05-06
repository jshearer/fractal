#!/usr/bin/python2
from multiprocessing import Pool
import utils
from PIL import Image
import numpy
import argparse
from Vector import Vector

def genChunk(position,size,zoom,iterations=50):
	try:
		zoom = float(zoom)
		
		if type(size) is not int:
			result = numpy.zeros((size[0],size[1]))
			dimensions = (size[0],size[1])
		else:
			result = numpy.zeros((size,size))
			dimensions = (size,size)
		
		for x in range(dimensions[0]):
			for y in range(dimensions[1]):
				t_x = (x+position[0])/float(zoom)
				t_y = (y+position[1])/float(zoom)
				comp = complex(t_x,t_y)
				z = comp
				for i in range(1,iterations+1):
					z = z*z + comp
					if((z.real*z.real + z.imag*z.imag)>4):
						result[x,y] = i
						#break

		return (result,position,size)
	except Exception as e:
		print "ERROR::::::::: "+str(e)

#position,zoom,resolution,scale
#position is obvious
#zoom is the fractal's divisor
#dimensions is the size, as a 2-tuple, of the output image
#scale is a number that allows you to reduce the zoom and dimensions simultaneously 
#in order to render a lower-res version of the same fractal
def gen(position,zoom,dimensions,name,scale=1,squaresize=50,processes=4, scd=False): #scale change dimensions
	scale = 1.0/scale
	procPool = Pool(processes=processes)

	#to correct, not sure why the problem occurs in the first place.
	position.reverse()
	dimensions.reverse()

	zoom = zoom/scale
	if scd:
		dimensions = (int(dimensions[0]/scale),int(dimensions[1]/scale))

	position = Vector(position[0]/scale,position[1]/scale)
	position = position - (Vector(dimensions[0],dimensions[1])/2)
	position = (int(position.x),int(position.y))


	result = numpy.zeros((dimensions[0],dimensions[1]),dtype=numpy.uint8)

	num = 1
	done = [0]
	def callback(data): #should find a better numpy-way to do this...
		pos = (data[1][0]-position[0],data[1][1]-position[1])
		size = data[2]
		data = data[0] #overwrite
		#print "Called back. "+str(pos)
		print str(done[0])+"/"+str(num)+", "+str((done[0]/float(num))*100.0)+"%"
		done[0] += 1
		try:
			for x in range(pos[0],size[0]+pos[0]):
				for y in range(pos[1],size[1]+pos[1]):
					result[x,y] = data[x-pos[0],y-pos[1]]*3
		except Exception as e:
			print "Error:::::: "+str(e)

	for x in xrange(position[0],dimensions[0]+position[0],squaresize):
		for y in xrange(position[1],dimensions[1]+position[1],squaresize):
			procPool.apply_async(genChunk,((x,y),(squaresize,squaresize),zoom),callback=callback)
			num += 1
	num -=1

	procPool.close()
	procPool.join()
	result[dimensions[0]/2,dimensions[1]/2]=255
	Image.fromarray(result,"L").save(name)

#gen((-320,900),1050,(400,400),squaresize=100,scale=0.01,processes=4)

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description="A program to generate a fractal image. \nIn the case of 2-argument flags (such as --position), the arguments should be space-seperated. As in: --position 10 10", epilog='''Example usage:
	./fractal.py -p 0 0 -z 50 -d 200 200 -- This will render a 200x200 image, with the fractal centered, and zoomed to 50.
	./fractal.py -p 100 0  -d 200 200 -z 50 -s 2 -- This will render a 200x200 image, zoomed to 50, and then scaled up 2x. 
	Without the -m argument this effectively means it will zoom in on the center of the image 2x.''', prog="fractal")
parser.add_argument('--position','-p', metavar="pos", nargs=2, type=float, required=True, help="The offset of the rendered fractal. If set to 0 0, the fractal will be centered in the output image.")
parser.add_argument('--dimensions','-d', metavar="dim", nargs=2, type=int, required=True, help="The rendered image dimensions, in pixels. This may be modified by the use of the scale argument.")
parser.add_argument('-zoom','-z', type=float, required=True, help="The zoom of the fractal. This may be modified by the scale argument.")
parser.add_argument('-scale','-s', type=float, default=1, help="The scale multiplier. 1=default, use provided position and zoom. 2=2x zoom and position. If used with the -m argument, the output dimensions will also be scaled up. This can be used to make a thumbnail image before running the full render, to see if your coordinates are correct.\n")
parser.add_argument('-processes','-procs', type=int, default=4, help="The number of processes to use for multi-process rendering. This is usually the number of CPU cores you have.")
parser.add_argument('-m', dest="scd", action="store_true", help="If this flag is set, then the scale argument will also modify the dimensions of the image.")
parser.add_argument('name', help="The name of the output file. This can have any image extension supported by PIL.")
args = vars(parser.parse_args())
gen(args['position'],args['zoom'],args['dimensions'],args['name'], processes=args['processes'], scd=args['scd'], scale=args['scale'])