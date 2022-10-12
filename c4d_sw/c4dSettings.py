################################################################################################
# Settings
################################################################################################
import argparse

simultation 		= False
connection_string 	= '/dev/ttyACM0'
MAV_MODE_AUTO   	= 4
# https://github.com/PX4/PX4-Autopilot/blob/master/Tools/mavlink_px4.py


# Parse connection argument
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--connect", help="connection string")
args = parser.parse_args()

if args.connect:
    connection_string = args.connect

# Yolo Settings
model_dir 	= ""								#yolo model folder
model 		= model_dir + "c4d-aitek-v1.onnx"	#yolo model onnx file
vid_path 	= '/samples/2022-01-28_15m.mp4'		#path of test video

boxOnFrame 		= False	#print bounding boxes on the frames
write_frames	= False	#write output frames to png
write_video 	= False	#write video output
full_video 		= False	#only if camera=False
camera			= True	#enable input from camera
artichokeCount 	= True	#output artichoke Count

cameraID 		= 0
thresh 			= 0.2	#NMS threshold
num_of_frames 	= 100 	#only if full_video=False


simultation = True

# Yolo Settings
model_dir = ""
model = model_dir + "c4d-aitek-v1.onnx"
vid_path = 'C4D-UNISS-UNIMORE/samples/2022-01-28_15m.mp4'
img_path = 'C4D-UNISS-UNIMORE/samples/images/p'

boxOnFrame = False
write_frames = False
write_video = False
full_video = False
camera = True
artichokeCount = True

cameraID = 0
thresh = 0.2
num_of_frames = 100

simultation 		= False
connection_string 	= '/dev/ttyACM0'
MAV_MODE_AUTO   	= 4
