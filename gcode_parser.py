import math
import _thread
import time


class NeggxtBotGCodeParser:

    def __init__(self, rotation_motor, moving_motor, pulling_motor, egg_height=3.5, egg_width=4.5, full_rotation=1200, max_movement=200, max_pull_height=400, fast_pull_height=300):
        self.m_x = rotation_motor
        self.m_y = moving_motor
        self.m_pull = pulling_motor
        self.egg_height = egg_height
        self.egg_width = egg_width
        self.full_rotation = full_rotation
        self.max_movement = max_movement
        self.max_pull_height = max_pull_height
        self.fast_pull_height = fast_pull_height
        self.x = 0
        self.y = 0
        self.sets = {'G': 0.0, 'X': 0.0, 'Y': 0.0, 'F': 1.0}
        self.codes = {
            '0': self.g_0,
            '1': self.g_1
        }

    def g_0(self, args):
        old_movment = self.sets['G']
        if old_movment == 1:
            self.pen_up()
        self.update(args)
        self.move()

    def g_1(self, args):
        old_movment = self.sets['G']
        if old_movment == 0:
            self.pen_down()
        self.update(args)
        self.move()

    # moves the pen to the (new) posision in self.sets
    def move(self):
        # important! make sure the Y coordinate is in the drawable area
        if self.sets['Y'] > self.egg_height or self.sets['Y'] < 0:
            raise GCodeParseError('Y Coordinate out of drawable Area')
        else:
            delta_x = self.sets['X'] - self.x
            self.x += delta_x

            delta_y = self.sets['Y'] - self.y
            self.y += delta_y

            print('I am moving! deltaX: %s, deltaY: %s' % (delta_x, delta_y))
            self.dual_move(delta_x, delta_y)

    def dual_move(self, delta_x, delta_y):
        tacho_x = self.rotation_by_x(abs(delta_x))
        tacho_y = self.movment_by_y(abs(delta_y))

        if delta_x != 0 and delta_y != 0:
            # which one needs more power? the more power you need to drive one tacho degree in a second (=the harder) and the more tacho degrees you have to drive the more power you need -> this larger power is limited to self.sets['F']
            if self.m_x_func.power_per_time() * tacho_x > self.m_y_func.power_per_time() * tacho_y:
                power_x = self.sets['F']
                power_y = self.m_y_func.calc_power_by_tacho(tacho_x, tacho_y, power_x)
            else:
                power_y = self.sets['F']
                power_x = self.m_x_func.calc_power_by_tacho(tacho_y, tacho_x, power_y)

            power_x = int(power_x * int(delta_x) / abs(delta_x))
            power_y = int(power_y * int(delta_y) / abs(delta_y))

            #power the motors simultaneously
            _thread.start_new_thread(self.turn_motor, (self.m_x, power_x, tacho_x))
            _thread.start_new_thread(self.turn_motor, (self.m_y, power_y, tacho_y))

        else:
            if delta_x != 0:
                # turn m_x with maximum power
                self.m_x.turn(int(self.sets['F'] * int(delta_x) / abs(delta_x)), abs(tacho_x))
            if delta_y != 0:
                self.m_y.turn(int(self.sets['F'] * int(delta_y) / abs(delta_y)), abs(tacho_y))

    def turn_motor(self, motor, power, tacho):
        print('power: ' + str(power) + ' tacho: ' + str(tacho))
        motor.turn(power, tacho)

    # returns the tacho degrees the motor has to rotate to draw delta_x cm. The egg is estimated as a cylinder with a constant radius egg_width
    def rotation_by_x(self, delta_x):
        return delta_x / (math.pi * self.egg_width) * self.full_rotation

    # returns the tacho degrees the motor has to move to draw delta_y cm
    def movment_by_y(self, delta_y):
        return delta_y / self.egg_height * self.max_movement

    # excecute a GCode command
    def exec(self, cmd):
        self.parse(cmd)

    # Only called with G0 or G1! Update all the sets with the new values from the arguments. Not appearing values are being kept.
    def update(self, args):
        for arg in args:
            code = arg[0]
            if code in self.sets:
                # update the set with the following value converted to float if the name is valid (meaning contained in the initial sets)
                self.sets[code] = float(arg[1:])
            else:
                raise GCodeParseError('Unknown argument name: %s' % code)

    def parse(self, cmd):
        # split arguments after space
        args = cmd.split()

        # GCode
        if args[0][0] == 'G':
            # the code is the remaining of the first argument without the G
            code = args[0][1:]

            # is there a code after the G
            if len(code) == 0:
                raise GCodeParseError('No code after G')
            else:

                def parse_exception(args):
                    raise GCodeParseError('No action for code G%s' % code)

                # select the corresponding action for the code, if not found raise an error
                code_function = self.codes.get(code, parse_exception)
                # execute the function and pass all the args
                code_function(args)
        else:
            raise GCodeParseError('No other commands than G accepted')

    # move the pen down to start drawing
    def pen_down(self):
        self.m_pull.turn(-30, self.max_pull_height)

    # move the pen up to stop drawing
    def pen_up(self):
        self.m_pull.turn(30, self.max_pull_height)

    # finds out the power the motors need to move in a certain time and calculates the parameters of the exponential function
    def calibrate(self):
        times = []
        powers = [30, 60, 120]
        for power in powers:
            # m_y
            start_time = time.time()
            self.m_y.turn(power, self.max_movement)
            self.m_y.turn(power * -1, self.max_movement)
            delta_time_y = time.time() - start_time

            # m_x
            start_time = time.time()
            self.m_x.turn(power, self.full_rotation)
            self.m_x.turn(power * -1, self.full_rotation)
            delta_time_x = time.time() - start_time

            # scale for 1 tacho degree
            times.append((delta_time_x / self.full_rotation, delta_time_y / self.max_movement))
        # pass the corresponding (power, time) tuples to the function generator
        self.m_x_func = MotorExpFunction([(powers[0], times[0][0]), (powers[1], times[1][0]), (powers[2], times[2][0])])
        self.m_y_func = MotorExpFunction([(powers[0], times[0][1]), (powers[1], times[1][1]), (powers[2], times[2][1])])

class MotorExpFunction():

    # powertimes: list of three (power, time) tuples
    def __init__(self, powertimes):
        self.powertimes = powertimes
        # the offset in time of the function is the time it took for the largest power
        self.n = powertimes[-1][1]
        # Exponential function: t = m * a^p + n
        # (I)   t_1 = m * a^p_1 + n
        # (II)   t_2 = m * a^p_2 + n
        # (t_1 - n) / a^p_1 = (t_2 - n) / a^p_2
        # (t_1 - n) / (t_2 - n) = a^p_1 / a^p_2
        # (t_1 - n) / (t_2 - n) = a^(p_1 - p_2)
        # a = ((t_1 - n) / (t_2 - n))^(1/(p_1 - p_2))
        self.a = math.pow((powertimes[0][1] - self.n) / (powertimes[1][1] - self.n), 1/(powertimes[0][0] - powertimes[1][0]))
        # m = (t_1 - n) / (a^p_1)
        self.m = (powertimes[0][1] - self.n) / math.pow(self.a, powertimes[0][0])

    # power to drive one tacho degree in one second
    def power_per_time(self):
        return math.log((1 - self.n) / self.m, self.a)

    def calc_power_by_tacho(self, tacho_1, tacho_2, power_1):
        return math.log(((self.m * math.pow(self.a, power_1) + self.n) * tacho_1 / tacho_2 - self.n) / self.n, self.a)

class GCodeParseError(Exception):
    pass
