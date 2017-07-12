import array

from ROOT import TH2D

# def chisq(histo, fcn, xmin, xmax, ymin, ymax):
#     """
#     Assumes constant width bins
#     """
#     xwidth = (histo.GetXaxis().GetXmax() - histo.GetXaxis().GetXmin()) / histo.GetNbinsX()
#     ywidth = (histo.GetYaxis().GetYmax() - histo.GetYaxis().GetYmin()) / histo.GetNbinsY()

def cut_histo(histo, xmin, xmax, ymin, ymax, name, title):
    """
    Create and return a copy of histo restricted to bins [xmin, xmax), [ymin, ymax)
    # TODO: Check for fencepost errors
    """
    xbins = array.array('d', [-1 for i in range(histo.GetNbinsX())])
    histo.GetXaxis().GetLowEdge(xbins)
    
    
    ybins = array.array('d', [-1 for i in range(histo.GetNbinsY())])
    histo.GetYaxis().GetLowEdge(ybins)

    # TODO: use GetArray() instead of GetBinContent(x, y)
    
    new_histo = TH2D(name, title,
                     xmax-xmin-1, xbins[xmin:xmax],
                     ymax-ymin-1, ybins[ymin:ymax])

    for x in range(xmin, xmax):
        for y in range(ymin, ymax):
            new_histo.SetBinContent(x-xmin+1, y-ymin+1, histo.GetBinContent(x, y))

    return new_histo
    
