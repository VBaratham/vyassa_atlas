import sys
import array

from ROOT import TF1, TFile, TGraphErrors

from utils import cut_histo, slice_histo_y, slice_by_slice_fit
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
    jetmass = f.Get("jetmass_avg")
    jetmass_cut = cut_histo(jetmass,
                            mj_fit_range[0]/mj_binsize, mj_fit_range[1]/mj_binsize,
                            mjj_fit_range[0]/mjj_binsize, mjj_fit_range[1]/mjj_binsize,
                            "jetmass_cut", "Jet masses after cut")

    fcns, fit_histo = slice_by_slice_fit(jetmass_cut, get_1d_fit_fcn_b)

    diff_histo = jetmass_cut - fit_histo

    # NOTE: this is now done by utils.slice_by_slice_fit, but this graphs the fit params too
    # # Fit the 1d function to each slice and store the fit parameters
    # xpoints = array.array('d')
    # fitparams = [array.array('d') for i in range(NPARAM)]
    # fitparam_errs = [array.array('d') for i in range(NPARAM)]
    # for x in range(jetmass_cut.GetNbinsX()):
    #     sliced_histo = slice_histo_y(jetmass_cut, x+1, "slice_%s" % (x+1), "M_jj, slice %s" % (x+1))
    #     fit_fcn = get_1d_fit_fcn_b(sliced_histo, x+1)
    #     sliced_histo.Fit(fit_fcn)
    #     print "Slice %s chisq = %s" % (x+1, fit_fcn.GetChisquare())
    #     print
    #     print

    #     if fit_fcn.GetChisquare() < 98.1:  # 93.1 is p=.005 for 61 df
    #         xpoints.append(mj_fit_range[0] + mj_binsize * x)
    #         for i in range(NPARAM):
    #             fitparams[i].append(fit_fcn.GetParameter(i))
    #             fitparam_errs[i].append(fit_fcn.GetParError(i))

    print "total chisquare = %s" % sum(f.GetChisquare() for f in fcns)
    print "total ndf = %s" % (jetmass_cut.GetNbinsX() * (jetmass_cut.GetNbinsY() - NPARAM))

    import pdb; pdb.set_trace()


    # Histogram/graph fit parameters
    # xpoints = array.array('d', [float(mj_fit_range[0] + mj_binsize * i)
    #                             for i in range(len(fitparams[0]))])
    no_errors = array.array('d', [0.0 for i in range(len(fitparams[0]))])
    fitparam_graphs = [
        TGraphErrors(len(fitparams[i]), xpoints, fitparams[i], no_errors, fitparam_errs[i])
        for i in range(NPARAM)
    ]

    # Figure out parameters of a linear fit to each param. THIS DIDNT WORK WELL
    # for i in range(NPARAM):
    #     print "Doing linear fit for param [%s]:" % i
    #     linear_param_fit_fcn = TF1("param %s" % i, "[0]*(x/13000)+[1]", *mj_fit_range)
    #     fitparam_graphs[i].Fit(linear_param_fit_fcn)
    #     print
    #     print
    #     # print "Param [%s] ax+b: a = %s, b = %s"
    #     # % (i, linear_param_fit_fcn.GetParameter(0), linear_param_fit_fcn.GetParameter(1))


    import pdb; pdb.set_trace()


    
    
if __name__ == "__main__":
    main()
