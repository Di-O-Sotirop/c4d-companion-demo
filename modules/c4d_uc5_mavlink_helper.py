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

from dronekit import connect, Command, LocationGlobal
from pymavlink import mavutil
import pymavlink
import dronekit

def initialize_mavlink(connection_string):
    # Connect to the Vehicle
    return connect(connection_string, wait_ready=True)


def PX4setMode(mavMode, vehicle):
    vehicle._master.mav.command_long_send(vehicle._master.target_system, vehicle._master.target_component,
                                          mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
                                          mavMode,
                                          0, 0, 0, 0, 0, 0)
