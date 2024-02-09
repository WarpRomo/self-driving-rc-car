
<h1>Documentation</h1>
<p><b>CarController</b>(ip=string, image_rate=float, image_downsample=int, control_rate=float)</p>
<p>ip(required)<br>The IP of the car's server to connect to, example: ip="http://127.0.0.1:5000"</p>
<p>image_rate<br>The interval at which to fetch the image from the camera of the car, set to -1 to fetch nothing at all, example: image_rate=0.1</p>
<p>image_downsample<br>The amount to scale down the image the car sends from the image fetch, higher is faster, example: image_downsample=10</p>
<p>control_rate<br>The interval at which to send car inputs to the car's server, example: control_rate=0.1</p>
Note: For image_rate and control_rate, do not use too low of a value or the server will become flooded. Recommended is 0.1 for both.
