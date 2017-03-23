#!/bin/env python
"""
Script to set trimdac values on a chamber
By: Christine McLean (ch.mclean@cern.ch), Cameron Bravo (c.bravo@cern.ch), Elizabeth Starling (elizabeth.starling@cern.ch)
"""

import sys
from array import array
from gempython.tools.vfat_user_functions_uhal import *
from gempython.utils.nesteddict import nesteddict as ndict
from chamberInfo import chamber_config

def runCommand(cmd):
    import datetime,os,sys
    import subprocess
    from subprocess import CalledProcessError
    try:
        print "Executing command",cmd
        sys.stdout.flush()
        returncode = subprocess.call(cmd)
    except CalledProcessError as e:
        print "Caught exception",e,"running",cmd
        sys.stdout.flush()
        pass
    return returncode

from qcoptions import parser

parser.add_option("--ztrim", type="float", dest="ztrim", default=4.0,
                  help="Specify the p value of the trim", metavar="ztrim")


uhal.setLogLevelTo( uhal.LogLevel.WARNING )
(options, args) = parser.parse_args()

ztrim = options.ztrim
print 'trimming at p = %f'%ztrim

if os.getenv('DATA_PATH') == None or os.getenv('DATA_PATH') == '':
    print 'You must source the environment properly!'
if os.getenv('BUILD_HOME') == None or os.getenv('BUILD_HOME') == '':
    print 'You must source the environment properly!'

from macros.fitScanData import fitScanData
import subprocess,datetime
startTime = datetime.datetime.now().strftime("%Y.%m.%d-%H.%M.%S.%f")
print startTime

ohboard = getOHObject(options.slot,options.gtx,options.shelf,options.debug)

dirPath = '%s/%s/trimming/%s'%(os.getenv("DATA_PATH"),chamber_config[options.gtx],startTime)
runCommand(["mkdir","-p",dirPath])

# bias vfats
biasAllVFATs(ohboard,options.gtx,0x0,enable=False)
writeAllVFATs(ohboard, options.gtx, "VThreshold1", 100, 0)

CHAN_MIN = 0
CHAN_MAX = 128

masks = ndict()
for vfat in range(0,24):
    for ch in range(CHAN_MIN,CHAN_MAX):
        masks[vfat][ch] = False

#Find trimRange for each VFAT
tRanges    = ndict()
tRangeGood = ndict()
trimVcal = ndict()
trimCH   = ndict()
goodSup  = ndict()
goodInf  = ndict()
for vfat in range(0,24):
    tRanges[vfat] = 0
    tRangeGood[vfat] = False
    trimVcal[vfat] = 0
    trimCH[vfat] = 0
    goodSup[vfat] = -99
    goodInf[vfat] = -99

###############
# TRIMDAC = 0
###############
# Configure for initial scan
for vfat in range(0,24):
    writeVFAT(ohboard, options.gtx, vfat, "ContReg3", tRanges[vfat],0)
    for scCH in range(CHAN_MIN,CHAN_MAX):
        writeVFAT(ohboard,options.gtx,vfat,"VFATChannels.ChanReg%d"%(scCH),0)

# Scurve scan with trimdac set to 0
filename0 = "%s/SCurveData_trimdac0_range0.root"%dirPath
runCommand(["./ultraScurve.py",
            "-s%d"%(options.slot),
            "-g%d"%(options.gtx),
            "--filename=%s"%(filename0)]
           )
muFits_0  = fitScanData(filename0)
for vfat in range(0,24):
    for ch in range(CHAN_MIN,CHAN_MAX):
        if muFits_0[4][vfat][ch] < 0.1: masks[vfat][ch] = True

# This loop determines the trimRangeDAC for each VFAT
for trimRange in range(0,5):
    # Set Trim Ranges
    for vfat in range(0,24):
        writeVFAT(ohboard, options.gtx, vfat, "ContReg3", tRanges[vfat],0)
    ###############
    # TRIMDAC = 31
    ###############
    # Setting trimdac value
    for vfat in range(0,24):
        for scCH in range(CHAN_MIN,CHAN_MAX):
            writeVFAT(ohboard,options.gtx,vfat,"VFATChannels.ChanReg%d"%(scCH),31)

    # Scurve scan with trimdac set to 31 (maximum trimming)
    filename31 = "%s/SCurveData_trimdac31_range%i.root"%(dirPath,trimRange)
    runCommand(["./ultraScurve.py",
                "-s%d"%(options.slot),
                "-g%d"%(options.gtx),
                "--filename=%s"%(filename31)]
               )

    # For each channel check that the infimum of the scan with trimDAC = 31
    # is less than the subpremum of the scan with trimDAC = 0.
    # The difference should be greater than the trimdac range.
    muFits_31 = fitScanData(filename31)

    sup   = ndict()
    supCH = ndict()
    inf   = ndict()
    infCH = ndict()

    # Check to see if the new trimRange is good
    for vfat in range(0,24):
        if(tRangeGood[vfat]): continue
        sup[vfat] = 999.0
        inf[vfat] = 0.0
        supCH[vfat] = -1
        infCH[vfat] = -1
        for ch in range(CHAN_MIN,CHAN_MAX):
            if(masks[vfat][ch]): continue
            if(muFits_31[0][vfat][ch] - ztrim*muFits_31[1][vfat][ch] > inf[vfat]):
                inf[vfat] = muFits_31[0][vfat][ch] - ztrim*muFits_31[1][vfat][ch]
                infCH[vfat] = ch
            if(muFits_0[0][vfat][ch] - ztrim*muFits_0[1][vfat][ch] < sup[vfat] and muFits_0[0][vfat][ch] - ztrim*muFits_0[1][vfat][ch] > 0.1):
                sup[vfat] = muFits_0[0][vfat][ch] - ztrim*muFits_0[1][vfat][ch]
                supCH[vfat] = ch
        print "vfat: %i"%vfat
        print muFits_0[0][vfat]
        print muFits_31[0][vfat]
        print "sup: %f  inf: %f"%(sup[vfat],inf[vfat])
        print "supCH: %f  infCH: %f"%(supCH[vfat],infCH[vfat])
        print " "
        if (inf[vfat] <= sup[vfat]):
            tRangeGood[vfat] = True
            goodSup[vfat] = sup[vfat]
            goodInf[vfat] = inf[vfat]
            trimVcal[vfat] = sup[vfat]
            trimCH[vfat] = supCH[vfat]
        else:
            tRanges[vfat] += 1
            trimVcal[vfat] = sup[vfat]
            trimCH[vfat] = supCH[vfat]

            pass
        pass
    pass

#Init trimDACs to all zeros
trimDACs = ndict()
for vfat in range(0,24):
    for ch in range(CHAN_MIN,CHAN_MAX):
        trimDACs[vfat][ch] = 0

# This is a binary search to set each channel's trimDAC
for i in range(0,5):
    # First write this steps values to the VFATs
    for vfat in range(0,24):
        for ch in range(CHAN_MIN,CHAN_MAX):
            trimDACs[vfat][ch] += pow(2,4-i)
            writeVFAT(ohboard,options.gtx,vfat,"VFATChannels.ChanReg%d"%(ch),trimDACs[vfat][ch])
    # Run an SCurve
    filenameBS = "%s/SCurveData_binarySearch%i.root"%(dirPath,i)
    runCommand(["./ultraScurve.py",
                "-s%d"%(options.slot),
                "-g%d"%(options.gtx),
                "--filename=%s"%(filenameBS)]
               )
    # Fit Scurve data
    fitData = fitScanData(filenameBS)
    # Now use data to determine the new trimDAC value
    for vfat in range(0,24):
        for ch in range(CHAN_MIN,CHAN_MAX):
            if(fitData[0][vfat][ch] - ztrim*fitData[1][vfat][ch] < trimVcal[vfat]): trimDACs[vfat][ch] -= pow(2,4-i)

# Now take a scan with trimDACs found by binary search
for vfat in range(0,24):
    for ch in range(CHAN_MIN,CHAN_MAX):
        writeVFAT(ohboard,options.gtx,vfat,"VFATChannels.ChanReg%d"%(ch),trimDACs[vfat][ch])

filenameFinal = "%s/SCurveData_Trimmed.root"%dirPath
runCommand(["./ultraScurve.py",
            "-s%d"%(options.slot),
            "-g%d"%(options.gtx),
            "--filename=%s"%(filenameFinal)]
           )

scanFilename = '%s/scanInfo.txt'%dirPath
outF = open(scanFilename,'w')
outF.write('vfat/I:tRange/I:sup/D:inf/D:trimVcal/D:trimCH/D\n')
for vfat in range(0,24):
    outF.write('%i  %i  %f  %f  %f  %i\n'%(vfat,tRanges[vfat],goodSup[vfat],goodInf[vfat],trimVcal[vfat],trimCH[vfat]))
    pass
outF.close()

exit(0)












