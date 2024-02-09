# Documentation

### CarController(params)

> ### ip(required)
> The IP of the car's server to connect to.

> ### image_rate
> The interval at which to fetch the image from the camera of the car, set to -1 to fetch nothing at all.

> ### image_downsample
> The amount to scale down the image the car sends from the image fetch, higher is faster.

> ### control_rate
> The interval at which to send car inputs to the car's server.

> [!WARNING]
> For image_rate and control_rate, do not use too low of a value or the server will become flooded.

```python
CarManager = CarControl(ip="http://127.0.0.1:5000")
```
```python
CarManager = CarControl(ip="http://127.0.0.1:5000",
                        image_rate=0.1,
                        control_rate=0.1)
```
```python
CarManager = CarControl(ip="http://127.0.0.1:5000",
                        image_rate=0.1,
                        control_rate=0.1,
                        image_downsample=10)
```

### CarController.turn(params)

> ### value(required)
> The direction that the wheels should be set to. -1 is left, 1 is right, keep the value between -1 and 1.

```python
CarManager = CarControl(ip="127.0.0.1:5000")
CarManager.turn(-1) #turn left
```

### CarController.speed(params)
> ### value(required)
> The speed that the wheels should turn -1 is backwrads, 1 is forwards, keep the value between -1 and 1 and low.

```python
CarManager = CarControl(ip="127.0.0.1:5000")
CarManager.turn(-0.3) #move backwards
```

### CarController.ns.carImage
> A numpy RGB array containing the most recently fetched image from the car.

```python
CarManager = CarControl(ip="127.0.0.1:5000")
time.sleep(0.5)
print(CarManager.ns.carImage)
```
