from car_module import CarControl;
import time;

import PIL;
from PIL import Image;

if __name__ == "__main__":

    CarManager = CarControl('http://20.1.1.70:5000', image_downscale=3); #Create Car Controller

    #image_downscale is how much to reduce the resolution of the image.
    #lower resolution image = faster

    time.sleep(0.1); #give time to fetch image

    imageArray = CarManager.ns.carImage #RGB pixels
    PIL.Image.fromarray(imageArray, "RGB").show()

    CarManager.terminate(); #End controller
