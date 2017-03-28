import os
from optparse import OptionParser
from gempython.utils.nesteddict import nesteddict as ndict

parser = OptionParser()

parser.add_option("-i", "--infilename", type="string", dest="filename", default="SCurveFitData.root",
                  help="Specify Input Filename", metavar="filename")
parser.add_option("-t", "--type", type="string", dest="GEBtype", default="long",
                  help="Specify GEB (long/short)", metavar="GEBtype")
parser.add_option("-c","--channels", action="store_true", dest="channels",
                  help="Make plots vs channels instead of strips", metavar="channels")
parser.add_option("-a","--all", action="store_true", dest="all_plots",
                  help="Make all plots", metavar="all_plots")
parser.add_option("-f","--fit", action="store_true", dest="fit_plots",
                  help="Make fit parameter plots", metavar="fit_plots")
parser.add_option("-x","--chi2", action="store_true", dest="chi2_plots",
                  help="Make Chi2 plots", metavar="chi2_plots")


(options, args) = parser.parse_args()
filename = options.filename[:-5]

from ROOT import TFile,TH2D,TH1D,TCanvas,gROOT,gStyle,gPad,TGraph

gROOT.SetBatch(True)
GEBtype = options.GEBtype
inF = TFile(filename+'.root')
outF = TFile(filename+'_Plots.root', 'recreate')


buildHome = os.environ.get('BUILD_HOME')

vSum   = ndict()
vNoise = ndict()
vThreshold = ndict()
vChi2      = ndict()
vComparison = ndict()
vNoiseTrim  = ndict()
vPedestal   = ndict()
vSumofSum = ndict()

for i in range(0,24):
    vNoise[i] = TH1D('Noise%i'%i,'Noise%i;Noise [DAC units]'%i,35,-0.5,34.5)
    vPedestal[i] = TH1D('Pedestal%i'%i,'Pedestal%i;Pedestal [DAC units]'%i,256,-0.5,255.5)
    vThreshold[i] = TH1D('Threshold%i'%i,'Threshold%i;Threshold [DAC units]'%i,60,-0.5,299.5)
    vChi2[i] = TH1D('ChiSquared%i'%i,'ChiSquared%i;Chi2'%i,100,-0.5,999.5)
    vComparison[i] = TH2D('vComparison%i'%i,'Fit Summary %i;Threshold [DAC units];Noise [DAC units]'%i,60,-0.5,299.5,70,-0.5,34.5)
    vNoiseTrim[i] = TH2D('vNoiseTrim%i'%i,'Noise vs. Trim Summary %i;Trim [DAC units];Noise [DAC units]'%i,32,-0.5,31.5,70,-0.5,34.5)
    vComparison[i].GetYaxis().SetTitleOffset(1.5)
    vNoiseTrim[i].GetYaxis().SetTitleOffset(1.5)
    pass
vSumofSumNoise = TH2D('vSumofSumNoise','Average Noise per VFAT;VFAT;Noise [DAC units]',24,-0.5,23.5,70,-0.5,34.5)
vSumofSumThreshold = TH2D('vSumofSumThreshold','Average Threshold per VFAT;VFAT;Threshold [DAC units]',24,-0.5,23.5,60,-0.5,299.5)
vSumofSumNoise.GetYaxis().SetTitleOffset(1.5)
vSumofSumThreshold.GetYaxis().SetTitleOffset(1.5)

for event in inF.scurveFitTree:
    strip = event.vfatstrip
    param0 = event.threshold
    param1 = event.noise
    param2 = event.pedestal
    vThreshold[event.vfatN].Fill(param0)
    vNoise[event.vfatN].Fill(param1)
    vPedestal[event.vfatN].Fill(param2)
    vChi2[event.vfatN].Fill(event.chi2)
    vComparison[event.vfatN].Fill(param0, param1)
    vNoiseTrim[event.vfatN].Fill(event.trimDAC, param1)
    pass

outF.cd()
for i in range(0,24):
    vSumofSumNoise.Fill(i, vNoise[i].GetMean())
    vSumofSumThreshold.Fill(i, vThreshold[i].GetMean())
    pass


if options.fit_plots or options.all_plots:

#    canvas_sumofsum = TCanvas('canvas_sumofsum', 'canvas_sumofsum', 800, 800)
#    vSumofSumNoise.Draw()
    vSumofSumNoise.Write()
    vSumofSumThreshold.Write()


    gStyle.SetOptStat(111100)
    canv_comp = TCanvas('canv_comp','canv_comp',500*8,500*3)
    canv_comp.Divide(8,3)
    for i in range(0,24):
        canv_comp.cd(i+1)
        gStyle.SetOptStat(111100)
        vComparison[i].Draw('colz')
        vComparison[i].Write()
        canv_comp.Update()
        pass
    canv_comp.SaveAs(filename+'_FitSummary.png')

    gStyle.SetOptStat(111100)
    canv_trim = TCanvas('canv_trim','canv_trim',500*8,500*3)
    canv_trim.Divide(8,3)
    for i in range(0,24):
        canv_trim.cd(i+1)
        gStyle.SetOptStat(111100)
        vNoiseTrim[i].Draw('colz')
        vNoiseTrim[i].Write()
        canv_trim.Update()
        pass
    canv_trim.SaveAs(filename+'_TrimNoiseSummary.png')

    canv_thresh = TCanvas('canv_thresh','canv_thresh',500*8,500*3)
    canv_thresh.Divide(8,3)
    for i in range(0,24):
        canv_thresh.cd(i+1)
        gStyle.SetOptStat(111100)
        vThreshold[i].Draw()
        vThreshold[i].Write()
        gPad.SetLogy()
        canv_thresh.Update()
        pass
    canv_thresh.SaveAs(filename+'_FitThreshSummary.png')

    canv_Pedestal = TCanvas('canv_Pedestal','canv_Pedestal',500*8,500*3)
    canv_Pedestal.Divide(8,3)
    for i in range(0,24):
        canv_Pedestal.cd(i+1)
        gStyle.SetOptStat(111100)
        vPedestal[i].Draw()
        gPad.SetLogy()
        vPedestal[i].Write()
        canv_Pedestal.Update()
        pass
    canv_Pedestal.SaveAs(filename+'_FitPedestalSummary.png')

    canv_noise = TCanvas('canv_noise','canv_noise',500*8,500*3)
    canv_noise.Divide(8,3)
    for i in range(0,24):
        canv_noise.cd(i+1)
        vNoise[i].Draw()
        vNoise[i].Write()
        gPad.SetLogy()
        canv_noise.Update()
        pass
    canv_noise.SetLogy()
    canv_noise.SaveAs(filename+'_FitNoiseSummary.png')
    pass
if options.chi2_plots or options.all_plots:
    canv_Chi2 = TCanvas('canv_Chi2','canv_Chi2',500*8,500*3)
    canv_Chi2.Divide(8,3)
    canv_Chi2.SetLogy()
    for i in range(0,24):
        canv_Chi2.cd(i+1)
        vChi2[i].Draw()
        vChi2[i].Write()
        gPad.SetLogy()
        canv_Chi2.Update()
        pass
    canv_Chi2.SetLogy()
    canv_Chi2.SaveAs(filename+'_FitChi2Summary.png')
    pass

outF.Write()
outF.Close()
