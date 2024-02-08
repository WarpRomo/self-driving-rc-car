from car_module import CarControl;
import time;

if __name__ == "__main__":

    CarManager = CarControl('http://20.1.1.70:5000', image_rate=-1); #Create Car Controller
    #image_rate=-1 makes it so that the manager will not fetch camera image (faster)


    time.sleep(0.1);

    #Move slowly forward and left
    CarManager.speed(0.3); #NOTE: the car goes fast, so keep the value low
    CarManager.turn(-1);

    time.sleep(0.5); #Stay that way for half a second

    #Stop moving, and stop turning
    CarManager.speed(0);
    CarManager.turn(0);

    time.sleep(0.1); #Give thread time to send 0 speed/turn instruction...

    CarManager.terminate(); #End controller
