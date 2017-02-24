import serial as s
import time as t

class Finnpipette():

    def __init__(self, min_volume=5, max_volume=50):
        self.serial = s.Serial(port='/dev/cu.usbmodem1411', baudrate=9600)
        self.terminator = '\n'
        self.min_volume = min_volume
        self.max_volume = max_volume
        self.precision = 0.1 # ul
        self.volume = self.max_volume
        
        self.init()

    def init(self):
        t.sleep(2.5)
        self.on()
        t.sleep(1)
        self.trigger()
        t.sleep(1)
        self.home(True)
        self.state = 0 # 0==dispensed, 1==aspirated

    def cmd(self, cmd_string, block=True):
        cmd_string = cmd_string + self.terminator
        self.serial.write(cmd_string)
        
        # wait for response
        while self.serial.inWaiting()==0:
            pass
        t.sleep(0.8)

        return self.serial.read(self.serial.inWaiting())

    def on(self):
        self.cmd('i')
    def off(self):
        self.cmd('o')
    
    def exit(self):
        self.off()
        self.serial.close()

    def home(self, hard_home=False):
        # self.cmd('Z')
        if hard_home:
            self.up(self.max_volume)
        else:
            self.up(self.max_volume - self.volume + 4)
        self.right()
        self.volume = self.max_volume


    def down(self, d_vol=-1):
        if d_vol < 0:
            self.cmd('d')
            self.volume -= self.precision
        else:
            self.cmd('D,{}'.format(d_vol))
            self.volume -= (self.precision + d_vol)

    def up(self, d_vol=-1):
        if d_vol < 0:
            self.cmd('u')
            self.volume += self.precision
        else:
            self.cmd('U,{}'.format(d_vol))
            self.volume += (self.precision + d_vol)
            

    def right(self):
        self.cmd('r')

    def trigger(self):
        self.cmd('t')

    # TODO: consider minimum case
    def set_volume(self, volume):
        volume = round(volume, 1)
        if volume == self.volume:
            pass
        else:
            self.home()
            d_vol = self.max_volume - volume

            if d_vol < 1:
                n = round(int(d_vol/self.precision), 1)
                for i in xrange(n):
                    self.down()
            else:
                self.down(d_vol)
                self.up()

            self.right()

    def asp_disp(self, volume = None, rate = 1.0):
        if volume == None:
            volume = self.volume
        self.set_volume(volume)
        self.trigger()
        self.state = (self.state + 1)%2


    def set_speed(self, **kwargs):
        """
        Set the speed (mm/minute) the :any:`Pipette` plunger will move
        during :meth:`aspirate` and :meth:`dispense`

        Parameters
        ----------
        kwargs: Dict
            A dictionary who's keys are either "aspirate" or "dispense",
            and who's values are int or float (Example: `{"aspirate": 300}`)
        """
        keys = {'aspirate', 'dispense'} & kwargs.keys()
        for key in keys:
            self.speeds[key] = kwargs.get(key)
        return self



