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

import argparse

def readConfiguration():
    # Parse connection argument
    parser = argparse.ArgumentParser()
    parser.add_argument("--vehicle_id", action='store', help="Vehicle Identifier used for communication", default="0000000000000000")

    # PX4 Connection and Configuration
    parser.add_argument("--px4_device", action='store', help="Path of PX4 device (default /dev/ttyACM0)", default="/dev/ttyACM0")
    parser.add_argument("--px4_mavlink_mode", action='store', help="Mavlink mode (default 4)", default=4)
    parser.add_argument("--px4_skip_wait_position", action='store_true', help="Bypass wait for GPS lock loop", default=False)
    parser.add_argument("--px4_use_fake_position", action='store_true', help="Use fake GPS position (for simulation purpose)", default=False)

    # Input Video Configuration
    parser.add_argument("--input_video_path", action='store', help="Path to input video. NOTE: that if this argument is set, camera frames are skipped.", default=None)
    parser.add_argument("--input_camera_device_id", action='store', help="Input camera ID", default=0)
    parser.add_argument("--set_max_num_of_frames", action='store', help="Set max number of frames processed (for simulation purpose)", default=None)

    # Processing Configuration
    parser.add_argument("--skip_inference", action='store_true', help="Skip crop detector", default=False)
    parser.add_argument("--crop_detector_model", action='store', help="ONNX DL Model for crop detection", default="models/c4d-aitek-v1.onnx")
    parser.add_argument("--crop_detector_thresh", action='store', help="Set ONNX bounding box confidence threshold", default=0.2)
    parser.add_argument("--show_crop_detection", action='store_true', help="Show on the frame the bboxes", default=False)
    parser.add_argument("--output_video_path", action='store', help="Write video output. NOTE: if --show_crop_detection option is active, the video will contain the detected bboxes", default=None)

    
    # Telemetry Encryption and transmission Configuration
    parser.add_argument("--skip_encryption", action='store_true', help="Set to True for skipping the encryption step.", default=False)
    parser.add_argument("--skip_communication", action='store_true', help="Set to True for skipping the communicatio step.", default=False)
    parser.add_argument("--transmitter_device", action='store', help="Set the serial device for outboud communication", default="/dev/ttyUSB0")
    parser.add_argument("--transmitter_boudrate", action='store', help="Set the serial device boudrate", default=9600)

    # Verbose
    parser.add_argument("--verbose", action='store_true', help="print messages for debugging", default=False)

    args = parser.parse_args()
    return args
