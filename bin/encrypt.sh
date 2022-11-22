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

#!/bin/bash
aesX="bin/aes-hw-accel-wp5-08-rot"
len=${#1}
aesstep=16

aes_output_file="output/aes-hw-accel-wp5-08-rot.out"
aes_tmp="output/aes-hw-accel-wp5-08-rot.tmp"
encrypted_msg="output/encrypted-msg.out"

cat /dev/null > $encrypted_msg
for i in $(seq 0 $aesstep $len)
do
  ./$aesX ${1:i:$(($i+16))} > $aes_output_file
  grep "CIPHERTEXT: " -n $aes_output_file > $aes_tmp
  cut -c 34- $aes_tmp >> $encrypted_msg
done
