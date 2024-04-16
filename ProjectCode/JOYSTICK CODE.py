import machine
import time
import math
hPin=27
vPin=26
hJoy= machine.ADC(hPin)
vJoy= machine.ADC(vPin)
while True:
    vVal=hJoy.read_u16()
    hVal=vJoy.read_u16()
    print(vVal,hVal)
    time.sleep_ms(200) 