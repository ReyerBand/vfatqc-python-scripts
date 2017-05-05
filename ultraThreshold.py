#!/bin/env python
"""
Script to take VT1 data using OH ultra scans
By: Cameron Bravo c.bravo@cern.ch
"""

import sys, os, random, time
from array import array

from gempython.tools.optohybrid_user_functions_uhal import *
from gempython.tools.vfat_user_functions_uhal import *

from qcoptions import parser

parser.add_option("--vt2", type="int", dest="vt2", default=0,
                  help="Specify VT2 to use", metavar="vt2")
parser.add_option("-f", "--filename", type="string", dest="filename", default="VT1ScanData.root",
                  help="Specify Output Filename", metavar="filename")
parser.add_option("--perchannel", action="store_true", dest="perchannel",
                  help="Run a per-channel VT1 scan", metavar="perchannel")
parser.add_option("--trkdata", action="store_true", dest="trkdata",
                  help="Run a per-VFAT VT1 scan using tracking data (default is to use trigger data)", metavar="trkdata")
parser.add_option("-l", "--latency", type="int", dest = "latency", default = 37,
                  help="Specify Latency", metavar="latency")
parser.add_option("--MSPL", type="int", dest = "MSPL", default = 48,
                  help="Specify value written to ContReg2.  A value of 0 corresponds to 1 clock cycle.  Must be range 0-7 after bitshifting to the right by 4", metavar="MSPL")
parser.add_option("--CalPhase", type="int", dest = "CalPhase", default = 0,
                  help="Specify CalPhase", metavar="CalPhase")
parser.add_option("--CalPulse", action="store_true", dest="CalPulse",
                  help="Configure to send a CalPulse before the scan", metavar="CalPulse")
parser.add_option("--VCal", type="int", dest = "VCal", default = 255,
                  help="Specify VCal pulse in DAC units to be sent with CalPulse option.", metavar="VCal")

(options, args) = parser.parse_args()

if options.vt2 not in range(256):
    print "Invalid VT2 specified: %d, must be in range [0,255]"%(options.vt2)
    exit(1)

if options.debug:
    uhal.setLogLevelTo( uhal.LogLevel.DEBUG )
else:
    uhal.setLogLevelTo( uhal.LogLevel.ERROR )

import ROOT as r
filename = options.filename
myF = r.TFile(filename,'recreate')
myT = r.TTree('thrTree','Tree Holding CMS GEM VT1 Data')

Nev = array( 'i', [ 0 ] )
Nev[0] = 1000
myT.Branch( 'Nev', Nev, 'Nev/I' )
vth = array( 'i', [ 0 ] )
myT.Branch( 'vth', vth, 'vth/I' )
vth1 = array( 'i', [ 0 ] )
myT.Branch( 'vth1', vth1, 'vth1/I' )
vth2 = array( 'i', [ 0 ] )
myT.Branch( 'vth2', vth2, 'vth2/I' )
vth2[0] = options.vt2
Nhits = array( 'i', [ 0 ] )
myT.Branch( 'Nhits', Nhits, 'Nhits/I' )
vfatN = array( 'i', [ 0 ] )
myT.Branch( 'vfatN', vfatN, 'vfatN/I' )
vfatCH = array( 'i', [ 0 ] )
myT.Branch( 'vfatCH', vfatCH, 'vfatCH/I' )
trimRange = array( 'i', [ 0 ] )
myT.Branch( 'trimRange', trimRange, 'trimRange/I' )
link = array( 'i', [ 0 ] )
myT.Branch( 'link', link, 'link/I' )
link[0] = options.gtx
mode = array( 'i', [ 0 ] )
myT.Branch( 'mode', mode, 'mode/I' )
utime = array( 'i', [ 0 ] )
myT.Branch( 'utime', utime, 'utime/I' )
latency = array( 'i', [ 0 ] )
myT.Branch( 'latency', latency, 'latency/I' )
latency[0] = options.latency

if options.CalPulse:
    CalPhase = array( 'i', [ 0 ] )
    myT.Branch( 'CalPhase', CalPhase, 'CalPhase/I' )
    VCal = array( 'i', [ 0 ] )
    myT.Branch( 'VCal', VCal, 'VCal/I' )
    CalPhase[0] = options.CalPhase
    VCal[0] = options.VCal
    pass
import subprocess,datetime,time
utime[0] = int(time.time())
startTime = datetime.datetime.now().strftime("%Y.%m.%d.%H.%M")
print startTime
Date = startTime

ohboard = getOHObject(options.slot,options.gtx,options.shelf,options.debug)

THRESH_MIN = 0
THRESH_MAX = 250

N_EVENTS = Nev[0]
CHAN_MIN = 67
CHAN_MAX = 68
if options.debug:
    CHAN_MAX = 5
    pass
mask = 0

try:
    if options.CalPulse:
        setTriggerSource(ohboard,options.gtx,1)
        configureLocalT1(ohboard, options.gtx, 1, 0, 40, 250, 0, options.debug)
        startLocalT1(ohboard, options.gtx)
        writeAllVFATs(ohboard, options.gtx, "VCal",    options.VCal, mask)
        writeAllVFATs(ohboard, options.gtx, "CalPhase",    options.CalPhase, mask)
        pass

    writeAllVFATs(ohboard, options.gtx, "Latency",     options.latency, mask)
    writeAllVFATs(ohboard, options.gtx, "ContReg0",    0x37, mask)
    writeAllVFATs(ohboard, options.gtx, "ContReg2",   int(options.MSPL), mask)
    writeAllVFATs(ohboard, options.gtx, "VThreshold2", options.vt2, mask)

    if options.perchannel or options.trkdata:
        mode[0] = scanmode.THRESHTRK
        if options.perchannel:
            mode[0] = scanmode.THRESHCH
            pass
#        sendL1A(ohboard, options.gtx, interval=250, number=0)

        for scCH in range(CHAN_MIN,CHAN_MAX):
            vfatCH[0] = scCH
            print "Channel #"+str(scCH)
            if options.CalPulse:
                for vfat in range(0,24):
                    trimVal = (0x3f & readVFAT(ohboard,options.gtx,vfat,"VFATChannels.ChanReg%d"%(scCH)))
                    writeVFAT(ohboard,options.gtx,vfat,"VFATChannels.ChanReg%d"%(scCH),trimVal+64)
                    pass
                pass
            configureScanModule(ohboard, options.gtx, mode[0], mask, channel = scCH,
                                scanmin = THRESH_MIN, scanmax = THRESH_MAX,
                                numtrigs = int(N_EVENTS),
                                useUltra = True, debug = options.debug)
            printScanConfiguration(ohboard, options.gtx, useUltra = True, debug = options.debug)
            startScanModule(ohboard, options.gtx, useUltra = True, debug = options.debug)
            scanData = getUltraScanResults(ohboard, options.gtx, THRESH_MAX - THRESH_MIN + 1, options.debug)
            sys.stdout.flush()
            for i in range(0,24):
                vfatN[0] = i
                dataNow = scanData[i]
                trimRange[0] = (0x07 & readVFAT(ohboard,options.gtx, i,"ContReg3"))
                for VC in range(THRESH_MAX-THRESH_MIN+1):
                    vth1[0] = int((dataNow[VC] & 0xff000000) >> 24)
                    vth[0]  = vth2[0] - vth1[0]
                    Nhits[0] = int(dataNow[VC] & 0xffffff)
                    myT.Fill()
                    pass
                pass
            myT.AutoSave("SaveSelf")
            pass

        stopLocalT1(ohboard, options.gtx)
        pass
    else:
        mode[0] = scanmode.THRESHTRG
        configureScanModule(ohboard, options.gtx, mode[0], mask,
                            scanmin = THRESH_MIN, scanmax = THRESH_MAX,
                            numtrigs = int(N_EVENTS),
                            useUltra = True, debug = options.debug)
        printScanConfiguration(ohboard, options.gtx, useUltra = True, debug = options.debug)
        startScanModule(ohboard, options.gtx, useUltra = True, debug = options.debug)
        scanData = getUltraScanResults(ohboard, options.gtx, THRESH_MAX - THRESH_MIN + 1, options.debug)
        sys.stdout.flush()
        for i in range(0,24):
            vfatN[0] = i
            dataNow = scanData[i]
            trimRange[0] = (0x07 & readVFAT(ohboard,options.gtx, i,"ContReg3"))
            for VC in range(THRESH_MAX-THRESH_MIN+1):
                vth1[0] = int((dataNow[VC] & 0xff000000) >> 24)
                vth[0]  = vth2[0] - vth1[0]
                Nhits[0] = int(dataNow[VC] & 0xffffff)
                myT.Fill()
                pass
            pass
        myT.AutoSave("SaveSelf")
        pass
except Exception as e:
    myT.AutoSave("SaveSelf")
    print "An exception occurred", e
finally:
    myF.cd()
    myT.Write()
    myF.Close()
