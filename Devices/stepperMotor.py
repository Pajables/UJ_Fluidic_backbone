from Devices.device import Device
import time


class StepperMotor(Device):
    """
    Class for managing stepper motors
    """
    def __init__(self, stepper_obj, motor_en_obj, device_config, s_lock):
        """
        :param stepper_obj: commanduino object for controlling the stepper motor
        :param motor_en_obj: commandduino object for toggling the enable pin with digitalWrite
        :param device_config: Dictionary containing the configuration information for the motor.
        """
        super(StepperMotor, self).__init__(motor_en_obj, s_lock)
        self.serial_lock = s_lock
        self.cmd_stepper = stepper_obj
        self.steps_per_rev = device_config['steps_per_rev']
        self.enabled_acceleration = device_config['enabled_acceleration']
        self.running_speed = device_config['speed']
        self.max_speed = device_config['max_speed']
        self.acceleration = device_config["acceleration"]
        self.reversed_direction = False
        self.position = 0
        self.stopped = False
        self.en_motor()

    def en_motor(self, en=False):
        if en:
            self.digital_write(0)
        else:
            self.digital_write(1)

    def enable_acceleration(self, enable=True):
        with self.serial_lock:
            if enable:
                self.cmd_stepper.enable_acceleration()
                self.enabled_acceleration = True
            else:
                self.cmd_stepper.disable_acceleration()
                self.enabled_acceleration = False

    def set_acceleration(self, acceleration):
        if type(acceleration) is int and acceleration > 0:
            with self.serial_lock:
                self.cmd_stepper.set_acceleration(acceleration)
            self.acceleration = acceleration
            return True
        else:
            print("That is not a valid acceleration")
            return False

    def set_running_speed(self, speed):
        if type(speed) is int and speed > 0:
            with self.serial_lock:
                self.cmd_stepper.set_running_speed(speed)
            self.running_speed = speed
            return True
        else:
            print("That is not a valid running speed")
            return False

    def set_max_speed(self, speed):
        if type(speed) is int and speed > 0:
            with self.serial_lock:
                self.cmd_stepper.set_max_speed(speed)
            self.max_speed = speed
            return True
        else:
            print("That is not a valid max speed")
            return False

    def reverse_direction(self, reverse):
        """
        :param reverse: True - clockwise, False, anticlockwise
        :return:
        """
        if reverse != self.reversed_direction:
            with self.serial_lock:
                self.cmd_stepper.revert_direction(reverse)
            self.reversed_direction = reverse

    def get_current_position(self):
        with self.serial_lock:
            self.position = self.cmd_stepper.get_current_position()
        return self.position

    def set_current_position(self, position):
        with self.serial_lock:
            self.cmd_stepper.set_current_position(position)
        self.position = position

    def move_steps(self, steps):
        self.stopped = False
        self.en_motor(True)
        with self.serial_lock:
            self.cmd_stepper.move(steps)
        self.watch_move()
        return True

    def move_to(self, position):
        self.stopped = False
        self.en_motor(True)
        with self.serial_lock:
            self.cmd_stepper.move_to(position)
        self.watch_move()
        return True

    def stop(self):
        with self.serial_lock:
            self.cmd_stepper.stop()
            self.stopped = True

    def watch_move(self):
        moving = True
        while moving:
            if not self.is_moving:
                moving = False
            time.sleep(1)
        self.en_motor()

    @property
    def is_moving(self):
        with self.serial_lock:
            moving = self.cmd_stepper.is_moving
        return moving


class LinearStepperMotor(StepperMotor):
    def __init__(self, stepper_obj, motor_en_obj, device_config, s_lock):
        super(LinearStepperMotor, self).__init__(stepper_obj, motor_en_obj, device_config, s_lock)
        self.switch_state = 0

    def check_endstop(self):
        with self.serial_lock:
            self.switch_state = self.cmd_stepper.get_switch_state()
        return self.switch_state

    def home(self):
        self.cmd_stepper.set_homing_speed(6400)
        with self.serial_lock:
            self.cmd_stepper.home(False)
        self.watch_move()
        self.set_running_speed(self.running_speed)
