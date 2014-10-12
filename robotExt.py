import time
import threading
import http.server
import serial
import re
import queue

HOST_NAME = 'localhost'
PORT_NUMBER = 12345

SENSOR_SIZE = 5

waitId = -1

# sensors
from enum import Enum

#@unique
class Sensor(Enum):
    TEMP_SENSOR = 0
    DISTACE_SENSOR = 1

class Cmd(Enum):
    led = 'e'
    forward = 'f'
    backward = 'b'
    left = 'l'
    right = 'r'
    wait = 'w'

#@unique
class MoveDir(Enum):
    forward = Cmd.forward.value
    backward = Cmd.backward.value
    left = Cmd.left.value
    right = Cmd.right.value

ser=serial.Serial(baudrate=9600)
cmdQueue = queue.Queue()

class robotThread (threading.Thread):
    global SENSOR_SIZE
    
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):

        global cmdQueue
        global waitId

        def relay_cmd(param):
            if 0 == param[1]:
                print(time.asctime(), 'relay_cmd off')
                ser.write(bytearray("qw",'ascii'))
            else:
                print(time.asctime(), 'relay_cmd on')
                ser.write(bytearray("12",'ascii'))

        def led_cmd(param):
            print(time.asctime(), 'led_cmd {} {}'.format(param[1], param[2]))
            ser.write(bytearray("1{}".format(param[1]),'ascii'))

        def buzzer_cmd(param):
            print(time.asctime(), 'buzzer_cmd {} {}'.format(param[1], param[2]))
            ser.write(bytearray("2{}".format(param[1]),'ascii'))

        def move_cmd(param):
            print(time.asctime(), 'move_cmd {} {}'.format(param[1], param[2]))
            for dir in MoveDir.__members__.items():
                if dir[0] == param[1]:
                    print(time.asctime(), 'dir {}{}'.format(dir[1].value, param[2]),'ascii')
                    ser.write(bytearray("{}{}\r".format(dir[1].value, param[2]),'ascii'))
                    break

        def default_cmd(param):
            print(time.asctime(), 'default_cmd')

        commands = {
            'relay': relay_cmd,
            'led': led_cmd,
            'buzzer': buzzer_cmd,
            'move': move_cmd,
        }

        print('Starting %s' % self.name)

        ser.port = int(comPort) - 1
        ser.timeout = 5
        ser.open()

        cmdId = -1
        while True:
            sensor_status = ser.readline()
            param_list = sensor_status.split()
            print(sensor_status)
            if b's' == param_list[0]:
                # if a command was finished
                if int(param_list[1]) != cmdId:
                    if not cmdQueue.empty():
                        cmdId = int(param_list[1])
                        print('commad!!!!! %d' % cmdId)
                        params = cmdQueue.get()
                        cmd_func = commands.get(params[0], default_cmd)
                        cmd_func(params)
                    else:
                        # empty command queue - reset wait ID
                        print('reset wait')
                        waitId = -1

    def getSensor(id):
        sensors = [0]

        if len(sensors) == SENSOR_SIZE:
            return sensors[id]
        else:
            return 0
            
class MyHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(s):
    
        def poll_cmd(param):

            def getTemperature():
            #    ser.flushInput()
            #    ser.write(bytearray('T','ascii'))
            #    temp = ser.readline().decode('utf-8')
            #    print(temp)
            #    return temp
                s.wfile.write(bytes("temperature {}\n".format(robotThread.getSensor(Sensor.TEMP_SENSOR)), 'UTF-8'))
                return 22

            def getDistance():
                s.wfile.write(bytes("distance {}\n".format(robotThread.getSensor(Sensor.DISTACE_SENSOR)), 'UTF-8'))
                return 23

            def getMoveDetector():
                s.wfile.write(bytes("move_sensor {}\n".format(24), 'UTF-8'))
                return 24

            sensors = [
                getDistance,
                getTemperature,
                getMoveDetector
            ]

            #print(time.asctime(), 'poll cmd')
            s.wfile.write(bytes("\n", 'UTF-8'))
            for sens in sensors:
                sens()

            # handle waiting
            global waitId
            if waitId >= 0:
                print(time.asctime(), '_busy {}'.format(waitId))
                s.wfile.write(bytes("_busy {}\n".format(waitId), 'UTF-8'))

        global waitId

        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        s.wfile.write(bytes("<html><head><title>Title goes here.</title></head>", 'UTF-8'))
        s.wfile.write(bytes("<body><p>This is a test.</p>", 'UTF-8'))
        # If someone went to "http://something.somewhere.net/foo/bar/",
        # then s.path equals "/foo/bar/".
        s.wfile.write(bytes("<p>You accessed path: {}</p>".format(s.path), 'UTF-8'))
        params = re.findall(r'((?<=[/ ])\w+)', s.path)
        
        if params[0] == 'wait':
            print(time.asctime(), 'wait_cmd {}'.format(params[1]))
            waitId = int(params[1])
        elif params[0] == 'poll':
            print(time.asctime(), 'poll_cmd {}'.format(waitId))
            poll_cmd(params)
        else:
            global cmdQueue
            cmdQueue.put(params)

        s.wfile.write(bytes("</body></html>", 'UTF-8'))

if __name__ == '__main__':

    import sys

    comPort = 6
    if len(sys.argv) > 1:
        comPort = sys.argv[1]

    print(time.asctime(), 'Open COM port:{}'.format(comPort))

    # Create new threads
    thread1 = robotThread(1, "RobotTread", 1)
    # thread dies when main thread exits.
    thread1.daemon = True
    # Start new Threads
    thread1.start()

# for relay
#    if ser.read() != b'R':
#        print("error")
#        ser.close()
#        sys.exit(-1)

    server_class = http.server.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print(time.asctime(), 'Server Starts - {}:{}'.format(HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), 'Server Stops - {}:{}'.format(HOST_NAME, PORT_NUMBER))
    
    ser.close()
