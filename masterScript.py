################################################################################################
# @File DroneKitPX4.py
# Example usage of DroneKit with PX4
#
# @author Sander Smeets <sander@droneslab.com>
#
# Code partly based on DroneKit (c) Copyright 2015-2016, 3D Robotics.
################################################################################################

# Import DroneKit-Python

import time, cv2, datetime

import numpy as np
import onnxruntime as ort

from c4d_sw import c4dCnnPkg as c4dcnn
from c4d_sw import pymavlinkPkg as mavl
from c4d_sw import c4dSettings as sett
from c4d_sw import aesHelperPkg as aesh

# import subprocess
import subprocess

################################################################################################
# Init
################################################################################################
args = sett.manipulate_args()
print(args.connectPX4)
vehicle = mavl.initialize_mavlink(connection_string='/dev/ttyACM0')
v = args.verbose 

## Listener ##
home_position_set = False

# Create a message listener for home position fix
@vehicle.on_message('HOME_POSITION')
def listener(self, name, home_position):
    global home_position_set
    home_position_set = True

sett.printV("Listener Created..",v)

## CNN Init ##
img_array = []
inputSize = (640, 640)

# Runtime Configuration
opts = ort.SessionOptions()
opts.intra_op_num_threads = 4
opts.inter_op_num_threads = 1
session = ort.InferenceSession(args.model, sess_options=opts)
input_name = session.get_inputs()[0].name
output_0_name = session.get_outputs()[0].name
sett.printV("ONNX runtime session initialized...",v)
sett.printV(">intra threads = " + str(opts.intra_op_num_threads),v)
sett.printV(">inter threads = " + str(opts.inter_op_num_threads),v)


# Import and Split Video
if args.nocamera:
    cap = cv2.VideoCapture(args.vid_path)
    sett.printV("Video Input from " + str(args.vid_path),v)
else:
    cap = cv2.VideoCapture(args.cameraID)
    sett.printV("Camera Input from cam" + str(args.cameraID),v)
frm_count = 0

# Read cap once to get constants
if not cap.isOpened():
    print("cap is not open. Program exiting...")
else:
    ret, frame = cap.read()
    if not ret:
        print('No Ret')
    
    ################################################################################################
    # Start mission
    ################################################################################################
    home_position_set = args.simulation
    # wait for a home position lock
    while not home_position_set:
        sett.printV("Waiting for home position...",v)
        time.sleep(1)

    # Display basic vehicle state
    # print( " Type: %s" % vehicle._vehicle_type)
    # print( " Armed: %s" % vehicle.armed)
    # print( " System status: %s" % vehicle.system_status.state)
    sett.printV(" GPS: %s" % vehicle.gps_0,v)
    sett.printV(" Alt: %s" % vehicle.location.global_relative_frame.alt,v)
    sett.printV(" Lon: %s" % vehicle.location.global_relative_frame.lon,v)
    sett.printV(" Lat: %s" % vehicle.location.global_relative_frame.lat,v)
    # Change to AUTO mode
    mavl.PX4setMode(args.MAV_MODE_AUTO, vehicle)
    time.sleep(1)
    # get global position
    home = vehicle.location.global_relative_frame

################################################################################################
# MAIN LOOP
################################################################################################
while (cap.isOpened()):

    # Capture Timestamp
    curDT = datetime.datetime.now()
    outMSG = curDT.strftime("%Y%m%d%H%M%S")
    # Add IMEI
    outMSG = outMSG + ',' + "0000000000000000"
    # Capture Position
    latitude = vehicle.location.global_relative_frame.lat
    longitude = vehicle.location.global_relative_frame.lon
    altitude = vehicle.location.global_relative_frame.alt
    vx = vehicle.velocity[0]
    vy = vehicle.velocity[1]
    vz = vehicle.velocity[2]
    sett.printV("Time and Position captured...",v)
    if args.simulation:
        latitude = 0
        longitude = 0
        altitude = 0
        vx = 0
        vy = 0
        vz = 0
    outMSG = outMSG + ',' + aesh.formatNumeric(latitude, 2, 10) \
             + ',' + aesh.formatNumeric(longitude, 2, 10) \
             + ',' + aesh.formatNumeric(altitude, 2, 10)
    # Capture Speed
    outMSG = outMSG + ',' + aesh.formatNumeric(vx, 2, 7) \
             + ',' + aesh.formatNumeric(vy, 2, 7) \
             + ',' + aesh.formatNumeric(vz, 2, 7) + ','
    sett.printV("plaintext message formatted...",v)
    ret, frame = cap.read()
    if not ret:
        print('escaping')
        break
    data = c4dcnn.inputPreprocess(frame, (640, 640))
    ###########################INFERENCE_WITH_ONNXRUNTIME###################################
    [result_0] = session.run([output_0_name], {input_name: data})
    #############################PREPROCESS OUTPUT############################################
    mOutputRow = session.get_outputs()[0].shape[1]  # 25200
    mOutputColumn = session.get_outputs()[0].shape[2]  # 6
    sett.printV("ONNX run executed...",v)
    boxes = np.array(c4dcnn.outputPreprocess(result_0, mOutputRow, mOutputColumn, frame))
    sett.printV("Preprocessing of output done...",v)
    # Sort Boxes for NMS
    if boxes.shape[0] > 1:
        boxes_sorted = boxes[np.argsort(-1 * boxes[:, 4])]
    else:
        boxes_sorted = boxes
    # apply NMS
    rem_bbox = c4dcnn.FilterBoxesNMS(boxes, args.thresh)
    rem_bbox = np.array(rem_bbox)
    sett.printV("Postprocessing of output done...",v)
    # Add artichoke count to out Msg
    outMSG = outMSG + aesh.formatPlantCnt(rem_bbox.shape[0], 3)

    # Print Count / BBoxes on Frame
    if args.artichokeCount:
        print(rem_bbox.shape[0])
    if args.boxOnFrame:
        # Print Boxes on frame and write frames
        (img_array, frm_count) = c4dcnn.PrintBBoxOnFrame(frame, rem_bbox, frm_count, img_array)
        if not args.full_video:
            if frm_count > num_of_frames:
                break
        else:
            num_of_frames = frm_count

    if args.print_msg:
        print(outMSG)
    ## Perform AES Encryption, generate files ##
    subprocess.call(sett.set_encrypt_script, outMSG)

cap.release()
cv2.destroyAllWindows()

##  Write Video avi ##
if args.write_video:
    c4dcnn.WriteC4DVideo(img_array)

# Close vehicle object before exiting script
vehicle.close()
time.sleep(1)
