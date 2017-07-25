import array
from itertools import product

from ROOT import TH1F, TH2F, TH3F

chisq_contrib = lambda obs, exp, err: (obs-exp)**2/err**2

def chisq(h1, h2):
    """
    Manual chi square calculation b/c idk what ROOT does
    h1 = observed (errors used from this histo)
    h2 = expected
    NOTE: Returns same thing as TF2.GetChisquare()
    """

    if isinstance(h1, TH1F):
        assert isinstance(h2, TH1F), "h1 and h2 must be the same type of histogram"
        return chisq1d(h1, h2)

    if isinstance(h1, TH2F):
        assert isinstance(h2, TH2F), "h1 and h2 must be the same type of histogram"
        return chisq2d(h1, h2)

    if isinstance(h1, TH3F):
        assert isinstance(h2, TH3F), "h1 and h2 must be the same type of histogram"
        return chisq3d(h1, h2)

def chisq1d(h1, h2):
    assert h1.GetNBinsX() == h2.GetNBinsX(), "histogram dimensions must agree"

    return sum(
        chisq_contrib(h1.GetBinContent(x+1), h2.GetBinContent(x+1), h1.GetBinError(x+1))
        for x in range(h1.GetNBinsX())
    )
    

def chisq2d(h1, h2):
    assert h1.GetNbinsX() == h2.GetNbinsX(), "histogram dimensions must agree"
    assert h1.GetNbinsY() == h2.GetNbinsY(), "histogram dimensions must agree"
    
    xbins = [x+1 for x in range(h1.GetNbinsX())]
    ybins = [y+1 for y in range(h1.GetNbinsY())]
    return sum(
        chisq_contrib(h1.GetBinContent(*_bin), h2.GetBinContent(*_bin), h1.GetBinError(*_bin))
        for _bin in product(xbins, ybins)
    )

def chisq3d(h1, h2):
    assert h1.GetNbinsX() == h2.GetNbinsX(), "histogram dimensions must agree"
    assert h1.GetNbinsY() == h2.GetNbinsY(), "histogram dimensions must agree"
    assert h1.GetNbinsZ() == h2.GetNbinsZ(), "histogram dimensions must agree"
    
    xbins = [x+1 for x in range(h1.GetNbinsX())]
    ybins = [y+1 for y in range(h1.GetNbinsY())]
    zbins = [z+1 for z in range(h1.GetNbinsZ())]
    return sum(
        chisq_contrib(h1.GetBinContent(*_bin), h2.GetBinContent(*_bin), h1.GetBinError(*_bin))
        for _bin in product(xbins, ybins, zbins)
    )
    
def get_xybins(histo):
    xbins = array.array('d', [-1 for i in range(histo.GetNbinsX())])
    histo.GetXaxis().GetLowEdge(xbins)
    xbins.append(histo.GetXaxis().GetXmax())
    
    ybins = array.array('d', [-1 for i in range(histo.GetNbinsY())])
    histo.GetYaxis().GetLowEdge(ybins)
    ybins.append(histo.GetYaxis().GetXmax())

    return xbins, ybins

def cut_histo(histo, xmin, xmax, ymin, ymax, name, title):
    """
    Create and return a copy of histo restricted to bins [xmin, xmax), [ymin, ymax)
    # TODO: Check for fencepost errors
    """
    xbins, ybins = get_xybins(histo)

    # TODO: use GetArray() instead of GetBinContent(x, y)?

    new_histo = TH2F(name, title,
                     xmax-xmin, xbins[xmin:xmax+1],
                     ymax-ymin, ybins[ymin:ymax+1])

    for x in range(xmin, xmax):
        for y in range(ymin, ymax):
            new_histo.SetBinContent(x-xmin+1, y-ymin+1, histo.GetBinContent(x, y))
            new_histo.SetBinError(x-xmin+1, y-ymin+1, histo.GetBinError(x, y))

    return new_histo

def slice_histo_y(histo, x, name, title):
    """
    Cut a 1d slice out of a TH2F along the y axis at the given x bin
    """
    ybins = array.array('d', [-1 for i in range(histo.GetNbinsY())])
    histo.GetYaxis().GetLowEdge(ybins)
    ybins.append(histo.GetYaxis().GetXmax())

    new_histo = TH1F(name, title, histo.GetNbinsY(), ybins)

    for y in range(histo.GetNbinsY()):
        new_histo.SetBinContent(y+1, histo.GetBinContent(x, y+1))
        new_histo.SetBinError(y+1, histo.GetBinError(x, y+1))

    return new_histo

def add_slice(histo, slice_histo, x):
    """
    add slice_histo (TH1F) to histo (TH2F) at the given x bin
    """
    assert histo.GetNbinsY() == slice_histo.GetNbinsX()
    for y in range(histo.GetNbinsY()):
        histo.SetBinContent(x, y+1, histo.GetBinContent(x, y+1) + slice_histo.GetBinContent(y+1))

def slice_by_slice_fit(histo, fit_fcn_factory, name_fmt="slice_%s", title_fmt="M_jj, slice %s"):
    """
    Fit slice by slice (along y) and return the TF1 for each x bin and a histogram of the fit
    fit_fcn_factory: a function that takes (sliced_histo, i) and returns the TF1 to fit to that slice
    """
    xbins, ybins = get_xybins(histo)
    fit_histo = TH2F("slicebyslicefit", "Fit", histo.GetNbinsX(), xbins, histo.GetNbinsY(), ybins)
    fcns = []

    for x in range(histo.GetNbinsX()):
        sliced_histo = slice_histo_y(histo, x+1, name_fmt % (x+1), title_fmt % (x+1))
        fit_fcn = fit_fcn_factory(sliced_histo, x+1)
        fit_fcn.SetNpx(sliced_histo.GetNbinsX())
        sliced_histo.Fit(fit_fcn)
        fcns.append(fit_fcn)
        add_slice(fit_histo, fit_fcn.GetHistogram(), x+1)

        
    return fcns, fit_histo

        
        
