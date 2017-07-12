import sys

from ROOT import TFile, TF2, TF1
from utils import cut_histo

"""
Playing around with fitting to the merged bkg file
"""

# mjj_range = (800, 3000) # dijet falling spectrum
# mavg_range = (35, 110) # average m_j falling spectrum

mjj_range = (800, 2500) # dijet falling spectrum
mavg_range = (35, 90) # average m_j falling spectrum

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
    # jetmass.SetAxisRange(*(mavg_range+('x',)))
    # jetmass.SetAxisRange(*(mjj_range+('y',)))

    jetmass_cut = cut_histo(jetmass, 18, 45, 53, 167, "new", "New")

    import pdb; pdb.set_trace()
    
    fit_fcn = TF2(
        "mjj_avg_fcn", "[0]*(1-x/13000)^[1]*(x/13000)^([2] + [3]*log(x/13000))*" + 
        "(1-y/13000)^[4]*(y/13000)^([5] + [6]*log(y/13000))",
        *(mavg_range+mjj_range)
    )
    # fit_fcn.SetNpx(jetmass.GetNbinsX())
    # fit_fcn.SetNpy(jetmass.GetNbinsY())
    fit_fcn.SetParameter(0, 5000)
    fit_fcn.SetParameter(1, 15)
    fit_fcn.SetParameter(2, -4)
    fit_fcn.SetParameter(3, -1)
    fit_fcn.SetParameter(4, 15)
    fit_fcn.SetParameter(5, -4)
    fit_fcn.SetParameter(6, -1)

    jetmass.Fit(fit_fcn)


    import pdb; pdb.set_trace()



if __name__ == '__main__':
    main()
