# Python's interface for serial port communication
import serial

# Send a byte 'val' as serial input to the Arduino (assumes prior connection)
def send_arduino(connection,val):
    connection.write(val)

# Arduino communicates on COM3 @ 9600 bps
PORT = 'COM3'
SPEED = 9600

if __name__ == '__main__':
    # Establish connection with the Arduino
    connection = serial.Serial( PORT, 
                                SPEED,
                                timeout=0,
                                stopbits=serial.STOPBITS_TWO )

    # Sending byte inputs to the Arduino
    choice = 'y'
    while choice == 'y' or choice == 'n':
        choice = input("y -> LED on, n -> LED off, q -> LED on & quit: ")
        if choice == 'y':
            send_arduino(connection,b'1')
        elif choice == 'n':
            send_arduino(connection,b'0')
        elif choice == 'q':
            send_arduino(connection,b'1')
            break
        else:
            print("Undefined choice... try again.")
            choice = 'y'
            continue


    # Close the connection when done
    connection.close()
