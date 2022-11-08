################################################################################################
# Settings
################################################################################################
import argparse
#import sys


# https://github.com/PX4/PX4-Autopilot/blob/master/Tools/mavlink_px4.py

def manipulate_args():
    # Parse connection argument
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulation",     action='store_true',    help="Bypass wait for GPS lock loop for Simulation")
    parser.add_argument("--connectPX4",     action='store',         help="Path of PX4 device (default /dev/ttyACM0", nargs='?',
                        default='/dev/ttyACM0')
    parser.add_argument("--MAV_MODE_AUTO",  action='store',         help="Mavlink mode (default 4)", default=4)
    parser.add_argument("--model_dir",      action='store',         help="directory of .onnx model", default="")
    parser.add_argument("--model",          action='store',         help=".onnx model filename", default="c4d-aitek-v1.onnx")
    parser.add_argument("--vid_path",       action='store',         help="path to sample video for simulation",
                        default="/samples/2022-01-28_15m.mp4")
    parser.add_argument("--set_encrypt_script", action='store',    help="set the path to encryption script", default="encryptDemos_16B.sh")
    parser.add_argument("--boxOnFrame",     action='store_true',    help="print bboxes on frame")
    parser.add_argument("--write_frames",   action='store_true',    help="write frames to png")
    parser.add_argument("--write_video",    action='store_true',    help="write frames to avi")
    parser.add_argument("--full_video",     action='store_true',    help="write whole video")
    parser.add_argument("--nocamera",       action='store_true',    help="enable camera input")
    parser.add_argument("--artichokeCount", action='store_true',    help="print artichoke count")
    parser.add_argument("--cameraID",       action='store',         help="Choose camera", default=0)
    parser.add_argument("--thresh",         action='store',         help="set bbox confidence threshold", default=0.2)
    parser.add_argument("--num_of_frames",  action='store',         help="set number of frames from input video", default=100)
    parser.add_argument("--print_msg",      action='store_true',    help="print the output message to console")
    parser.add_argument("--verbose",        action='store_true',    help="print messages for debugging")

    args = parser.parse_args()
    return args
def printV(str,v):
    if v:
        print(str)
        

