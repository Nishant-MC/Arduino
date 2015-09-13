import glob
import serial
import sys


# Creates a list of all serial ports to broadcast to (cross-platform)
def make_serial_ports_list():
    
    # On Windows, serial ports start with the prefix "COM"
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]

    # On Linux / Cygwin, serial ports start with the prefix /dev/tty    
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
        
    # Don't know how to work with OSX / other OS types as of now
    else:
        raise EnvironmentError('Unsupported platform / OS')

    # Try connecting to ports; any open ones are appended to the result
    # All closed/invalid ports are left alone
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
        
    return result

# Send byte 'val' as input to all serial ports (assumes prior connections)
def send_serial(connections,val):
    for c in connections:
        c.write(val)

# Main code
if __name__ == '__main__':

    # Make all connections @ 9600 bps (Arduino emulation)
    CONNECTIONS = []
    PORTS = make_serial_ports_list()
    SPEED = 9600

    for PORT in PORTS:
        CONNECTIONS.append( serial.Serial( PORT, SPEED,
                                           timeout=0,
                                           stopbits=serial.STOPBITS_ONE ) )

    print("Broadcasting to ports: ", PORTS)

    # Sending byte inputs to available serial ports
    msg = ''
    while msg.lower() != 'q':
        msg = input("Enter byte to send (1 = LED on, 0 = LED off, q or Q = quit): ")
        send_serial(CONNECTIONS, msg.encode("utf-8") )
        if msg.lower() != 'q':
            continue
        else:
            break

    # Close the connections when done
    for c in CONNECTIONS:
        c.close()
