from PIL import Image
import numpy as np
from circles import Circle, Circles
import glob
from time import time

class ShapeFill(Circles):
	"""A class for filling a shape with circles."""

	def __init__(self, img_name, reverse=False, *args, **kwargs):
		"""Initialize the class with an image specified by filename.

		The image should be black on a white background.

		The maximum and minimum circle sizes are given by rho_min and rho_max
		which are proportions of the minimum image dimension.
		The maximum number of circles to pack is given by n
		colours is a list of SVG fill colour specifiers (a default palette is
		used if this argument is not provided).

		"""

		self.img_name = img_name
		self.reverse=reverse
		# Read the image and set the image dimensions; hand off to the
		# superclass for other initialization.
		self.read_image(img_name)
		dim = min(self.width, self.height)
		super().__init__(self.width, self.height, dim, *args, **kwargs)

	def read_image(self, img_name):
		"""Read the image into a NumPy array and invert it."""

		img = Image.open(img_name).convert('1')
		self.width, self.height = img.width, img.height
		self.img = 255 - np.array(img.getdata()).reshape(img.height, img.width)
		self.img = self.img.T

	def _circle_fits(self, icx, icy, r):
		"""If I fits, I sits."""

		if icx-r < 0 or icy-r < 0:
			return False
		if icx+r >= self.width or icy+r >= self.height:
			return False

		if not all((self.img[icx-r,icy], self.img[icx+r,icy],
				self.img[icx,icy-r], self.img[icx,icy+r])):
			return False
		return True

	def apply_circle_mask(self, icx, icy, r):
		"""Zero all elements of self.img in circle at (icx, icy), radius r."""

		x, y = np.ogrid[0:self.width, 0:self.height]
		r2 = (r+1)**2
		mask = (x-icx)**2 + (y-icy)**2 <= r2
		self.img[mask] = 0

	def _place_circle(self, r, c_idx=None):
		"""Attempt to place a circle of radius r within the image figure.
 
		c_idx is a list of indexes into the self.colours list, from which
		the circle's colour will be chosen. If None, use all colours.

		"""

		if not c_idx:
			c_idx = range(len(self.colours))

		# Get the coordinates of all non-zero image pixels
		img_coords = np.nonzero(self.img)
		if not img_coords:
			return False

		# The guard number: if we don't place a circle within this number
		# of trials, we give up.
		guard = self.guard
		# For this method, r must be an integer. Ensure that it's at least 1.
		r = max(1, int(r))
		while guard:
			# Pick a random candidate pixel...
			i = np.random.randint(len(img_coords[0]))
			icx, icy = img_coords[0][i], img_coords[1][i]
			# ... and see if the circle fits there
			if self._circle_fits(icx, icy, r):
				self.apply_circle_mask(icx, icy, r)
				circle = Circle(icx, icy, r, icolour=np.random.choice(c_idx))
				self.circles.append(circle)
				return True
			guard -= 1
		print('guard reached.')
		return False

if __name__ == '__main__':
	black = ['#000000']
	white = ['#FFFFFF']

	number=0
	all_images=glob.glob('Bad Apple frames/*')
	#6572 frames
	debut=time()
	test_frames=["1","300","500","1246","4798","6238","418","2171"]
	test_frames=["6238"]
	for testname in test_frames:
	#for filename in all_images:
		filename="Bad Apple frames/"+testname+".png"
		print(filename)
		number+=1
		shape = ShapeFill(filename, rho_max=0.01, colours=black)
		#max of 691200 black pixels
		filling=np.count_nonzero(shape.img == 255)
		filling_percentage=round(100*filling/691200)
		#if more than half is black we reverse the color
		if filling_percentage>50 and filling_percentage!=100:
			shape.img = 255 - shape.img
			shape.colours=white
			shape.reverse=True
			filling_percentage=100-filling_percentage
		print("Filling of "+str(filling_percentage)+"%")
		#modify the number of circles to correspond to the filling
		shape.n=int(filling_percentage*3000/42)
		shape.guard = 1000
		shape.make_circles(c_idx=range(1))
		#shape.make_svg('svg/'+filename[filename.find('\\')+1:filename.find('.')]+'.svg')
		shape.make_svg('svg/'+testname+'.svg')
		print("Temps moyen : {0}s par frame. Durée estimée : {1}h.".format(round((time()-debut)/number),round(len(all_images)*(time()-debut)/(number*3600))))
