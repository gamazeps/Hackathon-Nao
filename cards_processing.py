# -*- encoding: UTF-8 -*-

# This is just an example script that shows how images can be accessed
# through ALVideoDevice in python.
# Nothing interesting is done with the images in this example.

from naoqi import ALProxy
import vision_definitions
import numpy as np

IP = "nao.local"  # Replace here with your NAOqi's IP address.
PORT = 9559

def parse_hsy(data):
	bytearray_data = bytearray.fromhex(str(hex(data))[2::])
	hsy = [bytearray_data[2], bytearray_data[1], bytearray_data[0]]
	return hsy

def hsv_threshold(source, data, dist=10):
	if(abs(source[0] - data[0]) > dist):
		return false
	else if(abs(source[1] - data[1]) > dist):
		return false
	else if(abs(source[2] - data[2]) > dist):
		return false
	else:
		return true

def get2dArray(data, width=120, length=160):
	matrix = np.zeros([length, width], dtype = int)
	for i in range(width*length):
		matrix[i%width][i/length] = data[i]
	return matrix


def connex_components(logic_matrix, width = 120, length = 160):
	## The case where j=0 isn't treated but i am honestly too lazy to care about it now
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
				if logic_matrix[i-1][j] && logic_matrix[i][j - 1]:
					if components_id[i - 1][j] != components_id[i][j - 1]:
						union(components, components_id, components_id[i - 1][j], components_id[i][j - 1])
					else:
						components[components_id[i - 1][j]].append([i][j])
						components_id[i][j] = components_id[i - 1][j]
					pass
				else if logic_matrix[i - 1][j]:
					components[components_id[i - 1][j]].append([i][j])
					components_id[i][j] = components_id[i - 1][j]
				else if logic_matrix[i][j - 1]:
					components[components_id[i][j - 1]].append([i][j])
					components_id[i][j] = components_id[i][j - 1]
				else:
					components.append([i][j])
					components_id[i][j] = id_count
					id_count = id_count + 1
	return components

def union(components, components_id, id1, id2):
	if len(components[id1])>len(components[id2]):
		for k in components[id2]:
			components_id[k[1]][k[2]] = id1
			components[id2].remove(k)
			components[id1].append(k)
	else:
		for k in components[id1]:
			components_id[k[1]][k[2]] = id2
			components[id1].remove(k)
			components[id2].append(k)



####
# Create proxy on ALVideoDevice

print "Creating ALVideoDevice proxy to ", IP

camProxy = ALProxy("ALVideoDevice", IP, PORT)

####
# Get camera frame

resolution = vision_definitions.kQVGA
colorSpace = vision_definitions.kHSYColorSpace
fps = 15

nameId = camProxy.subscribe("python_GVM", resolution, colorSpace, fps)
print nameId


print 'getting an image in remote'
image = camProxy.getImageRemote(nameId)[6]

camProxy.unsubscribe(nameId)

print 'end of gvm_getImageLocal python script'