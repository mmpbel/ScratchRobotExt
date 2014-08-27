import time
import http.server
import serial
import re

'''
        if params[0]=='poll':
            print(time.asctime(), 'poll cmd', getTemperature())
            s.wfile.write(bytes("\n", 'UTF-8'))
            s.wfile.write(bytes("temperature {}\n".format(getTemperature()), 'UTF-8'))
            s.wfile.write(bytes("distance {}\n".format(getDistance()), 'UTF-8'))
            s.wfile.write(bytes("move_sensor {}\n".format(getMoveDetector()), 'UTF-8'))
        elif params[0]=='turnOn':
            print(time.asctime(), 'turnOn cmd')
            ser.write(bytearray("12",'ascii'))
        elif params[0]=='turnOff':
            print(time.asctime(), 'turnOff cmd')
            ser.write(bytearray("qw",'ascii'))
'''

HOST_NAME = 'localhost'
PORT_NUMBER = 12345

ser=serial.Serial()

class MyHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(s):
    
        def poll_cmd(param):
            
            def getTemperature():
            #    ser.flushInput()
            #    ser.write(bytearray('T','ascii'))
            #    temp = ser.readline().decode('utf-8')
            #    print(temp)
            #    return temp
                s.wfile.write(bytes("temperature {}\n".format(25), 'UTF-8'))
                return 22

            def getDistance():
                s.wfile.write(bytes("distance {}\n".format(23), 'UTF-8'))
                return 23

            def getMoveDetector():
                s.wfile.write(bytes("move_sensor {}\n".format(24), 'UTF-8'))
                return 24

            sensors = [
                getDistance,
                getTemperature,
                getMoveDetector
            ]

            print(time.asctime(), 'poll cmd')
            s.wfile.write(bytes("\n", 'UTF-8'))
            for sens in sensors:
                sens()

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
            print(time.asctime(), 'move_cmd')
            ser.write(bytearray("3{}".format(param[1]),'ascii'))

        def default_cmd(param):
            print(time.asctime(), 'default_cmd')

        commands = {
            'poll': poll_cmd,
            'relay': relay_cmd,
            'led': led_cmd,
            'buzzer': buzzer_cmd,
            'move': move_cmd,
        }

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
        
        cmd_func = commands.get(params[0], default_cmd)
        cmd_func(params)

        s.wfile.write(bytes("</body></html>", 'UTF-8'))

if __name__ == '__main__':
    comPort = 2
    ser.port = int(comPort)
    ser.timeout = 5
    ser.open()
    ser.write(bytearray("'",'ascii'))
    print(time.asctime(), 'Open COM port:{}'.format(comPort+1))

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
