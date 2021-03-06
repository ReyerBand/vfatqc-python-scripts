
def fitScanData(treeFile):
    import ROOT as r
    import numpy as np
    from gempython.utils.nesteddict import nesteddict as ndict
    r.gROOT.SetBatch(True)
    r.gStyle.SetOptStat(0)

    inF = r.TFile(treeFile)

    scanHistos = ndict()
    scanCount  = ndict()
    scanFits   = ndict()

    for vfat in range(0,24):
        scanFits[0][vfat] = np.zeros(128)
        scanFits[1][vfat] = np.zeros(128)
        scanFits[2][vfat] = np.zeros(128)
        scanFits[3][vfat] = np.zeros(128)
        scanFits[4][vfat] = np.zeros(128)
        for ch in range(0,128):
            scanHistos[vfat][ch] = r.TH1D('scurve_%i_%i_h'%(vfat,ch),'scurve_%i_%i_h'%(vfat,ch),254,0.5,254.5)
            scanCount[vfat][ch] = 0

    for event in inF.scurveTree :
        scanHistos[event.vfatN][event.vfatCH].Fill(event.vcal,event.Nhits)
        if(event.vcal > 250):
            scanCount[event.vfatN][event.vfatCH] += event.Nhits
            pass
        pass

    random = r.TRandom3()
    random.SetSeed(0)
    fitTF1 = r.TF1('myERF','500*TMath::Erf((TMath::Max([2],x)-[0])/(TMath::Sqrt(2)*[1]))+500',1,253)
    for vfat in range(0,24):
        print 'fitting vfat %i'%vfat
        for ch in range(0,128):
            fitStatus = 1
            fitChi2 = 0
            fitN = 0
            fitGoodN = 0
            MinChi2Temp = 99999999
            stepN = 0
            chi2_iter = 0
            while(stepN < 25):
                rand = random.Gaus(10, 5)
                if (rand < 0.0 or rand > 100): continue
                fitTF1.SetParameter(0, 8+stepN*8)
                fitTF1.SetParameter(1,rand)
                fitTF1.SetParameter(2,8+stepN*8)
                fitTF1.SetParLimits(0, 0.01, 300.0)
                fitTF1.SetParLimits(1, 0.0, 100.0)
                fitTF1.SetParLimits(2, 0.0, 300.0)
                fitResult = scanHistos[vfat][ch].Fit('myERF','SQ')
                #fitStatus = fitResult.Status()
                fitChi2 = fitTF1.GetChisquare()
                #print fitChi2
                stepN +=1
                fitGoodN+=1
                if abs(fitChi2 - MinChi2Temp) < 0.001:
                    chi2_iter += 1
                    pass
                if (fitChi2 < MinChi2Temp and fitChi2 > 0.0):
                    scanFits[0][vfat][ch] = fitTF1.GetParameter(0)
                    scanFits[1][vfat][ch] = fitTF1.GetParameter(1)
                    scanFits[2][vfat][ch] = fitTF1.GetParameter(2)
                    scanFits[3][vfat][ch] = fitChi2
                    scanFits[4][vfat][ch] = scanCount[vfat][ch]
                    MinChi2Temp = fitChi2
                    pass
                if (fitTF1.GetParameter(0) == 8+stepN*8):
                    scanFits[0][vfat][ch] = -999.9
                    scanFits[1][vfat][ch] = -999.9
                    scanFits[2][vfat][ch] = -999.9
                    scanFits[3][vfat][ch] = -999999999.9
                    scanFits[4][vfat][ch] = scanCount[vfat][ch]
                    MinChi2Temp = fitChi2
                    pass
                if (MinChi2Temp < 50): break
                pass
            pass
        pass
    return scanFits
