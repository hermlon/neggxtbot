import math
import _thread
import time


class NeggxtBotGCodeParser:

    def __init__(self, rotation_motor, moving_motor, pulling_motor, egg_height=100, egg_width=128.5, full_rotation=1200, max_movement=200, max_pull_height=400, fast_pull_height=300,
        t_p_1=(105, 120, 0.0044429075150262745),
        t_p_2=(25, 120, 0.013160743713378907),
        p_p_1=(195, 40, 0.003705470378582294),
        p_p_2=(195, 20, 0.005971569281357985),
        n=0.0029973720892881735):
        self.m_x = rotation_motor
        self.m_y = moving_motor
        self.m_pull = pulling_motor
        self.egg_height = egg_height
        self.egg_width = egg_width
        self.full_rotation = full_rotation
        self.max_movement = max_movement
        self.max_pull_height = max_pull_height
        self.fast_pull_height = fast_pull_height
        self.m_func = MotorExpFunction(t_p_1, t_p_2, p_p_1, p_p_2, n)
        self.x = 0
        self.y = 0
        self.is_pen_down = False
        self.relative = False
        self.sets = {'X': 0.0, 'Y': 0.0, 'F': 30.0}
        self.codes = {
            '0': self.g_0,
            '1': self.g_1,
            '90': self.set_absolut,
            '91': self.set_relative
        }

    def g_0(self, args):
        self.pen_up()
        self.update(args)
        self.move()

    def g_1(self, args):
        self.pen_down()
        self.update(args)
        self.move()

    def set_absolut(self, args):
        self.relative = False

    def set_relative(self, args):
        self.relative = True

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
            # which one needs more power? the one who has to move further! abs: movment doesn't care about the direction!!!
            if abs(tacho_x) > abs(tacho_y):
                power_x = self.sets['F']
                power_y = self.m_func.calc_power_by_tacho(tacho_x, tacho_y, power_x)
            else:
                power_y = self.sets['F']
                power_x = self.m_func.calc_power_by_tacho(tacho_y, tacho_x, power_y)

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
        #motor.turn(30, 30)

    # returns the tacho degrees the motor has to rotate to draw delta_x cm. The egg is estimated as a cylinder with a constant radius egg_width
    def rotation_by_x(self, delta_x):
        return delta_x / (math.pi * self.egg_width) * self.full_rotation

    # returns the tacho degrees the motor has to move to draw delta_y cm
    def movment_by_y(self, delta_y):
        return delta_y / self.egg_height * self.max_movement

    def exec_file(self, filename):
        print('Loading file: %s' % filename)
        starttime = time.time()
        with open(filename, 'r') as file:
            for line in file:
                self.exec(line)

        # move to initial position
        self.pen_up()
        self.exec('G90')
        self.exec('G0 X0')
        self.exec('G0 Y0')
        print('Finished drawing. Time: %s min' % str(int((time.time() - starttime) / 60)))

    # excecute a GCode command
    def exec(self, cmd):
        self.parse(cmd)

    # Only called with G0 or G1! Update all the sets with the new values from the arguments. Not appearing values are being kept.
    def update(self, args):
        for arg in args:
            # ok, we accept lazy GCode writers...
            arg_name = arg[0].upper()
            if arg_name in self.sets:
                if self.relative:
                    # relative movment means values are added to the previous value
                    self.sets[arg_name] += float(arg[1:])
                else:
                    # update the set with the following value converted to float if the name is valid (meaning contained in the initial sets)
                    self.sets[arg_name] = float(arg[1:])
            else:
                raise GCodeParseError('Unknown argument name: %s' % arg_name)

    def parse(self, cmd):
        # split arguments after space
        args = cmd.split()

        # GCode (we accept g)
        if args[0][0].upper() == 'G':
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
                # execute the function and pass all the args except G
                code_function(args[1:])
        # Do nothing, could be comment or unknown command

    # move the pen down to start drawing
    def pen_down(self):
        if not self.is_pen_down:
            self.m_pull.turn(-30, self.max_pull_height)
            self.is_pen_down = True

    # move the pen up to stop drawing
    def pen_up(self):
        if self.is_pen_down:
            self.m_pull.turn(30, self.max_pull_height)
            self.is_pen_down = False

    # finds out the power the motors need to move in a certain time and calculates the parameters of the exponential function
    def calibrate(self):
        # TODO: Update to new method!
        pass
        """
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
            times.append((delta_time_x / self.full_rotation / 2, delta_time_y / self.max_movement / 2))
        # pass the corresponding (power, time) tuples to the function generator
        self.m_x_func = MotorExpFunction([(powers[0], times[0][0]), (powers[1], times[1][0]), (powers[2], times[2][0])])
        self.m_y_func = MotorExpFunction([(powers[0], times[0][1]), (powers[1], times[1][1]), (powers[2], times[2][1])])
        """

    def reset_movment(self):
        self.m_y.weak_turn(-60, self.max_movement)
        self.m_y.idle()

class MotorExpFunction():

    # (tacho, power, time)
    def __init__(self, tp_1, tp_2, pp_1, pp_2, n):
        self.n = n
        self.a, self.b = self.calc_params((tp_1[2], tp_1[0]), (tp_2[2], tp_2[0]))
        self.c, self.d = self.calc_params((pp_1[2], pp_1[1]), (pp_2[2], pp_2[1]))

    def calc_params(self, p_1, p_2):
        b = math.pow((p_1[0] - self.n) / (p_2[0] - self.n), 1 / (p_1[1] - p_2[1]))
        a = (p_1[0] - self.n) / math.pow(b, p_1[1])
        return (a, b)

    def calc_time(self, tacho, power):
        return self.a * math.pow(self.b, tacho) + self.c * math.pow(self.d, power) + self.n

    # don't know why but when I switch tacho_1 and tacho_2 it seems to work. Must have messed up somewhere
    def calc_power_by_tacho(self, tacho_2, tacho_1, power_1):
        # import pdb; pdb.set_trace()
        #try:
        return math.log((self.a * math.pow(self.b, tacho_1) + self.c * math.pow(self.d, power_1) - self.a * math.pow(self.b, tacho_2)) / self.c, self.d)
        #except:
        #    return -1

class GCodeParseError(Exception):
    pass
