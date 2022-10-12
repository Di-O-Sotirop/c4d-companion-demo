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

from c4d_sw.c4dCnnPkg import ResizeAndPad, FilterBoxesNMS, inputPreprocess, outputPreprocess, printBBoxes, \
    WriteC4DVideo, PrintBBoxOnFrame
from c4d_sw.pymavlinkPkg import initialize_mavlink, PX4setMode

# import subprocess
import subprocess
import c4d_sw.c4dSettings
from c4d_sw.aesHelperPkg import formatNumeric, formatPlantCnt

################################################################################################
# Settings
################################################################################################


################################################################################################
# Init
################################################################################################
vehicle = initialize_mavlink(connection_string='/dev/ttyACM0')

## Listener ##
home_position_set = False


# Create a message listener for home position fix
@vehicle.on_message('HOME_POSITION')
def listener(self, name, home_position):
    global home_position_set
    home_position_set = True


## CNN Init ##
img_array = []
inputSize = (640, 640)

# Runtime Configuration
opts = ort.SessionOptions()
opts.intra_op_num_threads = 4
opts.inter_op_num_threads = 1
session = ort.InferenceSession(c4d_sw.model, sess_options=opts)
input_name = session.get_inputs()[0].name
output_0_name = session.get_outputs()[0].name

# Import and Split Video
if c4d_sw.camera == False:
    cap = cv2.VideoCapture(c4d_sw.vid_path)
else:
    cap = cv2.VideoCapture(c4d_sw.cameraID)
frm_count = 0

# Read cap once to get constants
if cap.isOpened():
    ret, frame = cap.read()
    if ret == False:
        print('No Ret')

    ################################################################################################
    # Start mission
    ################################################################################################

    # wait for a home position lock
    while not home_position_set:
        print("Waiting for home position...")
        time.sleep(1)

    # Display basic vehicle state
    # print( " Type: %s" % vehicle._vehicle_type)
    # print( " Armed: %s" % vehicle.armed)
    # print( " System status: %s" % vehicle.system_status.state)
    print(" GPS: %s" % vehicle.gps_0)
    print(" Alt: %s" % vehicle.location.global_relative_frame.alt)
    print(" Lon: %s" % vehicle.location.global_relative_frame.lon)
    print(" Lat: %s" % vehicle.location.global_relative_frame.lat)
    # Change to AUTO mode
    PX4setMode(c4d_sw.MAV_MODE_AUTO)
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
    outMSG = outMSG + "0000000000000000"
    # Capture Position
    latitude = vehicle.location.global_relative_frame.lat
    longitude = vehicle.location.global_relative_frame.lon
    altitude = vehicle.location.global_relative_frame.alt

    outMSG = outMSG + formatNumeric(latitude, 2, 10) + formatNumeric(longitude, 2, 10) + formatNumeric(altitude, 2, 10)
    # Capture Speed
    outMSG = outMSG + formatNumeric(str(vehicle.velocity.vx), 2, 7) + formatNumeric(str(vehicle.velocity.vy), 2,
                                                                                    7) + formatNumeric(
        str(vehicle.velocity.vz), 2, 7)

    #  LonLatAlt = []
    #  LonLatAlt.append(vehicle.location.global_relative_frame.lon)
    #  LonLatAlt.append(vehicle.location.global_relative_frame.lat)
    #  LonLatAlt.append(vehicle.location.global_relative_frame.alt)

    ret, frame = cap.read()
    if ret == False:
        print('escaping')
        break

    # Image Pre-Processing
    data = inputPreprocess(frame)
    ###########################INFERENCE_WITH_ONNXRUNTIME###################################
    [result_0] = session.run([output_0_name], {input_name: data})
    #############################PREPROCESS OUTPUT############################################
    mOutputRow = session.get_outputs()[0].shape[1]  # 25200
    mOutputColumn = session.get_outputs()[0].shape[2]  # 6

    boxes = np.array(outputPreprocess(result_0, mOutputRow, mOutputColumn, frame))

    # Sort Boxes for NMS
    if boxes.shape[0] > 1:
        boxes_sorted = boxes[np.argsort(-1 * boxes[:, 4])]
    else:
        boxes_sorted = boxes
    # apply NMS
    rem_bbox = FilterBoxesNMS(boxes, c4d_sw.thresh)
    rem_bbox = np.array(rem_bbox)

    # Add artichoke count to out Msg
    outMSG = outMSG + formatPlantCnt(rem_bbox.shape[0], 3)

    # Print Count / BBoxes on Frame
    if c4d_sw.artichokeCount == True:
        print(rem_bbox.shape[0])
    if c4d_sw.boxOnFrame == True:
        # Print Boxes on frame and write frames
        (img_array, frm_count) = PrintBBoxOnFrame(frame, rem_bbox, frm_count, img_array)
        if not c4d_sw.full_video:
            if frm_count > num_of_frames:
                break
        else:
            num_of_frames = frm_count

    ## Perform AES Encryption, generate files ##
    # subprocess.call("encryptDemos.sh", outMSG)
    # subprocess.call("encryptDemos.sh", str(LonLatAlt[0])+ ' ' + str(LonLatAlt[1]), str(LonLatAlt[2])+ ' ' + str(rem_bbox.shape[0]))

cap.release()
cv2.destroyAllWindows()

##  Write Video avi ##
if c4d_sw.write_video == True:
    WriteC4DVideo(img_array)

# Close vehicle object before exiting script
vehicle.close()
time.sleep(1)
