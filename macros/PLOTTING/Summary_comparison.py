import os
from optparse import OptionParser
from gempython.utils.nesteddict import nesteddict as ndict
from numpy import array, zeros
parser = OptionParser()

parser.add_option("-i", "--infilename", type="string", dest="filename", default="SCurveFitData.root",
                  help="Specify Input Filename", metavar="filename")

(options, args) = parser.parse_args()
filename = options.filename[:-5]

from ROOT import TFile,TH2D,TH1D,TCanvas,gROOT,gStyle,gPad,TGraph,TGraphErrors,TLegend

gROOT.SetBatch(True)
inF = TFile(filename+'.root')

outF = TFile(filename+'_rootfile.root', 'recreate')
dir_name = os.environ.get('PWD')
title_name = dir_name[-10:]
high_thresh = inF.Get('higher_SumThresh')
high_noise = inF.Get('higher_SumNoise')

low_thresh = inF.Get('lower_SumThresh')
low_noise = inF.Get('lower_SumNoise')
outF.cd()
canvas_threshold = TCanvas("canvas_threshold", "canvas_threshold", 1200, 1200)
leg = TLegend(0.8, 0.8, 1.0, 1.0)
high_thresh.SetMarkerColor(2)
high_thresh.SetMarkerStyle(22)
high_thresh.SetMarkerSize(1.5)
high_thresh.SetLineColor(2)
high_thresh.SetLineWidth(3)
low_thresh.SetMarkerColor(4)
low_thresh.SetMarkerStyle(23)
low_thresh.SetMarkerSize(1.5)
low_thresh.SetLineColor(4)
low_thresh.SetLineWidth(3)
high_thresh.SetTitle(title_name)
high_thresh.GetXaxis().SetRangeUser(-0.5, 24.5)
high_thresh.GetXaxis().SetTitle("VFAT Slot")
high_thresh.GetXaxis().CenterTitle()
high_thresh.GetYaxis().SetTitle("Average Threshold [DAC units]")
high_thresh.GetYaxis().SetTitleOffset(1.5)
high_thresh.GetYaxis().SetTickSize(0.02)
high_thresh.GetYaxis().CenterTitle()

high_thresh.SetMinimum(0)
high_thresh.SetMaximum(270)

high_thresh.Draw('ap')
low_thresh.Draw('p')
leg.AddEntry(high_thresh, 'High LV', 'p')
leg.AddEntry(low_thresh, 'Low LV', 'p')
leg.Draw('SAME')
canvas_threshold.Write()
canvas_threshold.SaveAs(dir_name+"_threshold_comparison.png")
leg.Clear()


canvas_noise = TCanvas("canvas_noise", "canvas_noise", 1500, 1200)
high_noise.SetMarkerColor(2)
high_noise.SetMarkerStyle(22)
high_noise.SetMarkerSize(1.5)
high_noise.SetLineColor(2)
low_noise.SetMarkerColor(4)
low_noise.SetMarkerStyle(22)
low_noise.SetMarkerSize(1.5)
low_noise.SetLineColor(4)
low_noise.SetLineWidth(3)
high_noise.SetLineWidth(3)
high_noise.SetTitle(title_name)
high_noise.GetXaxis().SetRangeUser(-0.5, 24.5)
high_noise.GetXaxis().SetTitle("VFAT Slot")
high_noise.GetXaxis().CenterTitle()
high_noise.GetYaxis().SetTitle("Average ENC [e]")
high_noise.GetYaxis().SetTitleOffset(1.5)
high_noise.GetYaxis().SetTickSize(0.02)
high_noise.GetYaxis().CenterTitle()

high_noise.SetMinimum(0)
high_noise.SetMaximum(10000)


leg.AddEntry(high_noise, 'High LV', 'p')
leg.AddEntry(low_noise, 'Low LV', 'p')

high_noise.Draw('ap')
low_noise.Draw('p')
leg.Draw('SAME')
canvas_noise.Update()
canvas_noise.Write()
canvas_noise.SaveAs(dir_name+"_noise_comparison.png")
outF.Write()
outF.Close()
