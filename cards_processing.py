# -*- encoding: UTF-8 -*-

# This is just an example script that shows how images can be accessed
# through ALVideoDevice in python.
# Nothing interesting is done with the images in this example.

from naoqi import ALProxy
import vision_definitions
import numpy as np

IP = "nao.local"  # Replace here with your NAOqi's IP address.
PORT = 9559

# Gives out a list containing the hsv coordinates of a pixel from the raw input of the camera
def parse_hsy(data):
	bytearray_data = bytearray.fromhex(str(hex(data))[2::])
	hsy = [bytearray_data[2], bytearray_data[1], bytearray_data[0]]
	return hsy

# Applies a basic threshold to an hsv pixel
def hsy_threshold(source, data, dist = 10):
	if (abs(source[0] - data[0]) > dist):
		return false
	elif (abs(source[1] - data[1]) > dist):
		return false
	elif (abs(source[2] - data[2]) > dist):
		return false
	else:
		return true

def get2D_thresholded(array_source, data, width = 120, length = 160, dist = 10):
	bit_array = np.zeros([length, width], dtype = bool)
	for i in range(length):
		for j in range(width):
			bit_array[i][j] = hsy_threshold(array_source[i][j], data, dist)
	return bit_array

# Returns a 2D array from a 1D array, given the width 
def get2d_array(data, width=120, length=160):
	if len(data) == width * length:
		matrix = np.zeros([length, width], dtype = int)
		for i in range(width*length):
			matrix[i%width][i/length] = data[i]
		return matrix
	else:
		print "The size of the 2D array does not match the size of the 1D array"

# Finds the connex components in a binary 2D array, the data structure employed is a lazy union-find one,
# is executed in a O(n*ln(n)) complexity in the average and worst case (where n is the numpber of pixels) 
# and in best case scenario in O(n) 
def connex_components(logic_matrix, size = 7, width = 120, length = 160):
	components = []
	components_id = np.zeros([length, width], dtype = int)
	id_count = 1
	if logic_matrix[0][0]:
		components.append([[0,0]])
		components_id[0][0] = 1
		id_count = id_count + 1
	for i in range(1,length):
		if logic_matrix[i][0]:
			if logic_matrix[i - 1][0]:
				components[components_id[i - 1][0]].append([i][0])
				components_id[i][0] = components_id[i - 1][0]
			else:
				components.append([i,0])
				components_id[i][0] = id_count
				id_count = id_count + 1
		for j in range(1, width):
			if logic_matrix[i][j]:
				if logic_matrix[i-1][j] and logic_matrix[i][j - 1]:
					if components_id[i - 1][j] != components_id[i][j - 1]:
						union(components, components_id, components_id[i - 1][j], components_id[i][j - 1])
					else:
						components[components_id[i - 1][j]].append([i][j])
						components_id[i][j] = components_id[i - 1][j]
					pass
				elif logic_matrix[i - 1][j]:
					components[components_id[i - 1][j]].append([i][j])
					components_id[i][j] = components_id[i - 1][j]
				elif logic_matrix[i][j - 1]:
					components[components_id[i][j - 1]].append([i][j])
					components_id[i][j] = components_id[i][j - 1]
				else:
					components.append([i][j])
					components_id[i][j] = id_count
					id_count = id_count + 1
	# Here we remove all the empty components and the one too small to be cards
	lists_to_remove = []
	for component in components:
		if len(component) < size:
			lists_to_remove.append(component)
	for component in range(lists_to_remove):
		components.remove(component)

	return components

# Realises the union action in the union-find datastructure
def union(components, components_id, id1, id2):
	if len(components[id1]) > len(components[id2]):
		for k in components[id2]:
			components_id[k[0]][k[1]] = id1
			components[id1].append(k)
		components[id2] = []
	else:
		for k in components[id1]:
			components_id[k[0]][k[1]] = id2
			components[id2].append(k)
		components[id1] = []

# Returns the center of a group of pixels
def get_centers(components):
	centers = []
	for component in components:
		i = 0
		j = 0
		for pixel in component:
			i = i + pixel[0]
			j = j + pixel[1]
		centers.append([i/len(component), j/len(component)])
	return centers

def get_cards_pos(blue_cards_components, red_cards_components, yellow_cards_components):
	blue_centers = get_centers(blue_cards_components)
	red_centers = get_centers(red_cards_components)
	yellow_centers = get_centers(yellow_cards_components)
	color_and_pos = []
	for card in blue_centers:
		color_and_pos.append([card[0], 'b'])
	for card in red_centers:
		color_and_pos.append([card[0], 'r'])
	for card in yellow_centers:
		color_and_pos.append([card[0], 'y'])
	color_and_pos.sort()
	cards = []
	for card in color_and_pos:
		cards.append(card[1])
	return cards

def process_image(raw_data):
	BLUE = [170, 85, 15]
	RED = [0, 100, 39]
	YELLOW = [28, 98, 45]
	hsy_data = []
	for pixel in raw_data:
		hsy_data.append(parse_hsy(pixel))
	hsy_array = get2d_array(hsy_data)
	blue_array = get2D_thresholded(hsy_array, BLUE) 
	blue_cards_components = connex_components(blue_array)
	red_array = get2D_thresholded(hsy_array, RED) 
	red_cards_components = connex_components(red_array)
	yellow_array = get2D_thresholded(hsy_array, YELLOW) 
	yellow_cards_components = connex_components(yellow_array)
	return get_cards_pos(blue_cards_components, red_cards_components, yellow_cards_components)


####
# Create proxy on ALVideoDevice

print "Creating ALVideoDevice proxy to ", IP

# = ALProxy("ALVideoDevice", IP, PORT)

####
# Get camera frame

resolution = vision_definitions.kQVGA
colorSpace = vision_definitions.kHSYColorSpace
fps = 15

nameId = camProxy.subscribe("python_GVM", resolution, colorSpace, fps)
#print nameId


print 'getting an image in remote'
image = camProxy.getImageRemote(nameId)[6]
cards = process_image(image)

print cards

camProxy.unsubscribe(nameId)

print 'end of gvm_getImageLocal python script'