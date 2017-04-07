from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--infilename", type="string", dest="filename", default="SCurveFitData.root",
                  help="Specify Input Filename", metavar="filename")
parser.add_option("-v", "--vfat", type="int", dest="vfat",
                  help="Specify VFAT to plot", metavar="vfat")
parser.add_option("-c","--channels", action="store_true", dest="channels",
                  help="Make plots vs channels instead of strips", metavar="channels")

(options, args) = parser.parse_args()


def plot_vfat_summary(VFAT, fit_filename):
    import ROOT as r
    fitF = r.TFile(fit_filename)
    Scurve = r.TH1D()
    if options.channels:
        vSum = r.TH2D('vSum', 'vSum for VFAT %i; Channels; VCal [DAC units]'%VFAT, 128, -0.5, 127.5, 256, -0.5, 255.5)
        pass
    else:
        vSum = Tr.H2D('vSum', 'vSum for VFAT %i; Strips; VCal [DAC units]'%VFAT, 128, -0.5, 127.5, 256, -0.5, 255.5)
        pass
    vSum.GetYaxis().SetTitleOffset(1.5)
    for event in fitF.scurveFitTree:
        if (event.vfatN == VFAT):
            Scurve = ((event.scurve_h).Clone())
            for x in range(0, 256):
                y = Scurve.FindBin(x)
                if options.channels:
                    vSum.Fill(event.vfatCH, x, Scurve.GetBinContent(y))
                    pass
                else:
                    vSum.Fill(event.vfatstrip, x, Scurve.GetBinContent(y))
                    pass
                pass
            pass
        pass
    canvas = r.TCanvas('canvas', 'canvas', 500, 500)
    r.gStyle.SetOptStat(0)
    vSum.Draw('colz')
    canvas.Update()
    canvas.SaveAs('Summary_VFAT_%i.png'%VFAT)
    return

plot_vfat_summary(options.vfat, options.filename)
