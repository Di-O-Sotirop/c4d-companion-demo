from dronekit import connect, Command, LocationGlobal
from pymavlink import mavutil
import pymavlink
import dronekit

import argparse, math, time

def initialize_mavlink(connection_string='/dev/ttyACM0'):
    MAV_MODE_AUTO = 4
    # https://github.com/PX4/PX4-Autopilot/blob/master/Tools/mavlink_px4.py

    # Parse connection argument
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--connect", help="connection string")
    args = parser.parse_args()

    if args.connect:
        connection_string = args.connect

    # Connect to the Vehicle
    print("Connecting")
    global vehicle
    vehicle = connect(connection_string, wait_ready=True)



def PX4setMode(mavMode):
    vehicle._master.mav.command_long_send(vehicle._master.target_system, vehicle._master.target_component,
                                          mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
                                          mavMode,
                                          0, 0, 0, 0, 0, 0)

def PX4changeToAuto():
    PX4setMode(mavMode)
def get_location_offset_meters(original_location, dNorth, dEast, alt):
    """
    Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the
    specified `original_location`. The returned Location adds the entered `alt` value to the altitude of the `original_location`.
    The function is useful when you want to move the vehicle around specifying locations relative to
    the current vehicle position.
    The algorithm is relatively accurate over small distances (10m within 1km) except close to the poles.
    For more information see:
    http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
    """
    earth_radius = 6378137.0  # Radius of "spherical" earth
    # Coordinate offsets in radians
    dLat = dNorth / earth_radius
    dLon = dEast / (earth_radius * math.cos(math.pi * original_location.lat / 180))

    # New position in decimal degrees
    newlat = original_location.lat + (dLat * 180 / math.pi)
    newlon = original_location.lon + (dLon * 180 / math.pi)
    return LocationGlobal(newlat, newlon, original_location.alt + alt)
