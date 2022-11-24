# C4D UC5 Demo SW Documentation (v0.3)
The demo consists of a Kria board with PX4 equipped with a camera and a GPS module. The board is running an artichoke detection neural network and an AES encryptor.

## Components 
- **Bin\\**: Folder containing the AES binary file and the script to execute the binary and manage the output.
- **Docs\\**: Folder containing documentation
- **Models\\**: Folder containing the AITEK plant detector CNN model ONNX file.
- **Modules\\**: Folder containing custom library files in python for the c4d-uc5-launcher.py script.
- **Output\\**: Folder containing files with the encrypted output of the project as well as an encryption report.

## C4D UC5 Demo Message Format
For each frame acquired by the camera, an output string of comma separated values (83 characters + 8 commas) is generated, encrypted and trasmitted to the dashboard by the companion computer.
The Mmssage format is the follow:

```
<timestamp>,<IMEI>,<Latitude>,<Longitude>,<Altitude>,<SpeedX>,<SpeedY>,<SpeedZ>,<NumPlants>
```

Where
- `<timestamp>`: Timestamp of the message in format `yyyymmddhhmmss` (14 chars)
- `<IMEI>`: UAV Identifier in format `xxxxxxxxxxxxxxx` (15 chars)
- `<Latitude>`: Latitude of UAV in format `{sign}XX.XXXXXX` (10 chars)
- `<Longitude>`: Longitude of UAV in format `{sign}XX.XXXXXX` (10 chars)
- `<Altitude>`: Altitude of UAV in format `{sign}XX.XXXXXX` (10 chars)
- `<SpeedX>`: Speed on X-axis (*m/s*) of UAV in format `{sign}XX.XXX` (7 chars)
- `<SpeedY>`: Speed on Y-axis (*m/s*) of UAV in format `{sign}XX.XXX` (7 chars)
- `<SpeedZ>`: Speed on X-axis (*m/s*) of UAV in format `{sign}XX.XXX` (7 chars)
- `<NumPlants>`: Number of plants detected in format `XXX` (3 chars)

## C4D UC5 Demo Launcher Command Line Arguments
Argument	type	Description	Default
|Argument|Type|Default|Description|
|---|---|---|---|
|`--vehicle_id`| `string` | `"0000000000000000”`| Vehicle Identifier used for communication. (Output message IMEI) |
|`--px4_device`| `string` | `"/dev/ttyACM0"`| Path of PX4 device |
|`--px4_mavlink_mode`| `integer` | `4` (AUTO) | Mavlink mode|
|`--px4_skip_wait_position`| `boolean` | `False`| Bypass wait for GPS lock loop|
|`--px4_use_fake_position`| `boolean` | `False`| Use fake GPS position (for simulation purpose) |
|`--input_video_path`| `string` | `None`| Path to input video. NOTE: that if this argument is set, camera frames are skipped |
|`--input_camera_device_id`| `integer` | `0`| Input camera ID |
|`--set_max_num_of_frames`| `integer` | `None`| Set max number of frames processed (for simulation purpose) |
|`--crop_detector_model`| `string` | `"models/c4d-aitek-v1.onnx"` | ONNX DL Model for crop detection |
|`--crop_detector_thresh`| `integer` | `0.2`| Set ONNX NMS threshold |
|`--show_crop_detection`| `boolean` | `False` | Show on the frame the bboxes |
|`--output_video_path`| `string` | `None`| Write video output. NOTE: if `--show_crop_detection` option is active, the video will contain the detected bboxes |
|`--skip_encryption`| `boolean` | `False` | Set to True for skipping the encryption step |
|`--skip_communication`| `boolean` | `False` | Set to True for skipping the communication step |
|`--transmitter_device`| `string` | `"/dev/ttyUSB0"` | Set the serial device for outbound communication |
|`--transmitter_boudrate`| `integer` | `9600`| Set the serial device baud rate |
|`--verbose`| `boolean` | `False` | Print All Messages (for debugging) |

*Boolean* options are set true just by `--{command}` while all other have to be assigned a value like `--{command} {value}`

## C4D UC5 Demo Launcher Description
The main script is the `c4d-uc5-launcher.py`. In general the script
1. initializes the onnx runtime for the artichoke detector network model as well as
2. the mavlink communication and then
3. loops infinitely until the camera is closed. 

In each instance of the loop, the GPS position is captured and then the network is executed. At the end of the post-processing of the network output, the GPS coordinates and the artichoke count are encrypted and sent to the transmitter for communication. The produced output can also be evaluated in the output folder.

The functionality of the containing code of the `c4d-uc5-launcher.py is` presented in the sections below.

### Aitek Artichoke Detector NN
The network provided by aitek is running on ONNX runtime on 4 arm-cortex cores of the board.
Initialization, execution of the network and post processing is handled by python code.

Before the execution of the network the camera or video input is preprocessed with padding and downscaling. The ONNX runtime is initialized to utilize the 4 arm-cortex cores. 
The raw output is then post-processed. Bounding boxes with confidence lower than the threshold (0.25) are dumped and *Non-maximal suppression* (NMS) is applied to clean overlapping boxes with threshold of overlap at 0.2.

Preprocessing function `ResizeAndPad()` and post-processing functions `bbox_intersection_over_union()` and `FilterBoxesNMS()` are defined in the `modules/c4d_uc5_onnx_helper.py`

Parameterization of the network is done via the argparse python library with all the options defined in the `c4d_uc5_settings.py` file. The default configuration of the deliverable is set for the outdoor application using a camera for artichoke detection. The settings can be configured to use an input video instead of a camera and write the input video to AVI for testing.
For further notes on the parameters either run the script using the `–help` parameter (`python3 c4d-uc5-launcher.py –help`) or look at the previous table `Command Line Arguments`.


### Mavlink Communication
Code for communication between the board and the connected PX4 via mavlink is drawn from DroneKit and defined in `modules/c4d_uc5_mavlink_helper.py`.
The code receives GPS information from the GPS module of the PX4. For this, the gps module requires a `Good 3D-fix` -- communication with multiple satellites to triangulate an accurate gps position --. **This only works in outdoor areas**. 
To bypass the waiting loop for a `Good 3D-fix` execute the launcher with the `--px4_skip_wait_position` argument.
In outdoors application, the board requests an initial home position from the PX4 GPS module that is updated at the start of every loop. The GPS position coordinates of the PX4 are updated dynamically.

### AES Encryptor/Decryptor
In the current version of the demo the AES encryptor is called from an executable binary file `aes-hw-accel-wp5-08-rot` written in C. The executable takes an input of 16 bytes per execution. Note that the application will always encrypt 16 bytes, filling the rest of the message with junk from memory should less bytes be inputted. 
The executable was produced for testing and outputs a complete report of the execution (input message, execution time, encrypted message, decrypted message etc)
The executable is called at each loop from the `bin\encrypt.sh` script that cleans the long output report, writing only the encrypted message (cipher) in the `output\encrypted-msg.out` file that is overwritten with the new message on every loop. The full encryption report is saved in `output/aes-hw-accel-wp5-08-rot.out`.

## Notes for the Developer
The project has been tested on a Xilinx Kria 260 board with a Pixhawk Holybro with a Holybro Pixhawk 4 GPS M8N module. The message is sent to a serial converter utilizing the ftdi driver for the transmitter.
