import glob
import serial
import sys
import threading

# Setting a limit on how big serial reads can be
READ_SIZE = 1

# Arduino communicated @ 9600 BPS
SPEED = 9600

# Broadcaster loop in __main__ can set KILLALL = True when terminating
KILLALL = False

# Lock object - for avoiding races + duplicate reads
LOCK = threading.Lock()

PROMPT = ">>> "

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

# Send byte 'val' as input to all open serial ports
def send_serial(connections,val):
    for c in connections:
        c.write(val)

# Getter that returns a connection's port name
def con_name(connection):
    return str(connection).split("port=")[1].split("'")[1]

# Target thread for listening on a serial port
def listener(connection, ports):
    while KILLALL == False:
        output = connection.read(size=READ_SIZE).decode()
        LOCK.acquire()
        if len(output) > 0:
            print( ("Byte from " + con_name(connection) +
                  ": " + str(output) + "\n" + PROMPT), end="")
        else:
            pass
        LOCK.release()
    print("TERMINATING " + con_name(connection) + " LISTENER...")


# Main code
if __name__ == '__main__':

    LOCK.acquire()

    # Maintaining lists of connections, listening threads & serial ports
    CONNECTIONS = []
    LISTENERS = []
    PORTS = []

    # Populating the port and connection lists
    PORTS = make_serial_ports_list()
    for p in PORTS:
        CONNECTIONS.append( serial.Serial( p, SPEED,
                                           timeout=0,
                                           stopbits=serial.STOPBITS_ONE ) )

    # Creating listener threads for each serial port
    print("CREATING LISTENERS...")
    for c in range(len(CONNECTIONS)):
        LISTENERS.append( threading.Thread( target=listener,
                                            args=(CONNECTIONS[c],PORTS) ) )
    print("LISTENERS CREATED.")

    LOCK.release()

    # Actually starting up all the listener threads
    for l in LISTENERS:
        l.start()

    # Broadcaster loop
    print("'1' = LED on, '0' = LED off, 'Q' or 'q' = quit")
    print("BROADCASTER ONLINE. Sending to: " + str(PORTS) + "\n")
    while KILLALL == False:
        msg = ''
        while msg not in ('q','Q'):
            msg = input(PROMPT)
            LOCK.acquire()
            send_serial( CONNECTIONS, msg.encode("utf-8") )
            LOCK.release()
            if msg not in ('q','Q'):
                continue
            else:
                LOCK.acquire()
                KILLALL = True
                break

        # Killing the listeners; close all connections when done
        for c in CONNECTIONS:
            c.close()
        LOCK.release()
    
    print("PROGRAM TERMINATING.")
