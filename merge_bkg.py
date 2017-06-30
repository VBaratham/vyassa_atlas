from ROOT import TH3D,TH1D, TFile, TLorentzVector
import sys, os
from operator import itemgetter

"""
Merge outfiles from grid jobs into one final histogram, including proper event and sample (TODO) weighting
"""

def iter_outfiles(dirname):
    for fn in os.listdir(dirname):
        if fn.endswith(".root"):
            yield TFile(os.path.join(dirname, fn), "READ")

def masses(evt):
    sort_order = [i[0] for i in sorted(enumerate(evt.JetPt), key=itemgetter(1))]
    i, j = sort_order[-1], sort_order[-2]
    while evt.JetM[i] == evt.JetM[j]:
        j -= 1
    lead_vector = TLorentzVector()
    lead_vector.SetPtEtaPhiM(evt.JetPt[i], evt.JetEta[i], evt.JetPhi[i], evt.JetM[i])
    subl_vector = TLorentzVector()
    subl_vector.SetPtEtaPhiM(evt.JetPt[j], evt.JetEta[j], evt.JetPhi[j], evt.JetM[j])
    return evt.JetM[i], evt.JetM[j], (lead_vector + subl_vector).Mag(), evt.JetPt[i], evt.JetPt[j]

def main():

    m1 = TH1D("jet1m", "Leading Jet Mass", 50, 0, 600)
    m2 = TH1D("jet2m", "Subleading Jet Mass", 50, 0, 500)
    pt1 = TH1D("jet1pt", "Leading Jet pT", 50, 0, 3000)
    pt2 = TH1D("jet2pt", "Subleading Jet pT", 50, 0, 3000)
    mjj = TH1D("dijetmass", "Dijet Mass", 100, 0, 10000)
    jetm = TH3D("jetmass", "Jet Masses", 50, 0, 500, 50, 0, 500, 100, 0, 10000)

    # TODO: store/pull kfactor, xsec, filtering eff
    for i, f in enumerate(iter_outfiles(sys.argv[1])):
        tree = f.Get("aTree")
        for evt in tree:
            try:
                leading, subleading, dijet, p1, p2 = masses(evt)
                m1.Fill(leading, evt.weight)
                m2.Fill(subleading, evt.weight)
                mjj.Fill(dijet, evt.weight)
                jetm.Fill(leading, subleading, dijet, evt.weight)
                pt1.Fill(p1, evt.weight)
                pt2.Fill(p2, evt.weight)
            except IndexError:
                pass

    f = TFile("merged.root", "RECREATE")

    m1.Write()
    m2.Write()
    mjj.Write()
    jetm.Write()
    pt1.Write()
    pt2.Write()

    f.Close()
    

if __name__ == '__main__':
    main()
