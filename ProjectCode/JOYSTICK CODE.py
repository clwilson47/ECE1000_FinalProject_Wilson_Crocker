#This script was inspired by Youtuber Paul McWhorter https://www.youtube.com/@paulmcwhorter.
# Videos used:
#     https://www.youtube.com/watch?v=KpDIv0i41Tw&t=953s
#     https://www.youtube.com/watch?v=ayY2wOJmrUE&t=1136s
#     https://www.youtube.com/watch?v=rRHyho4vwIQ
#     https://www.youtube.com/watch?v=0W8XSJhGux0

# The joystick utilizies two potentiometers and will output a voltage between two values depending on the position of the joystick. 
# In order to read these ANALOG values we must use an Analog to Digital Converter (ADC), which takes these continuous values and represents as signals the computer can understand (0, 1, etc...)

# How does this code work? Well, first we declare our libraries, then we delare what is hooked up to the Raspberry Pi Pico and to which pins they are connected, and finally we then ask the Pi Pico to show us the values of the joystick (FOREVER) .... (while True:)
from machine import PWM, ADC, Pin
import math
import utime


#This code shows the X/Y and switch joystick pins.We have the "X" pin on GP pin 27, and the "Y" pin on GP(26). Analog-to-Digital Converter(ADC) pins are needed because it allows us to convert the voltage in the joystick to binary numbers.
adc_x_joystick = ADC(Pin(26))
adc_y_joystick = ADC(Pin(27))
#This code is for the switch pin of the joystick,it doesn't need to be a ADC pin because it is either 0/1 meaning on or off.
sw_joystick = Pin(16, Pin.IN, Pin.PULL_UP)
# This is allowing us to move the servos using the inputs given from the joystick.  (50 Hz is a standard frequency for the pulse used to control the servos).
servo_x = PWM(Pin(0), freq=50)
servo_y = PWM(Pin(4), freq = 50)
servo_switch = PWM(Pin(1), freq = 50)

# This function will map the ADC value for the joystick to a value between -100 and 100 for ease of viewing (creating a slope between two points (m) and then creating a line y = mx + b)
# joystick_position = value from ADC (VRx)
# joystick_min = Joystick to the left/down
# joystick_max = Joystick to the right/up
# desired_min = -100
# desired_max = 100
def get_joystick_value(joystick_position, joystick_min, joystick_max, desired_min, desired_max):
    m = ((desired_min - desired_max)/(joystick_min - joystick_max))
    return int((m*joystick_position) - (m*joystick_max) + desired_max)

# This function will take the value from the joystick (between -100 and 100) and then convert it to a duty cycle to be used to control the servo motor (for my servos: 0.5 ms = 0 degrees,  2.5 ms = 180 degrees, and the period of the wave is normally 20 ms [1/freq = 1/50 = 0.02 sec])
def get_servo_duty_cycle(joystick_value, min_angle_ms, max_angle_ms, period_ms, desired_min, desired_max):
    point_1_x = desired_min
    point_1_y = (min_angle_ms/period_ms)*65536
    point_2_x = desired_max
    point_2_y = (max_angle_ms/period_ms)*65535
    m = (point_2_y - point_1_y) / (point_2_x - point_1_x)
    return int((m*joystick_value) - (m*desired_min) + point_1_y)
    
# In this while loop, we will continually read the status (position) of the x direction and switch ... the value shown for x will be between 0 and 65535 ... as the 65535 is the maximum number that can be represented with an unsigned 16 bit integer
# however, we will be representing this number in terms of -100 to 100 in order to read the value more clearly ... so, -100 will represent the servo -90 degrees and 100 will represent the servo +90 degrees
while True:
    # What does the u_16 mean? This means unsigned integrer with 16 bits ... this is the RESOLUTION of our Analog to Digital Converter that is used to fully show where the joystick is!
    x_position = adc_x_joystick.read_u16()
    y_position = adc_y_joystick.read_u16()
    # We don't need u16 here as value() will give us either 0 or 1 ... 1 will represent no push on the button and 0 will represent pushed down
    sw_status = sw_joystick.value()        
    
#This code converts the big range of binary numbers(320-65535) to a smaller easier value (-100,100).
    x_value = get_joystick_value(x_position, 320, 65535, -100, 100)
    y_value = get_joystick_value(y_position, 320, 65536, -100, 100)
    
    
    # This portion will find the maximum length of values (from -100 to 100) and then if we are close to 0 (meaning the joystick is in the middle), the values will be set to 0 to remove any jittering or noise
    range_of_values=math.sqrt(x_value**2+y_value**2)
    #When the joystick isnt moving it gives values of 0-8,therefore to remove that jittering we set any value less than or equal to 8 to display as 0.
    if range_of_values<=8:
        x_value=0
        y_value=0
        
    # This portion will call the function above to get the joystick value into a useable form (duty cycle percentage)
    x_duty = get_servo_duty_cycle(x_value, 0.5, 2.5, 20, -100, 100)
    y_duty = get_servo_duty_cycle(y_value, .75, 2.5, 20, -100, 100)
    
    # This portion will get the value from the switch and will set it to the max value if the switch is pressed in.
    if sw_status == 0:
        #0.5 is when the servo is turned all the way to the left or -90 degrees(starting from 0)
        sw_duty = int((0.5*65535)/20)
    else: #Else shows if the button isnt being pressed the servo will be at 1.3ms
        #1.3 for us is around when the servo is 0 degrees.Visually it allows for our robot to return to an upright position
        sw_duty = int((1.3*65535)/20)
    
    servo_x.duty_u16(x_duty)
    servo_y.duty_u16(y_duty)
    servo_switch.duty_u16(sw_duty)
    
    # Finally, we print out the values so we can check what is happening as the code runs.
    print(f"x_value is: {x_value},  x_duty is: {x_duty}, y_value is: {y_value}, y_duty is: {y_duty}, sw_status is: {sw_status}, sw_duty is: {sw_duty}")
    #utime shows the binary number outputs.
    utime.sleep(0.1)
