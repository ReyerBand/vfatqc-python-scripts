from plot_scurve import *
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--infilename", type="string", dest="filename", default="SCurveFitData.root",
                  help="Specify Input Filename", metavar="filename")
parser.add_option("-v", "--vfat", type="int", dest="vfat",
                  help="Specify VFAT to plot", metavar="vfat")
parser.add_option("-s", "--strip", type="int", dest="strip",
                  help="Specify strip to plot", metavar="strip")
parser.add_option("-o","--overlay", action="store_true", dest="overlay_fit",
                  help="Make overlay of fit result on scurve", metavar="overlay_fit")
parser.add_option("-c","--channels_yes", action="store_true", dest="channel_yes",
                  help="Passing a channel number instead of strip number", metavar="channel_yes")

(options, args) = parser.parse_args()

filename = options.filename
overlay_fit = options.overlay_fit
channel_yes = options.channel_yes
vfat = options.vfat
strip = options.strip
import ROOT as r

r.gStyle.SetOptStat(0)

thr     = []
Scurves = []
if options.overlay_fit:
    fits = []
pass
fitF = r.TFile(filename)
for event in fitF.scurveFitTree:
    if (event.vthr) not in thr:
        thr.append(event.vthr)
        pass
    pass
print thr

canvas = r.TCanvas('canvas', 'canvas', 1200, 1200)
canvas.cd()
i = 0
for thresh in thr:
    for event in fitF.scurveFitTree:
        if (event.vthr == thresh) and (event.vfatN == vfat) and (event.ROBstr == strip):
            Scurves.append((event.scurve_h).Clone())
            if options.overlay_fit:
                fitTF1 =  r.TF1('myERF','500*TMath::Erf((TMath::Max([2],x)-[0])/(TMath::Sqrt(2)*[1]))+500',1,253)
                fitTF1.SetParameter(0, event.threshold)
                fitTF1.SetParameter(1, event.noise)
                fitTF1.SetParameter(2, event.pedestal)
                fits.append(fitTF1.Clone())
                pass
            pass
        pass
    pass

leg = r.TLegend(0.1, 0.6, 0.3, 0.8)

for hist in Scurves:
    hist.SetTitle("")
    hist.SetLineColor((i%9) + 1)
    hist.GetYaxis().SetRange(0,1000)
    hist.GetYaxis().SetTitle('Nhits')
    hist.SetMaximum(1000)
    if i == 0:
        hist.Draw()
        hist.Set
        i+=1
        pass
    else:
        hist.Draw('SAME')
        i+=1
        pass
    leg.AddEntry(hist, "Scurve for vthr%i"%thr[i-1])
    pass
j = 0
if options.overlay_fit:
    for fit in fits:
        fit.SetLineColor((j%9) + 1)
        fit.SetTitle("")
        j+=1
        fit.Draw('SAME')
        pass
    pass
leg.Draw('SAME')
canvas.Update()
canvas.SaveAs('ScurveThresh_VFAT%iStrip%i.png'%(vfat, strip))
