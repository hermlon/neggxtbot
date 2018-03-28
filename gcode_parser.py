class NeggxtBotGCodeParser:



    def __init__(self, rotation_motor, moving_motor, pulling_motor, full_rotation=1200, max_movement=240, max_pull_height=400, fast_pull_height=300):
        self.m_x = rotation_motor
        self.m_y = moving_motor
        self.m_pull = pulling_motor
        self.full_rotation = full_rotation
        self.max_movement = max_movement
        self.max_pull_height = max_pull_height
        self.fast_pull_height = fast_pull_height
        self.sets = {'G': 0.0, 'X': 0.0, 'Y': 0.0, 'F': 1.0}
        self.codes = {
            '0': self.g_0,
            '1': self.g_1
        }

    def g_0(self, args):
        old_movment = self.sets['G']
        if old_movement == 1:
            pen_up()
        self.update(args)

    def g_1(self, args):
        old_movment = self.sets['G']
        if old_movement == 0:
            pen_down()
        self.update(args)

    def move(self):
        pass

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
                # execute the function and pass all the remaining args
                code_function(args[1:])
        else:
            raise GCodeParseError('No other commands than G accepted')

class GCodeParseError(Exception):
    pass
