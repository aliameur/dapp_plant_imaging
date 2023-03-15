# import RPi.GPIO as GPIO
import time
import gphoto2 as gp
import os

# all cameras capable of MTP, PTP or PictBridge are supported without needing to be specifically listed here.
# list available at http://www.gphoto.org/proj/libgphoto2/support.php


class Controller:

    def __init__(self):
        self.deg_per_step = 1.8
        self.delay = 0.01
        self.motor_r = ()
        self.motor_theta = ()

        # GPIO.setmode(GPIO.BCM)
        # GPIO.setwarnings(False)

        self._set_motor_r()
        self._set_motor_theta()

        self.current_pos_r = 0
        self.current_angle_theta = 0

        self.camera = gp.Camera()
        self._init_camera()

    def _set_motor_r(self):
        for pin in self.motor_r:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)

    def _set_motor_theta(self):
        for pin in self.motor_theta:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)

    def _init_camera(self):
        cameras = list(self.camera.autodetect())
        if not cameras:
            pass
        else:
            self.camera.init()

    def control_r(self, length: float):
        pass

    def control_theta(self, angle: float):
        steps = abs(int(angle / self.deg_per_step))
        direction = 1 if angle > self.current_angle_theta else 0
        for i in range(steps):
            for j, pin in enumerate(self.motor_theta):
                if (i + j) % 2 == 0:
                    GPIO.output(pin, direction)
                else:
                    GPIO.output(pin, not direction)
            time.sleep(self.delay)
        self.current_angle_theta = angle

    def manual_sequence(self, steps_r: int, step_length_r: float, steps_theta: int, step_length_theta: float):
        for i in range(steps_theta):
            for j in range(steps_r):
                if j == 0:  # take picture
                    file_path = self.camera.capture(gp.GP_CAPTURE_IMAGE)
                    camera_file = self.camera.file_get(file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
                    target = os.path.join('/tmp', file_path.name)  # TODO add file naming
                    camera_file.save(target)
                    input("Press ENTER after taking picture")

                self.control_r(step_length_r)
                input("Press ENTER after taking picture")

            self.control_r(-1 * self.current_pos_r)  # return to initial r condition
            self.control_theta(step_length_theta)

        self.control_theta(-1 * self.current_angle_theta)  # return to initial theta condition
