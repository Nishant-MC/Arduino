// All code adapted from http://tldp.org/HOWTO/Serial-Programming-HOWTO/x115.html
// This is a canonical input processor

// Not sure what all these are for
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <termios.h>
#include <stdio.h>

// For exit()
#include <stdlib.h>
// For bzero()
#include <strings.h>
// For read()
#include <unistd.h>

// Not sure how important setting baudrate is...
// For now, matching Arduino standard
#define BAUDRATE 9600            

// Change MODEMDEVICE to the port you want to listen on (must already exist)
// UNIX-style serial ports are all prefixed with /dev/tty
#define MODEMDEVICE "/dev/ttyS5"
#define _POSIX_SOURCE 1

// True & False constants
#define FALSE 0
#define TRUE 1

// Controls whether our "port" is on / off
volatile int STOP = FALSE; 

int main()
{
	int fd,c, res;
	struct termios oldtio,newtio;
	char buf[255];

	/* 
	  Open modem device for reading and writing and not as controlling tty
      because we don't want to get killed if linenoise sends CTRL-C.
    */
 
	fd = open(MODEMDEVICE, O_RDWR | O_NOCTTY ); 
	if (fd <0) {perror(MODEMDEVICE); exit(-1); }

	tcgetattr(fd,&oldtio); // Save current serial port settings
	bzero(&newtio, sizeof(newtio)); // Clear struct for new port settings

	/* 
	  BAUDRATE: Set bps rate. 
	  CRTSCTS : Output hardware flow control (See sect. 7 of Serial-HOWTO)
	  CS8     : 8n1 (8 bit, no parity, 1 stopbit)
	  CLOCAL  : Local connection, no modem control
	  CREAD   : Enable receiving characters
	*/
	newtio.c_cflag = BAUDRATE | CRTSCTS | CS8 | CLOCAL | CREAD;
 
	/*
	  IGNPAR  : Ignore bytes with parity errors
	  ICRNL   : Map CR to NL (otherwise a CR input on the other computer
				will not terminate input)
	  Otherwise make device raw (no other input processing)
	*/
	newtio.c_iflag = IGNPAR | ICRNL;
 
	// Raw output
	newtio.c_oflag = 0;
	 
	/*
	  ICANON  : enable canonical input
	  Disable all echo functionality, and don't send signals to the calling program
	*/
	newtio.c_lflag = ICANON;
 
	/* 
	  Initialize all control characters 
	  Default values can be found in /usr/include/termios.h
	*/
	newtio.c_cc[VINTR]    = 0;     /* Ctrl-c */ 
	newtio.c_cc[VQUIT]    = 0;     /* Ctrl-\ */
	newtio.c_cc[VERASE]   = 0;     /* del */
	newtio.c_cc[VKILL]    = 0;     /* @ */
	newtio.c_cc[VEOF]     = 4;     /* Ctrl-d */
	newtio.c_cc[VTIME]    = 0;     /* inter-character timer unused */
	newtio.c_cc[VMIN]     = 1;     /* blocking read until 1 character arrives */
	newtio.c_cc[VSWTC]    = 0;     /* '\0' */
	newtio.c_cc[VSTART]   = 0;     /* Ctrl-q */ 
	newtio.c_cc[VSTOP]    = 0;     /* Ctrl-s */
	newtio.c_cc[VSUSP]    = 0;     /* Ctrl-z */
	newtio.c_cc[VEOL]     = 0;     /* '\0' */
	newtio.c_cc[VREPRINT] = 0;     /* Ctrl-r */
	newtio.c_cc[VDISCARD] = 0;     /* Ctrl-u */
	newtio.c_cc[VWERASE]  = 0;     /* Ctrl-w */
	newtio.c_cc[VLNEXT]   = 0;     /* Ctrl-v */
	newtio.c_cc[VEOL2]    = 0;     /* '\0' */

	// Now clean the modem line and activate the settings for the port
	tcflush(fd, TCIFLUSH);
	tcsetattr(fd,TCSANOW,&newtio);

	// Terminal settings done, now handle input
	while (STOP==FALSE) {
	 /* Read blocks program execution until a line terminating character is 
		input, even if more than 255 chars are input. If the number
		of characters read is smaller than the number of chars available,
		subsequent reads will return the remaining chars. res will be set
		to the actual number of characters actually read 
	 */
		res = read(fd,buf,255); 
		buf[res]=0;             // Set end of string for printf()
		printf("Byte(s) received: %s", buf);
		
		if (  (buf[0]=='1') &&(buf[1]==0) ) {
			printf(" | LED on request...\n");
		}
		else if (  (buf[0]=='0') &&(buf[1]==0) ) {
			printf(" | LED off request...\n");
		}
		else if ( ( (buf[0]=='Q')||(buf[0]=='q') )&&(buf[1]==0) ) {
			STOP=TRUE;
			printf(" | Quit request... Program terminating.\n");
		}
		else { 
			printf(" | Unknown command... Doing nothing.\n");
		}
	}
	
	// Restore the old port settings after we're done
	tcsetattr(fd,TCSANOW,&oldtio);	
}