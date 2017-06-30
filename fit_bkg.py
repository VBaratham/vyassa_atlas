import sys

from ROOT import TFile, TF2, TF1

"""
Playing around with fitting to the merged bkg file
"""


def main():
    f = TFile(sys.argv[1])
    # jetmass = f.Get("jetmass")
    # histo = jetmass.Project3D("yz")
    dijet = f.Get("dijetmass")
    fit_fcn = TF1(
        "dijet", "[0]*(1-x/13000)^[1]*(x/13000)^([2] + [3]*log(x/13000))",
        dijet.GetXaxis().GetXmin(),
        dijet.GetXaxis().GetXmax(),
    )
    
    fit_fcn.SetParameter(0, 100000)
    fit_fcn.SetParameter(1, 15)
    fit_fcn.SetParameter(2, 15)
    fit_fcn.SetParameter(3, 2)
    
    dijet.Fit(fit_fcn)
    

    import pdb; pdb.set_trace()



if __name__ == '__main__':
    main()
