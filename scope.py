import visa
import time
import numpy as np
import traceback


def list_devices():
    """
    Helper function to list all valid addresses
    """
    rm = visa.ResourceManager()
    print rm.list_resources()
    

class Scope:
    """Object modeling the oszilloscope

    Working example:
#####
import numpy as np
import matplotlib.pyplot as plt
import scope

#myscope=scope.Scope(u'GPIB0::1::INSTR', debug=True)
myscope=scope.Scope("COM1", debug=False)

x,data=myscope.readScope(fast_mode=False)

plt.plot(x,data)
plt.show()
#####
    """

#using serial (COM) (@baudrate: 9600)
#   normal mode: 5.3sec
#   fast mode:   2.7sec
#using GPIB
#   normal mode: 0.55sec
#   fast mode:   0.37sec

    def __init__(self, address, baudrate=9600, timeout=6000, debug = False):
        """Create the scope object with given parameters

        Arguments:
        address - the com port to be used, eg "COM1"
                  or a GPIB address like "u'GPIB0::1::INSTR'"
                  the address is obtained by using scope.list_devices()

        Keyword arguments:
        baudrate - serial baudrate that is used (default: 9600)
        timeout - set the timeout. NOTICE: a serial connection needs a long timeout, so the default value is 6sec!
        debug - switch the command line output
        """
        self.debug = True
        rm = visa.ResourceManager()
        try:
            self.inst = rm.open_resource(address, read_termination='\r\n')
        except:
            print "Cannot open connection."
        if timeout:
            self.inst.timeout = timeout
        if "COM" in address:
            self.inst.baud_rate=baudrate    
        self.debug = debug
        
    def readScope(self, channel="CH1", fast_mode=False):
        """Read the data from scope without changing settings

        Keyword arguments:
        channel - channel to be read (default: "CH1")
        fast_mode - use 1byte vs use 2bytes per data point (0.37sec vs 0.55sec)
        """
        # catch possible exceptions
        try:
            # select channel
            self.inst.write("DAT:SOU "+channel)
            # set encoding
            self.inst.write("DAT:ENC RIB")
            # set the byte width (2: 0 to 65,535 )
            if fast_mode:
                #in fast mode use only 1 byte per data point
                self.inst.write("DAT:WID 1")
            else:
                #in normal mode use 2 bytes per data point (more accurate)
                self.inst.write("DAT:WID 2")
            # set the starting point for aquisition
            ## should this be 0?
            self.inst.write("DAT:STAR 1")
            # set the end point
            self.inst.write("DAT:STOP 2500")

            # collect oszi settings for the waveform
            # with this the real axis can be obtained
            out = self.inst.query("WFMPRe?")
   
    
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
            self.inst.write("CURV?")
    
            ## debug for time measurement
            if self.debug: t0 = time.time()
        
            # read the data to out
            out = self.inst.read_raw()
            out = out[13:] #drop the first 13 chars = ":CURVE #45000"
            out = out[:-1] #drop '\r\n'
    
            ## debug reading time
            if self.debug: print "Reading took: "+str(time.time()-t0)+"sec"
    
            # convert read data
            # >: big-endian
            # i: int
            # 2: two bytes
            if fast_mode:
                if len(out) > 2500:
                    out = out[:2500]
                data = np.fromstring(out, dtype='b')
            else:
                if len(out) > 5000:
                    out = out[:5000] #drop another char  (only neccessary when using serial connection COM port)??
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
            #self.com.read(2)
            
        except:
            # error in read
            traceback.print_exc()
            try:
                print "Error"
                #self.com.close()
                return (0,0)
            except:
                print "Error Closing"  
                return (0,0)
        
        
        # close serial connection
        #self.inst.close()


        # return x and data
        return (x,data)