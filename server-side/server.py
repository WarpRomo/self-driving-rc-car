import json
import time;

import logging
log = logging.getLogger('werkzeug')

from multiprocessing import Process, Manager;
from picamera2 import Picamera2, Preview
import base64;
import numpy;
import RPi.GPIO as GPIO

from flask import Flask, request, jsonify;

pwm_freq = 1000;

left_pin = 13
right_pin = 19

back_pin = 18
forw_pin = 12

led_pin = 21;

manager = Manager()
ns = manager.Namespace()

ns.car_direction = 0;
ns.car_speed = 0;
ns.idle_limit = 0.6;
ns.last_request = -1;

picam = Picamera2()

config = picam.create_preview_configuration()
picam.configure(config)

picam.start()


app = Flask(__name__);

def sign(x):

    if x >= 0: return 1;
    else: return -1;


@app.route('/')
def index():
    return "Awake"

@app.route('/control/', methods=['POST'])
def car_control():
    global ns;

    input = json.loads(request.data);

    if(input["type"] == "turn"):
        ns.car_direction = input["value"];

    if(input["type"] == "speed"):
        ns.car_speed = input["value"];

    ns.last_request = time.time();

    return "Done";

@app.route('/idleLimit/', methods=['POST'])
def set_idle_limit():
    global ns;

    input = json.loads(request.data);

    ns.idle_limit = input["value"];

    return "Done";


@app.route("/control/", methods=['GET'])
def car_control_g():
    global ns;
    input = json.loads(request.data);

    if(input["type"] == "turn"):
        return ns.car_direction;

    if(input["type"] == "speed"):
        return ns.car_speed;

    return "Bad Request...";

@app.route("/image/", methods=['GET'])
def car_image():

    input = json.loads(request.data or "{}");
    down_scale = 1;

    if "down_scale" in input:
        down_scale = input["down_scale"];

    curr_time = time.time();

    array = picam.capture_array("main");
    array = numpy.flip(array, 1)[:,:,:3];
    array = numpy.ascontiguousarray(array[::down_scale, ::down_scale]);

    delay = time.time() - curr_time;

    return json.dumps([str(array.dtype), base64.b64encode(array).decode('utf-8'), array.shape])


def car_loop():

    global ns;

    try:

        GPIO.setwarnings(False);
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(led_pin, GPIO.OUT);
        GPIO.output(led_pin, GPIO.HIGH);

        GPIO.setup(left_pin, GPIO.OUT);
        GPIO.setup(right_pin, GPIO.OUT);

        GPIO.setup(forw_pin, GPIO.OUT);
        GPIO.setup(back_pin, GPIO.OUT);

        pi_forw = GPIO.PWM(forw_pin, pwm_freq);
        pi_back = GPIO.PWM(back_pin, pwm_freq);

        pi_left = GPIO.PWM(left_pin, pwm_freq);
        pi_right = GPIO.PWM(right_pin, pwm_freq);

        pi_left.start(0);
        pi_right.start(0);

        pi_forw.start(0);
        pi_back.start(0);

        speed_store = [0,time.time(),100];

        accel_time = 0.06;
        deccel_time = 0.04;

        decell_forw = 0.1;
        decell_forw_time = 0.02;

        prev_time = time.time();

        while True:

            curr_time = time.time()


            if (curr_time - ns.last_request) > ns.idle_limit:
                ns.car_direction = 0;
                ns.car_speed = 0;

            speed_c = ns.car_speed;
            direction_c = ns.car_direction;

            if direction_c < 0:
                pi_left.ChangeDutyCycle(-direction_c*100);
                pi_right.ChangeDutyCycle(0);
            elif direction_c > 0:
                pi_left.ChangeDutyCycle(0);
                pi_right.ChangeDutyCycle(direction_c*100);
            else:
                pi_left.ChangeDutyCycle(0);
                pi_right.ChangeDutyCycle(0);


            curr_time = time.time();

            accel_prevented = False;

            speed_store[0] += curr_time - prev_time;

            if speed_c == 0 or sign(speed_c) != sign(speed_store[1]):
                speed_store[0] = 0;

            if speed_c != 0:
                speed_store[1] = speed_c;
                speed_store[2] = 0;


            speed = speed_c;


            if speed_c == 0:

                speed_store[2] += curr_time - prev_time;

                if (speed_store[1] > 0 and speed_store[2] <= deccel_time):
                    speed = -1;
                if (speed_store[1] < 0 and speed_store[2] <= decell_forw_time):
                    speed = decell_forw


            if(speed != 0 and speed_store[0] <= accel_time):
                speed = sign(speed);

            if speed < 0:
                pi_forw.ChangeDutyCycle(-speed*100);
                pi_back.ChangeDutyCycle(0);
            elif speed > 0:
                pi_forw.ChangeDutyCycle(0);
                pi_back.ChangeDutyCycle(speed*100);
            else:
                pi_forw.ChangeDutyCycle(0);
                pi_back.ChangeDutyCycle(0);

            prev_time = curr_time;
    except KeyboardInterrupt:

        GPIO.cleanup();


if __name__ == "__main__":

    car_process = Process(target=car_loop);

    car_process.start();
    app.run(host="0.0.0.0", threaded=True, use_reloader=False,debug=True);
    car_process.join();
