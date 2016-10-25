import serial
import time
import numpy as np

class Scope:
    """Object modeling the oszilloscope

    Working example:
#####
import numpy as np
import matplotlib.pyplot as plt
import scope

myscope=scope.Scope("COM1")

x,data=myscope.readScope()

plt.plot(x,data)
plt.show()
#####
    """

    def __init__(self,port, baudrate=9600, debug=False):
        """Create the scope object with given parameters

        Arguments:
        port - the com port to be used, eg "COM1"

        Keyword arguments:
        baudrate - serial baudrate that is used (default: 9600)
        debug - switch the command line output
        """

        # store variables in object
        self.port=port
        self.debug=debug

        #create serial connection
        self.com = serial.Serial(port=port, baudrate=baudrate)


    def readScope(self, channel="CH1"):
        """Read the data from scope without changing settings

        Keyword arguments:
        channel - channel to be read (default: "CH1")
        """

        # check for open connection
        if not self.com.isOpen():
            self.com.open()

        # catch possible exceptions
        try:
            # select channel
            self.com.write("DAT:SOU "+channel+'\r\n')
            # set encoding
            self.com.write("DAT:ENC RIB"+'\r\n')
            # set the byte with (2: 0 to 65,535 )
            self.com.write("DAT:WID 2"+'\r\n')
            # set the starting point for aquisition
            ## should this be 0?
            self.com.write("DAT:STAR 1"+'\r\n')
            # set the end point
            self.com.write("DAT:STOP 2500"+'\r\n')

            # collect oszi settings for the waveform
            # with this the real axis can be obtained
            self.com.write("WFMPRe?"+'\r\n')
            #time.sleep(1)
            out = ''
            #read until the message is complete. "\r\n" signalizes THE END
            while self.com.inWaiting()>0 or not "\r\n" in out[-2:]:
                # collect all returned data
                out += self.com.read(self.com.inWaiting())
                #time.sleep(0.5)
                time.sleep(0.1) #sleep 100ms to wait for further bytes
    
            ## debug raw scope parameters
            if self.debug: print out
    
            # split the given string for single parameters
            out = out[1:].split(";")
    
            # store the parameters as dictionary
            params = {}
            for s in out:
                d = s.split(" ")
                params[d[0]] = d[1]
                ## debug formated parameters
                if self.debug: print str(d[0])+"\t"+str(d[1])
    
            # get the data
            self.com.write("CURV?"+'\r\n')
    
            ## debug for time measurement
            if self.debug: t0 = time.time()
    
            # why do i need to read 13 bytes?
            out = self.com.read(8)
            out = self.com.read(5)
    
            # read the data to out
            out = self.com.read(2500*2)
    
            ## debug reading time
            if self.debug: print "Reading took: "+str(time.time()-t0)+"sec"
    
            # convert read data
            # >: big-endian
            # i: int
            # 2: two bytes
            data = np.fromstring(out, dtype='>i2')
    
            # add offset to data
            data = np.add(data,np.ones(data.shape)*(-float(params['YOFF'])))
            # multiply to get voltage
            data *= float(params['YMULT'])
    
            # create x axis
            x = np.arange(float(params['XZERO']),
                            float(params['XZERO'])+2500*float(params['XINCR']),
                            float(params['XINCR']))
    
            ## debug get x and data length (should be same)
            if self.debug: print "x:"+str(len(x))+" y:"+str(len(data))
    
            # read the closing \r\n
            self.com.read(2)
            
        except:
            # error in read
            try:
                print "Error"
                self.com.close()
                return (0,0)
            except:
                print "Error Closing"  
                return (0,0)
        
        
        # close serial connection
        self.com.close()


        # return x and data
        return (x,data)