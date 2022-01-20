# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming
# Access web streaming by typing this into browser: http://Your IP Address:8000

import sys
import io
import picamera
import logging
import socketserver
import threading as th
from http import server
from line_notify import LineNotify
from gpiozero import PWMLED
from time import sleep 
led = PWMLED(4,active_high=True,initial_value=0,frequency=2400,pin_factory=None)
          
img_n = 0

ACCESS_TOKEN = "LnE4GiXqQdhgd36RxzQqZh4lfTgENLyEAja6arMpQjw"
notify = LineNotify(ACCESS_TOKEN)

PAGE="""\
<html>
<head>
<title>MECHA - Raspberry Pi Microscope</title>
</head>
<body>
<center><h1>MECHA - Raspberry Pi Microscope</h1></center>
<center><img src="stream.mjpg" width="1280" height="960"></center>
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = th.Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True
    
def key_capture_thread():
    while 1 :
        k = input("please enter 'led' to change LED value or 'c' to capture \n")
        if k == 'c':
            print('c')
            global img_n
            img_n += 1
            image_path = '/home/pi/Desktop/Mecha/Capture_Serve/img' + str(img_n) + '.jpg'
            camera.capture(image_path)
            notify.send("Captured from Pi_microscope", image_path)
        elif k == 'led':
            val = float(input("please enter LED value between 0.0-1.0 : "))
            led.value = val
            sleep(0.5)
        else:
            print('out of context')


with picamera.PiCamera(resolution='2560x1920', framerate=24) as camera:
    th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
    output = StreamingOutput()
    camera.rotation = 90
    camera.start_recording(output, format='mjpeg')
    
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        camera.stop_recording()
        sys.exit()
