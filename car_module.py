import json;
import numpy;
import requests;
import threading;
import base64;
import time;

import threading;

class CarControl:

    def __init__(self, ip, image_rate=0.1, image_downscale=10, control_rate=0.1):

        self.ip = ip;
        self.image_rate = image_rate;
        self.image_downscale = image_downscale;
        self.control_rate = control_rate;

        if not self.ping():
            raise Exception("IP Invalid, or server is down. Example IP: 'http://20.1.1.70:5000' (http://ip:port)")

        print("Connection success...");

        self.session = requests.Session();

        image_process = threading.Thread(target=self.image_loop);
        control_process = threading.Thread(target=self.control_loop);

        self.turnValue = 0;
        self.speedValue = 0;
        self.carImage = [];

        self.image_process_started = False;
        self.control_process_started = False;

        image_process.start();
        control_process.start();

        self.image_process = image_process;
        self.control_process = control_process;

        while not (self.image_process_started and self.control_process_started): 1;

        print("Car Controller Created.")


    def terminate(self):
        self.image_process_started = False;
        self.control_process_started = False;

    def ping(self):
        try:
            res = requests.get(self.ip)
            if(res.text == "Awake"): return True;
            return False;
        except:
            return False;

    def idle_limit(self,value):

        self.session.post(self.ip + "/idleLimit/",
                         json={
                             'value': value
                         });


    def async_control(self, type, value):
        try:
            self.session.post(self.ip + "/control/",
                             json={
                                 'type': type,
                                 'value': value
            });
        except Exception:
            return;

    def async_image(self):
        try:
            image = self.session.get(self.ip + "/image/", json={"down_scale": self.image_downscale});

            enc = json.loads(image.text)

            dataType = numpy.dtype(enc[0])
            dataArray = numpy.frombuffer(base64.b64decode(enc[1]), dataType).reshape(enc[2])

            self.carImage = dataArray;
        except Exception:
            return;


    def image_loop(self):
        self.image_process_started = True;

        while True:

            if(not self.image_process_started): break;
            if(self.image_rate == -1): continue;

            threading.Thread(target=self.async_image).start()

            time.sleep(self.image_rate);


    def control_loop(self):
        self.control_process_started = True;

        while True:

            if(not self.control_process_started): break;
            if(self.control_rate == -1): continue;

            threading.Thread(target=self.async_control, args=("turn", self.turnValue)).start();
            threading.Thread(target=self.async_control, args=("speed", self.speedValue)).start();

            time.sleep(self.control_rate);


    def turn(self,value):
        self.turnValue = value;

    def speed(self,value):
        self.speedValue = value;
