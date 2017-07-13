import sys

from ROOT import TFile, TF2, TF1, TH2D

from utils import cut_histo, chisq
from histoparams import *

"""
Playing around with fitting to the merged bkg file
"""

def main():
    f = TFile(sys.argv[1])


    # # jetmass = f.Get("jetmass")
    # # histo = jetmass.Project3D("yz")
    # dijet = f.Get("mjj_avg")
    # fit_fcn = TF1(
    #     "dijet", "[0]*(1-x/13000)^[1]*(x/13000)^([2] + [3]*log(x/13000))",
    #     # dijet.GetXaxis().GetXmin(),
    #     # dijet.GetXaxis().GetXmax(),
    #     *mjj_range
    # )
    # fit_fcn.SetNpx(jetmass.GetNbinsX())
    # fit_fcn.SetParameter(0, 100000)
    # fit_fcn.SetParameter(1, 15)
    # fit_fcn.SetParameter(2, 15)
    # fit_fcn.SetParameter(3, 2)
    
    # dijet.Fit(fit_fcn, "", "", *mjj_range)


    
    jetmass = f.Get("jetmass_avg")
    # jetmass.SetAxisRange(*(mj_range+('x',)))
    # jetmass.SetAxisRange(*(mjj_range+('y',)))

    jetmass_cut = cut_histo(jetmass,
                            mj_fit_range[0]/mj_binsize, mj_fit_range[1]/mj_binsize + 1,
                            mjj_fit_range[0]/mjj_binsize, mjj_fit_range[1]/mjj_binsize + 1,
                            "jetmass_cut", "Jet masses after cut")

    fit_fcn = TF2(
        "mjj_avg_fcn", "[0]*(1-x/13000)^[1]*(x/13000)^([2] + [3]*log(x/13000))*" + 
        "(1-y/13000)^[4]*(y/13000)^([5] + [6]*log(y/13000))",
        *(mj_fit_range+mjj_fit_range)
    )
    fit_fcn.SetNpx(jetmass_cut.GetNbinsX())
    fit_fcn.SetNpy(jetmass_cut.GetNbinsY())
    fit_fcn.SetParameter(0, 5000)
    fit_fcn.SetParameter(1, 15)
    fit_fcn.SetParameter(2, -4)
    fit_fcn.SetParameter(3, -1)
    fit_fcn.SetParameter(4, 15)
    fit_fcn.SetParameter(5, -4)
    fit_fcn.SetParameter(6, -1)

    jetmass_cut.Fit(fit_fcn)

    fit_histo = TH2D("fitfcn", "Fitted Function", 0, 0, 0, 0, 0, 0)
    fit_fcn.GetHistogram().Copy(fit_histo)

    # The following reports "different bin limits" warning due to bug
    # see https://root-forum.cern.ch/t/attempt-to-divide-histograms-with-different-bin-limits/17624/2
    diff_histo = jetmass_cut - fit_histo


    import pdb; pdb.set_trace()



if __name__ == '__main__':
    main()
