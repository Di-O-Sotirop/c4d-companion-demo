#############################################################################
# Copyright 2022 - University of Modena and Reggio Emilia                   #
#                                                                           #
# Author:                                                                   #
#    Dionysios Sotiropoulos, <dsotirop at unimore.it>                       #
#    Alessandro Capotondi, <a.capotondi at unimore.it>                      #
#                                                                           #
# Licensed under the Apache License, Version 2.0 (the "License");           #
# you may not use this file except in compliance with the License.          #
# You may obtain a copy of the License at                                   #
#                                                                           #
#    http://www.apache.org/licenses/LICENSE-2.0                             #
#                                                                           #
# Unless required by applicable law or agreed to in writing, software       #
# distributed under the License is distributed on an "AS IS" BASIS,         #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
# See the License for the specific language governing permissions and       #
# limitations under the License.                                            #
#                                                                           #
# C4D Companion Computer Demo                                               #
#                                                                           #
# This software is developed under the ECSEL project Comp4drones(No 826610) #
#                                                                           #
#############################################################################

import serial
import time, cv2, datetime
import sys

import numpy as np
import onnxruntime as ort

from modules import c4d_uc5_settings as c4d
from modules import c4d_uc5_onnx_helper as c4dDetector
from modules import c4d_uc5_mavlink_helper as px4
from modules import c4d_uc5_aes_helper as c4dAes

import subprocess

################################################################################################
# Init
################################################################################################
c4dConfig = c4d.readConfiguration()
verbose = c4dConfig.verbose

# Serial Communication handler
comm=None
if not c4dConfig.skip_communication:
    comm = serial.Serial(c4dConfig.transmitter_device, c4dConfig.transmitter_boudrate, timeout=0.050)
    if verbose:
        print("[C4D] Connecting Serial Device: " + c4dConfig.transmitter_device)


# Vehicle Handler
vehicle = None
if not c4dConfig.px4_use_fake_position:
    if verbose:
        print("[C4D] Connect to PX4 at: " + c4dConfig.px4_device)
    vehicle = px4.initialize_mavlink(connection_string=c4dConfig.px4_device)

    # Create a message listener for "HOME_POSITION" message
    @vehicle.on_message('HOME_POSITION')
    def vehicle_position_callback(self, name, home_position):
        print("[C4D][Vehicle] Name " + str(name))
        print("[C4D][Vehicle] Get Home Position " + str(home_position))
        vehicle_position_init = True
    
    if verbose:
        print("[C4D] Vehicle listener created.")
else:
    vehicle_position_init = True

## ONNX Runtime Configuration ##
img_array = []
inputSize = (640, 640)

# Runtime Configuration
opts = ort.SessionOptions()
opts.intra_op_num_threads = 4
opts.inter_op_num_threads = 1
session = ort.InferenceSession(c4dConfig.crop_detector_model, sess_options=opts)
input_name = session.get_inputs()[0].name
output_0_name = session.get_outputs()[0].name
if verbose:
    print("[C4D][ONNX] Runtime session initialized...")
    print("[C4D][ONNX] Intra Number of threads = " + str(opts.intra_op_num_threads))
    print("[C4D][ONNX] Inter Number of threads = " + str(opts.inter_op_num_threads))


# Import and Split Video
if not c4dConfig.input_video_path:
    cap = cv2.VideoCapture(c4dConfig.input_camera_device_id)
    if verbose:
        print("[C4D] Read Input Video from Camera " + str(c4dConfig.input_camera_device_id))
else:
    cap = cv2.VideoCapture(c4dConfig.input_video_path)
    if verbose:
        print("[C4D] Read Input Video from " + str(c4dConfig.input_video_path))

# Frame Counter
frm_count = 0

# Read cap once to get constants
if not cap.isOpened():
    sys.exit("[C4D] ERROR: cap is not open. Program exiting...")
    
################################################################################################
# Start mission
################################################################################################
if not c4dConfig.px4_use_fake_position and not c4dConfig.px4_skip_wait_position:
    # wait for a home position lock
    while not vehicle_position_init:
        print("[C4D] Waiting for home position...")
        time.sleep(1)

# Display basic vehicle state
if not c4dConfig.px4_use_fake_position:
    print("[C4D][Vehicle] Type: %s" % vehicle._vehicle_type)
    print("[C4D][Vehicle] Armed: %s" % vehicle.armed)
    print("[C4D][Vehicle] System status: %s" % vehicle.system_status.state)
    print("[C4D][Vehicle] GPS: %s" % vehicle.gps_0)
    print("[C4D][Vehicle] Alt: %s" % vehicle.location.global_relative_frame.alt)
    print("[C4D][Vehicle] Lon: %s" % vehicle.location.global_relative_frame.lon)
    print("[C4D][Vehicle] Lat: %s" % vehicle.location.global_relative_frame.lat)

    # Change to AUTO mode
    px4.PX4setMode(c4dConfig.px4_mavlink_mode, vehicle)
    time.sleep(1)

################################################################################################
# MAIN LOOP
################################################################################################
try:
    while (cap.isOpened()):

        # Capture Timestamp
        curDT = datetime.datetime.now()
        outMSG = curDT.strftime("%Y%m%d%H%M%S")

        # Add IMEI
        outMSG += ',' + str(c4dConfig.vehicle_id)

        # Capture Position
        if not c4dConfig.px4_use_fake_position:
            latitude = vehicle.location.global_relative_frame.lat
            longitude = vehicle.location.global_relative_frame.lon
            altitude = vehicle.location.global_relative_frame.alt
            vx = vehicle.velocity[0]
            vy = vehicle.velocity[1]
            vz = vehicle.velocity[2]
        else:
            latitude = 0
            longitude = 0
            altitude = 0
            vx = 0
            vy = 0
            vz = 0

        if verbose:
            print("[C4D][Vehicle] Alt: %s" % altitude)
            print("[C4D][Vehicle] Lon: %s" % longitude)
            print("[C4D][Vehicle] Lat: %s" % latitude)
        
        
        outMSG += ',' + c4dAes.formatNumeric(latitude, 2, 10) \
                + ',' + c4dAes.formatNumeric(longitude, 2, 10) \
                + ',' + c4dAes.formatNumeric(altitude, 2, 10)
        # Capture Speed
        outMSG += ',' + c4dAes.formatNumeric(vx, 2, 7) \
                + ',' + c4dAes.formatNumeric(vy, 2, 7) \
                + ',' + c4dAes.formatNumeric(vz, 2, 7) + ','

        # Read Frame
        ret, frame = cap.read()
        if not ret:
            print('[C4D] Warning: skipping frame...')
            continue
        
        # ONNX Pre-process
        data = c4dDetector.inputPreprocess(frame, (640, 640))

        # ONNX Inference
        [result_0] = session.run([output_0_name], {input_name: data})
        if verbose:
            print("[C4D][ONNX] Inference Executed for frame " + str(frm_count))

        # ONNX Post-process
        mOutputRow = session.get_outputs()[0].shape[1]  # 25200
        mOutputColumn = session.get_outputs()[0].shape[2]  # 6

        # Post-processes: boxes extraction
        boxes = np.array(c4dDetector.outputPreprocess(result_0, mOutputRow, mOutputColumn, frame))

        # Post-processes: boxes NMS
        if boxes.shape[0] > 1:
            boxes_sorted = boxes[np.argsort(-1 * boxes[:, 4])]
        else:
            boxes_sorted = boxes
        rem_bbox = c4dDetector.FilterBoxesNMS(boxes, c4dConfig.crop_detector_thresh)
        rem_bbox = np.array(rem_bbox)

        if verbose:
            print("[C4D][ONNX] Post-Processing Executed for frame " + str(frm_count))
            print("[C4D][ONNX] Crop Detection Output: " + str(rem_bbox.shape[0]) + " plants")

        # Add artichoke count to out Msg
        outMSG += c4dAes.formatPlantCnt(rem_bbox.shape[0], 3)
        if verbose:
            print("[C4D] Plain Message: " + outMSG)

        if c4dConfig.output_video_path:
            # Print Boxes on frame and write frames
            if c4dConfig.show_crop_detection:
                frame = c4dDetector.printBBoxes(frame, rem_bbox)        
            img_array.append(frame)

        # Perform AES Encryption
        encryptedMsg=None
        if not c4dConfig.skip_encryption:
            result = subprocess.run(['bin/aes-hw-accel-wp5-08-rot', '-e', outMSG], stdout=subprocess.PIPE, universal_newlines=True)
            encryptedMsg = result.stdout
            if verbose:
                print("[C4D] Encrypted Message: " + encryptedMsg)

        # Perform Communication
        if not c4dConfig.skip_communication:
            comm.write(encryptedMsg.encode())
            if verbose:
                print("[C4D] Messaged sent to Serial")

        # Count Frames Computed and exit if necessary
        if c4dConfig.set_max_num_of_frames:
            if frm_count >= int(c4dConfig.set_max_num_of_frames):
                break
        frm_count += 1

except KeyboardInterrupt:
    # Exception for ctrl-c case
    cap.release()
    cv2.destroyAllWindows()

    ##  Write Video avi ##
    if c4dConfig.output_video_path:
        print("[C4D][ONNX] Writing Video Output at " + str(c4dConfig.output_video_path))
        c4dDetector.WriteC4DVideo(c4dConfig.output_video_path, img_array)

    # Close vehicle object before exiting scrip
    if not c4dConfig.px4_use_fake_position:
        vehicle.close()
        time.sleep(1)
    sys.exit()

cap.release()
cv2.destroyAllWindows()

##  Write Video avi ##
if c4dConfig.output_video_path:
    print("[C4D][ONNX] Writing Video Output at " + str(c4dConfig.output_video_path))
    c4dDetector.WriteC4DVideo(c4dConfig.output_video_path, img_array)

# Close vehicle object before exiting scrip
if not c4dConfig.px4_use_fake_position:
    vehicle.close()
    time.sleep(1)

