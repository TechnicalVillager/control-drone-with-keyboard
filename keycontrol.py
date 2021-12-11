#!/usr/bin/env python

#...........................................................................
# Author:  Saiffullah Sabir Mohamed
# Github:  https://github.com/TechnicalVillager
# Website: http://technicalvillager.github.io/
#...........................................................................

# Import Necessary Packages
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time, math
from sshkeyboard import listen_keyboard
from pymavlink import mavutil

def basic_takeoff(altitude):

    """

    This function take-off the vehicle from the ground to the desired
    altitude by using dronekit's simple_takeoff() function.

    Inputs:
        1.  altitude            -   TakeOff Altitude

    """

    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True
    time.sleep(2)
    vehicle.simple_takeoff(altitude)

    while True:
        print("Reached Height = ", vehicle.location.global_relative_frame.alt)

        if vehicle.location.global_relative_frame.alt >= (altitude - 1.5):
            break
        time.sleep(1)


def change_mode(mode):

    """

    This function will change the mode of the Vehicle.

    Inputs:
        1.  mode            -   Vehicle's Mode

    """

    vehicle.mode = VehicleMode(mode)


def send_to(latitude, longitude, altitude):

    """

    This function will send the drone to desired location, when the 
    vehicle is in GUIDED mode.

    Inputs:
        1.  latitude            -   Destination location's Latitude
        2.  longitude           -   Destination location's Longitude
        3.  altitude            -   Vehicle's flight Altitude

    """

    if vehicle.mode.name == "GUIDED":
        location = LocationGlobalRelative(latitude, longitude, float(altitude))
        vehicle.simple_goto(location)
        time.sleep(1)

def change_alt(step):

    """
    
    This function will increase or decrease the altitude
    of the vehicle based on the input.

    Inputs:
        1.  step            -   Increase 5 meters of altitude from 
                                current altitude when INC is passed as argument.

                            -   Decrease 5 meters of altitude from 
                                current altitude when DEC is passed as argument.

    """

    actual_altitude = int(vehicle.location.global_relative_frame.alt)
    changed_altitude = [(actual_altitude + 5), (actual_altitude - 5)]

    if step == "INC":
        if changed_altitude[0] <= 50:
            send_to(vehicle.location.global_frame.lat, vehicle.location.global_frame.lon, changed_altitude[0])
        else:
            print("Vehicle Reached Maximum Altitude!!!")

    if step == "DEC":
        if changed_altitude[1] >= 5:
            send_to(vehicle.location.global_frame.lat, vehicle.location.global_frame.lon, changed_altitude[1])
        else:
            print("Vehicle Reached Minimum Altitude!!!")


def destination_location(homeLattitude, homeLongitude, distance, bearing):

    """

    This function returns the latitude and longitude of the
    destination location, when distance and bearing is provided.

    Inputs:
        1.  homeLattitude       -   Home or Current Location's  Latitude
        2.  homeLongitude       -   Home or Current Location's  Latitude
        3.  distance            -   Distance from the home location
        4.  bearing             -   Bearing angle from the home location

    """

    #Radius of earth in metres
    R = 6371e3

    rlat1 = homeLattitude * (math.pi/180) 
    rlon1 = homeLongitude * (math.pi/180)

    d = distance

    #Converting bearing to radians
    bearing = bearing * (math.pi/180)

    rlat2 = math.asin((math.sin(rlat1) * math.cos(d/R)) + (math.cos(rlat1) * math.sin(d/R) * math.cos(bearing)))
    rlon2 = rlon1 + math.atan2((math.sin(bearing) * math.sin(d/R) * math.cos(rlat1)) , (math.cos(d/R) - (math.sin(rlat1) * math.sin(rlat2))))

    #Converting to degrees
    rlat2 = rlat2 * (180/math.pi) 
    rlon2 = rlon2 * (180/math.pi)

    # Lat and Long as an Array
    location = [rlat2, rlon2]

    return location

def condition_yaw(heading):

    """
    
    This function helps the vehicle to maintain its
    heading thorught the flight (Heading Lock).

    Inputs:
        1.  heading         -   Desired heading value in Degrees

    """

    #yaw is an absolute angle
    is_relative=0 

    # create the CONDITION_YAW command using command_long_encode()
    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_CONDITION_YAW, #command
        0,              #confirmation
        heading,        # param 1, yaw in degrees
        0,              # param 2, yaw speed deg/s
        1,              # param 3, direction -1 ccw, 1 cw
        is_relative,    # param 4, relative offset 1, absolute angle 0
        0, 0, 0)        # param 5 ~ 7 not used

    # send command to vehicle
    vehicle.send_mavlink(msg)

def control(value):

    """
    
    This function call the respective functions based on received arguments.

        t             -       Take-Off
        l             -       Land
        g             -       Guided Mode
        r             -       RTL Mode
        up, down,
        right, left   -       This will call the navigation() function 

    Inputs:
        1.  value         -   ['space', 'tab', 't', 'l', 'g', 'r', 'up', 'down', 'right', 'left']

    """

    allowed_keys = ['space', 'tab', 't', 'l', 'g', 'r', 'up', 'down', 'right', 'left']

    if value in allowed_keys:

        if value == 'space':
            change_alt(step = "INC")

        if value == 'tab':
            change_alt(step = "DEC")

        if value == 't':
            if int(vehicle.location.global_relative_frame.alt) <= 5:
                basic_takeoff(altitude = 5)

        if value == 'l':
            change_mode(mode = "LAND")

        if value == 'g':
            change_mode(mode = "GUIDED")

        if value == 'r':
            change_mode(mode = "RTL")

        if value in allowed_keys[-4:]:
            navigation(value = value)

    else:
        print("Enter a valid Key!!!")


def navigation(value):

    """
    
    This function moves the vehicle to front, back, right, left
    based on the input argument.

        UP       -   Moves the Vehicle to Forward
        DOWN     -   Moves the Vehicle to Backward
        RIGHT    -   Moves the Vehicle to Right
        LEFT     -   Moves the Vehicle to Left

    Inputs:
        1.  value         -   [right, left, up, down]

    """

    # Vehicle Location
    angle = int(vehicle.heading)
    loc   = (vehicle.location.global_frame.lat, vehicle.location.global_frame.lon, vehicle.location.global_relative_frame.alt)

    # Default Distance in meters
    default_distance = 5

    if value == 'up':
        front = angle + 0
        new_loc = destination_location(homeLattitude = loc[0], homeLongitude = loc[1], distance = default_distance, bearing = front)
        send_to(new_loc[0], new_loc[1], loc[2])

    if value == 'down':
        back = angle + 180
        new_loc = destination_location(homeLattitude = loc[0], homeLongitude = loc[1], distance = default_distance, bearing = back)
        send_to(new_loc[0], new_loc[1], loc[2])

    if value == 'right':
        right = angle + 90
        new_loc = destination_location(homeLattitude = loc[0], homeLongitude = loc[1], distance = default_distance, bearing = right)
        send_to(new_loc[0], new_loc[1], loc[2])

    if value == 'left':
        left = angle -90
        new_loc = destination_location(homeLattitude = loc[0], homeLongitude = loc[1], distance = default_distance, bearing = left)
        send_to(new_loc[0], new_loc[1], loc[2])

def press(key):

    """
    
    This function prints the keybooard presses and calls the control()
    function.

    Inputs:
        1.  key         -   Pressed keyboard Key

    """

    print(f"'{key}' is pressed")

    # Sending Control Inputs
    control(value = key)

def main():

    # Declaring Vehicle as global variable
    global vehicle

    # Connecting the Vehicle
    vehicle = connect('udpin:127.0.0.1:14551', baud=115200)

    # Conditional Yaw (Setting the Heading as 0 degree for entire flight)
    condition_yaw(heading=0)

    # Listen Keyboard Keys
    listen_keyboard(on_press=press)

if __name__ == "__main__":
    main()