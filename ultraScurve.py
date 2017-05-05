#!/bin/env python
"""
Script to take Scurve data using OH ultra scans
By: Cameron Bravo (c.bravo@cern.ch)
"""

import sys
from array import array
from gempython.tools.vfat_user_functions_uhal import *

from qcoptions import parser

parser.add_option("-f", "--filename", type="string", dest="filename", default="SCurveData.root",
                  help="Specify Output Filename", metavar="filename")
parser.add_option("-l", "--latency", type="int", dest = "latency", default = 37,
                  help="Specify Latency", metavar="latency")
parser.add_option("-m", "--mono", type="int", dest = "MSPL", default = 48,
                  help="Specify MSPL.  Must be range 0-7 after bitshifting to the right by 4", metavar="MSPL")
parser.add_option("--CalPhase", type="int", dest = "CalPhase", default = 0,
                  help="Specify CalPhase", metavar="CalPhase")

(options, args) = parser.parse_args()
uhal.setLogLevelTo( uhal.LogLevel.WARNING )

if options.debug:
    uhal.setLogLevelTo( uhal.LogLevel.DEBUG )
else:
    uhal.setLogLevelTo( uhal.LogLevel.ERROR )

import ROOT as r
filename = options.filename
if (((options.MSPL >> 4) > 7) or ((options.MSPL >> 4) < 0)):
    print "Enter a valid range for the MSPL.  MSPL >> 4 must be between 0 and 7."
    exit
    pass
myF = r.TFile(filename,'recreate')
myT = r.TTree('scurveTree','Tree Holding CMS GEM SCurve Data')

Nev = array( 'i', [ 0 ] )
Nev[0] = 1000
myT.Branch( 'Nev', Nev, 'Nev/I' )
vcal = array( 'i', [ 0 ] )
myT.Branch( 'vcal', vcal, 'vcal/I' )
Nhits = array( 'i', [ 0 ] )
myT.Branch( 'Nhits', Nhits, 'Nhits/I' )
vfatN = array( 'i', [ 0 ] )
myT.Branch( 'vfatN', vfatN, 'vfatN/I' )
vfatCH = array( 'i', [ 0 ] )
myT.Branch( 'vfatCH', vfatCH, 'vfatCH/I' )
trimRange = array( 'i', [ 0 ] )
myT.Branch( 'trimRange', trimRange, 'trimRange/I' )
vthr = array( 'i', [ 0 ] )
myT.Branch( 'vthr', vthr, 'vthr/I' )
trimDAC = array( 'i', [ 0 ] )
myT.Branch( 'trimDAC', trimDAC, 'trimDAC/I' )
latency = array( 'i', [ 0 ] )
myT.Branch( 'latency', latency, 'latency/I' )
latency[0] = options.latency
link = array( 'i', [ 0 ] )
myT.Branch( 'link', link, 'link/I' )
link[0] = options.gtx
utime = array( 'i', [ 0 ] )
myT.Branch( 'utime', utime, 'utime/I' )

import subprocess,datetime,time
utime[0] = int(time.time())
startTime = datetime.datetime.now().strftime("%Y.%m.%d.%H.%M")
print startTime
Date = startTime

ohboard = getOHObject(options.slot,options.gtx,options.shelf,options.debug)

SCURVE_MIN = 0
SCURVE_MAX = 254

N_EVENTS = Nev[0]
CHAN_MIN = 67
CHAN_MAX = 68
if options.debug:
    CHAN_MAX = 5
    pass
mask = 0

try:
    setTriggerSource(ohboard,options.gtx,1)
    configureLocalT1(ohboard, options.gtx, 1, 0, 40, 250, 0, options.debug)
    startLocalT1(ohboard, options.gtx)

    print 'Link %i T1 controller status: %i'%(options.gtx,getLocalT1Status(ohboard,options.gtx))

    #biasAllVFATs(ohboard,options.gtx,0x0,enable=False)
    #writeAllVFATs(ohboard, options.gtx, "VThreshold1", 100, 0)

    writeAllVFATs(ohboard, options.gtx, "Latency",    options.latency, mask)
    writeAllVFATs(ohboard, options.gtx, "ContReg0", 0x37, mask)
    writeAllVFATs(ohboard, options.gtx, "ContReg2",   int(options.MSPL), mask)
    writeAllVFATs(ohboard, options.gtx, "CalPhase",    options.CalPhase, mask)

    for vfat in range(0,24):
        for scCH in range(CHAN_MIN,CHAN_MAX):
            trimVal = (0x3f & readVFAT(ohboard,options.gtx,vfat,"VFATChannels.ChanReg%d"%(scCH)))
            writeVFAT(ohboard,options.gtx,vfat,"VFATChannels.ChanReg%d"%(scCH),trimVal)

    for scCH in range(CHAN_MIN,CHAN_MAX):
        vfatCH[0] = scCH
        print "Channel #"+str(scCH)
        for vfat in range(0,24):
            trimVal = (0x3f & readVFAT(ohboard,options.gtx,vfat,"VFATChannels.ChanReg%d"%(scCH)))
            writeVFAT(ohboard,options.gtx,vfat,"VFATChannels.ChanReg%d"%(scCH),trimVal+64)
        configureScanModule(ohboard, options.gtx, 3, mask, channel = scCH, scanmin = SCURVE_MIN, scanmax = SCURVE_MAX, numtrigs = int(N_EVENTS), useUltra = True, debug = options.debug)
        printScanConfiguration(ohboard, options.gtx, useUltra = True, debug = options.debug)
        startScanModule(ohboard, options.gtx, useUltra = True, debug = options.debug)
        scanData = getUltraScanResults(ohboard, options.gtx, SCURVE_MAX - SCURVE_MIN + 1, options.debug)
        for i in range(0,24):
            vfatN[0] = i
            dataNow = scanData[i]
            trimRange[0] = (0x07 & readVFAT(ohboard,options.gtx, i,"ContReg3"))
            trimDAC[0]   = (0x1f & readVFAT(ohboard,options.gtx, i,"VFATChannels.ChanReg%d"%(scCH)))
            vthr[0]      = (0xff & readVFAT(ohboard,options.gtx, i,"VThreshold1"))
            for VC in range(SCURVE_MAX-SCURVE_MIN+1):
                try:
                    vcal[0]  = int((dataNow[VC] & 0xff000000) >> 24)
                    Nhits[0] = int(dataNow[VC] & 0xffffff)
                except IndexError:
                    print 'Unable to index data for channel %i'%scCH
                    print dataNow
                    vcal[0]  = -99
                    Nhits[0] = -99
                finally:
                    myT.Fill()
        for vfat in range(0,24):
            trimVal = (0x3f & readVFAT(ohboard,options.gtx,vfat,"VFATChannels.ChanReg%d"%(scCH)))
            writeVFAT(ohboard,options.gtx,vfat,"VFATChannels.ChanReg%d"%(scCH),trimVal)
        myT.AutoSave("SaveSelf")
        sys.stdout.flush()
        pass
    stopLocalT1(ohboard, options.gtx)
    writeAllVFATs(ohboard, options.gtx, "ContReg0",    0x36, mask)

except Exception as e:
    myT.AutoSave("SaveSelf")
    print "An exception occurred", e
finally:
    myF.cd()
    myT.Write()
    myF.Close()




