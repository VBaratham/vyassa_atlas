import sys
import array

from ROOT import TF1, TFile, TGraphErrors, THStack

from utils import cut_histo, slice_histo_y, slice_by_slice_fit, get_jetmass_cut
from histoparams import *

NPARAM = 5

def get_1d_fit_fcn(sliced_histo, i):
    fit_fcn = TF1("mjj_slice %s" % i,
                  "[0]*(1-x/13000)^[1]*(x/13000)^([2] + [3]*log(x/13000))",
                  *mjj_fit_range)
    fit_fcn.SetNpx(sliced_histo.GetNbinsX())
    fit_fcn.SetParameter(0, 5000)
    fit_fcn.SetParameter(1, 15)
    fit_fcn.SetParameter(2, -4)
    fit_fcn.SetParameter(3, -1)
    global NPARAM; NPARAM = 4
    return fit_fcn

def get_1d_fit_fcn_b(sliced_histo, i):
    fit_fcn = TF1("mjj_slice %s" % i,
                  "[0]*(1-x/13000)^([1] + [2]*log(1-x/13000))*(x/13000)^([3] + [4]*log(x/13000))",
                  *mjj_fit_range)
    fit_fcn.SetNpx(sliced_histo.GetNbinsX())
    fit_fcn.SetParameter(0, 5000)
    fit_fcn.SetParameter(1, 15)
    fit_fcn.SetParameter(2, 1)
    fit_fcn.SetParameter(3, -4)
    fit_fcn.SetParameter(4, -1)
    global NPARAM; NPARAM = 5
    return fit_fcn

def main():
    f = TFile(sys.argv[1])
    jetmass = f.Get("jetm_qg")
    # jetmass = f.Get("jetmass_avg")
    jetmass_cut = get_jetmass_cut(jetmass)

    fcns, fit_histo = slice_by_slice_fit(jetmass_cut, get_1d_fit_fcn)
    diff_histo = jetmass_cut - fit_histo

    # # NOTE: this is now done by utils.slice_by_slice_fit, but this makes a stackplot too
    # # Fit the 1d function to each slice and store the fit parameters
    # # xpoints = array.array('d')
    # fcns = []
    # # fitparams = [array.array('d') for i in range(NPARAM)]
    # # fitparam_errs = [array.array('d') for i in range(NPARAM)]
    # mjj_stack = THStack("mjjs", "") # Stack for each m_j, normalized to 1
    # for x in range(jetmass_cut.GetNbinsX()):
    #     sliced_histo = slice_histo_y(jetmass_cut, x+1, "slice_%s" % (x+1), "M_jj, slice %s" % (x+1))
    #     fit_fcn = get_1d_fit_fcn(sliced_histo, x+1)
    #     sliced_histo.Fit(fit_fcn)
    #     fcns.append(fit_fcn)

    #     print "Slice %s chisq = %s" % (x+1, fit_fcn.GetChisquare())
    #     print
    #     print

    #     # import pdb; pdb.set_trace()

    #     # This doesn't do what I'd hoped:
    #     # fit_fcn.SetParameter(0, fit_fcn.GetParameter(0)/sliced_histo.Integral())
    #     sliced_histo.Scale(1.0/sliced_histo.Integral())
    #     mjj_stack.Add(sliced_histo)


    # graph fit parameters
    fitparams = [
        array.array('d', [fit_fcn.GetParameter(i) for fit_fcn in fcns])
        for i in range(NPARAM)
    ]
    fitparam_errs = [
        array.array('d', [fit_fcn.GetParError(i) for fit_fcn in fcns])
        for i in range(NPARAM)
    ]
    xpoints = array.array('d', [float(mj_fit_range[0] + mj_binsize * (i+0.5))
                                for i in range(len(fitparams[0]))])
    no_errors = array.array('d', [0.0 for i in range(len(fitparams[0]))])
    fitparam_graphs = [
        TGraphErrors(len(fitparams[i]), xpoints, fitparams[i], no_errors, fitparam_errs[i])
        for i in range(NPARAM)
    ]


    print "total chisquare = %s" % sum(f.GetChisquare() for f in fcns)
    print "total ndf = %s" % (jetmass_cut.GetNbinsX() * (jetmass_cut.GetNbinsY() - NPARAM))



    import pdb; pdb.set_trace()


if __name__ == "__main__":
    main()
