import array
from itertools import product

from ROOT import TH2D

def chisq(h1, h2):
    """
    Manual chi square calculation b/c idk what ROOT does
    h1 = observed
    h2 = expected
    """
    assert h1.GetNbinsX() == h2.GetNbinsX()
    assert h1.GetNbinsY() == h2.GetNbinsY()
    
    xbins = [x+1 for x in range(h1.GetNbinsX())]
    ybins = [y+1 for y in range(h1.GetNbinsY())]
    contrib = lambda obs, exp: (obs-exp)**2/obs
    return sum(
        contrib(h1.GetBinContent(*_bin), h2.GetBinContent(*_bin))
        for _bin in product(xbins, ybins)
    )


def cut_histo(histo, xmin, xmax, ymin, ymax, name, title):
    """
    Create and return a copy of histo restricted to bins [xmin, xmax), [ymin, ymax)
    # TODO: Check for fencepost errors
    """
    xbins = array.array('d', [-1 for i in range(histo.GetNbinsX())])
    histo.GetXaxis().GetLowEdge(xbins)
    
    ybins = array.array('d', [-1 for i in range(histo.GetNbinsY())])
    histo.GetYaxis().GetLowEdge(ybins)

    # TODO: use GetArray() instead of GetBinContent(x, y)?

    new_histo = TH2D(name, title,
                     xmax-xmin-1, xbins[xmin:xmax],
                     ymax-ymin-1, ybins[ymin:ymax])

    for x in range(xmin, xmax):
        for y in range(ymin, ymax):
            new_histo.SetBinContent(x-xmin+1, y-ymin+1, histo.GetBinContent(x, y))

    return new_histo
