
<h1>Documentation</h1>
<p><b>CarController</b>(ip=string, image_rate=float, image_downsample=int, control_rate=float)</p>
<p>ip(required)<br>The IP of the car's server to connect to, example: ip="http://127.0.0.1:5000"</p>
<p>image_rate<br>The interval at which to fetch the image from the camera of the car, set to -1 to fetch nothing at all, example: image_rate=0.1</p>
<p>image_downsample<br>The amount to scale down the image the car sends from the image fetch, higher is faster, example: image_downsample=10</p>
<p>control_rate<br>The interval at which to send car inputs to the car's server, example: control_rate=0.1</p>
Note: For image_rate and control_rate, do not use too low of a value or the server will become flooded. Recommended is 0.1 for both.
<p><b>CarController.turn(value=float)</b></p>
<p>value(required)<br>The direciton that the wheels should be set to. -1 is left, 1 is right, keep the value between -1 and 1, example: value=0.7</p>
<p><b>CarController.speed(value=float)</b></p>
<p>value(required)<br>The speed that the wheels should turn -1 is backwrads, 1 is forwards, keep the value between -1 and 1 and low, example: value=-0.3</p>
<p><b>CarController.ns.carImage (nd.array)</b></p>
<p>An RGB array containing the most recently fetched image from the car.</p>
