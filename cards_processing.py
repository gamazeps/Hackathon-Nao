# -*- encoding: UTF-8 -*-

# This is just an example script that shows how images can be accessed
# through ALVideoDevice in python.
# Nothing interesting is done with the images in this example.

from naoqi import ALProxy
import vision_definitions

IP = "nao.local"  # Replace here with your NAOqi's IP address.
PORT = 9559

def parse_hsy(data):
	hsy = []
	bytearray_data = bytearray.fromhex(str(hex(data))[2::])
	hsv.append(bytearray_data[2], bytearray_data[1], bytearray_data[0])


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
camProxy.getImageRemote(nameId)

camProxy.unsubscribe(nameId)

print 'end of gvm_getImageLocal python script'