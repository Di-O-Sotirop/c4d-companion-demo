# c4d-companion-demo
This is the demo for the companion drone of the comp4drones project.

Run python3 masterScript.py directly.
If it fails try:
python3 -m venv onnx_mnist
source onnx_mnist/bin/activate
Then run the masterScript.py again


AES Encryption
The current repo does not include the aes encryption software. 
If the aes_sw is missing download the cloned repo from https://github.com/Di-O-Sotirop/Clone-aes-sw.git, compile it using `make clean all`
and move the executable `aes_sw` to the demo folder (where `masterScript.py` resides).
