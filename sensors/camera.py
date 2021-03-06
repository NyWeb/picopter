import threading
import picamera
import time
import os

class camera(threading.Thread):
    action = ""
    busy = False

    resolution = {
        "video": {
            "w": 1920,
            "h": 1080,
            "fps": 30
        },
        "slowmotion": {
            "w": 640,
            "h": 480,
            "fps": 90
        },
        "photo": {
            "w": 2592,
            "h": 1944,
            "fps": 1
        },
        "": {
            "w": 200,
            "h": 120,
            "fps": 30
        }
    }

    path = "/var/www/html/photos/"

    error = False

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

        try:
            self.camera = picamera.PiCamera()
            self.camera.vflip = True;

        except picamera.exc.PiCameraError:
            self.error = "ioerror initialize"
            return

    def run(self):
        if(self.camera):
            self.camera.start_preview()
        while self.camera:
            try:
                if(self.busy):
                    if(self.action==""):
                        self.camera.stop_recording()
                        self.busy = False
                        print "stop"
                    else:
                        time.sleep(.1)
                else:
                    self.camera.resolution = (self.resolution[self.action]["w"], self.resolution[self.action]["h"])
                    self.camera.framerate = self.resolution[self.action]["fps"]

                    if self.action=="photo":
                        self.camera.capture(self.path+str(int(time.time()))+".jpg", format='jpeg', use_video_port=True)
                        self.action = ""

                    elif self.action=="slowmotion" or self.action=="video":
                        self.busy = True
                        print "start"
                        self.camera.start_recording(self.path+str(int(time.time()))+".h264")

                    else:
                        i = 0
                        timer = 0
                        for key in self.camera.capture_continuous("/var/www/html/tmp/loading.jpg", format='jpeg', use_video_port=True):
                            image = "/var/www/html/tmp/image"+str(i)+".jpg"
                            os.rename(key, image)
                            i += 1

                            if(i==2):
                                i = 0

                            if(self.action):
                                break

            except IOError:
                self.error = "ioerror"
                print "no-camera"

    def read(self):
        return False

    def cancel(self, motors):
        return False