# Documentation

### CarController(ip=string, image_rate=float, image_downsample=int, control_rate=float)
> #### ip(required)
> The IP of the car's server to connect to, example: ip="http://127.0.0.1:5000"

> #### image_rate
> The interval at which to fetch the image from the camera of the car, set to -1 to fetch nothing at all, example: image_rate=0.1

> #### image_downsample
> The amount to scale down the image the car sends from the image fetch, higher is faster, example: image_downsample=10

> #### control_rate
> The interval at which to send car inputs to the car's server, example: control_rate=0.1</p>

> Note: For image_rate and control_rate, do not use too low of a value or the server will become flooded. Recommended is 0.1 for both.

### CarController.turn(value=float)

> #### value(required)
> The direciton that the wheels should be set to. -1 is left, 1 is right, keep the value between -1 and 1, example: value=0.7

### CarController.speed(value=float)
> #### value(required)
> The speed that the wheels should turn -1 is backwrads, 1 is forwards, keep the value between -1 and 1 and low, example: value=-0.3

### CarController.ns.carImage : nd.array
> An RGB array containing the most recently fetched image from the car.
