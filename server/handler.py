import re
import RPi.GPIO as GPIO

"""
N  w s a d ACTION
01 0 0 0 0 stop
02 1 1 0 0 stop
03 0 0 1 1 stop
04 1 0 1 1 forward
05 0 1 1 1 backward
06 1 1 1 0 stop
07 1 1 0 1 stop
08 1 1 1 1 stop
09 1 0 0 0 forward
10 0 0 1 0 forward_left
11 1 0 1 0 forward_left
12 0 0 0 1 forward_right
13 1 0 0 1 forward_right
14 0 1 0 0 backward
15 0 1 1 0 backward_left
16 0 1 0 1 backward_right

Wheel Pin
LEFT_FRONT 0-----0 RIGHT_FRONT
            |   |
            |   |
LEFT_REAR  0-----0 RIGHT_REAR

"""

LEFT_FRONT_FORWARD = 18
LEFT_FRONT_BACKWARD = 18

RIGHT_FRONT_FORWARD = 18
RIGHT_FRONT_BACKWARD = 18

LEFT_REAR_FORWARD = 18
LEFT_REAR_BACKWARD = 18

RIGHT_REAR_FORWARD = 18
RIGHT_REAR_BACKWARD = 18

#Initialize

GPIO.setmode(GPIO.BCM)
for PIN in [LEFT_FRONT_FORWARD,LEFT_FRONT_BACKWARD, RIGHT_FRONT_FORWARD, RIGHT_FRONT_BACKWARD, LEFT_REAR_FORWARD,\
            LEFT_REAR_BACKWARD, RIGHT_REAR_FORWARD, RIGHT_REAR_BACKWARD]:
    GPIO.setup(PIN, GPIO.OUT)

PRESSED = 1
RELEASED = 0

stat_dict = {'w':RELEASED,
             's':RELEASED,
             'a':RELEASED,
             'd':RELEASED}

def action_forward():
    print 'drive: forward'
    for pin in [LEFT_FRONT_FORWARD, RIGHT_FRONT_FORWARD]:
        GPIO.output(pin, GPIO.HIGH)
    for pin in [LEFT_FRONT_BACKWARD, RIGHT_FRONT_BACKWARD, LEFT_REAR_FORWARD,\
            LEFT_REAR_BACKWARD, RIGHT_REAR_FORWARD, RIGHT_REAR_BACKWARD]:
        GPIO.output(pin, GPIO.LOW)

def action_backward():
    print 'drive: backward'
    for pin in [LEFT_REAR_BACKWARD, RIGHT_REAR_BACKWARD]:
        GPIO.output(pin, GPIO.HIGH)
    for pin in [LEFT_FRONT_FORWARD, LEFT_FRONT_BACKWARD, RIGHT_FRONT_FORWARD,\
                RIGHT_FRONT_BACKWARD, LEFT_REAR_FORWARD, RIGHT_REAR_FORWARD]:
        GPIO.output(pin, GPIO.LOW)

def action_forward_left():
    print 'drive: forward_left'

def action_forward_right():
    print 'drive: forward_right'

def action_backward_left():
    print 'drive: backward_left'

def action_backward_right():
    print 'drive: backward_right'

def action_stop():
    print 'drive: stop'
    for pin in [LEFT_FRONT_FORWARD, LEFT_FRONT_BACKWARD, RIGHT_FRONT_FORWARD, RIGHT_FRONT_BACKWARD, LEFT_REAR_FORWARD, \
                LEFT_REAR_BACKWARD, RIGHT_REAR_FORWARD, RIGHT_REAR_BACKWARD]:
        GPIO.output(pin, GPIO.LOW)


def is_stop(dict):
    """
    Check if the status is stop
    """
    if PRESSED not in dict.values() or RELEASED not in dict.values():
        return True
    if dict['w'] == PRESSED and dict['s'] == PRESSED:
        return True
    if dict['a'] == PRESSED and dict['d'] == PRESSED:
        return True

def is_forward(dict):
    """
    Check if the status is forward
    :param dict:
    :return:
    """
    if dict['w'] == PRESSED and dict['s'] == RELEASED and dict['a'] == RELEASED and dict['d'] == RELEASED:
        return True

def is_backward(dict):
    if dict['w'] == RELEASED and dict['s'] == PRESSED and dict['a'] == RELEASED and dict['d'] == RELEASED:
        return True

def is_forward_left(dict):
    if dict['a'] == PRESSED and dict['d'] == RELEASED and dict['s'] == RELEASED:
        return True

def is_forward_right(dict):
    if dict['d'] == PRESSED and dict['a'] == RELEASED and dict['s'] == RELEASED:
        return True

def is_backward_left(dict):
    if dict['a'] == PRESSED and dict['s'] == PRESSED and dict['w'] == RELEASED and dict['d'] == RELEASED:
        return True

def is_backward_right(dict):
    if dict['d'] == PRESSED and dict['s'] == PRESSED and dict['w'] == RELEASED and dict['a'] == RELEASED:
        return True


def update_stat_dict(data, stat_dict):
    """
    Better way to update the socket data to status dictionary
    """
    if not re.match(r'\w\s\w', data):
        print 'not correct data'
        return True
    else:
        stat_dict[data[0]] = PRESSED if data[-1] == 'd' else RELEASED


def drive_car(stat_dict):
    """
    Determine which action according to the stat_dict
    :param stat_dict:
    :return:
    """
    '''
    for action in ['stop', 'forward', 'backward', 'forward_left', 'backward_left']:
        action_fun = 'action_%s' % action
        is_action_fun = 'is_%s' % action
        if eval(is_action_fun)(stat_dict):
            eval(action_fun)
    '''
    if is_stop(stat_dict):
        action_stop()
    if is_forward(stat_dict):
        action_forward()
    if is_backward(stat_dict):
        action_backward()
    if is_forward_left(stat_dict):
        action_forward_left()
    if is_forward_right(stat_dict):
        action_forward_right()
    if is_backward_left(stat_dict):
        action_backward_left()
    if is_backward_right(stat_dict):
        action_backward_right()

