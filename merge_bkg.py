import sys
import os
import argparse

from operator import itemgetter

from ROOT import TH3F, TH2F, TH1D, TFile, TLorentzVector

from histoparams import *

"""
Merge outfiles from grid jobs into one final histogram, including proper event and sample weighting
"""

MASS_DIFF_CUTOFF = 25

def iter_outfiles(dirname):
    for fn in os.listdir(dirname):
        if fn.endswith(".root"):
            f = TFile(os.path.join(dirname, fn), "READ")
            yield f
            f.Close()


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


def main(args):
    lumi = 40e6 # 6 orders of magnitude between femto- and nano-
    normalization = {
        # i: xsec (nb) * filt_eff * kfactor / nevents * lumi
        7: .016215 * 3.9216e-4 * 1 / 1770193 * lumi,
        6: .25753 * 9.4106e-4 * 1 / 1893389 * lumi,
        5: 4.5535 * 9.2196e-4 * 1 / 7977567 * lumi,
        4: 254.63 * 5.3015e-4 * 1 / 7975217 * lumi,
        3: 26454 * 3.1956e-4 * 1 / 7349799 * lumi,
    }

    m1 = TH1D("jet1m", "Leading Jet Mass", mj_max/mj_binsize, 0, mj_max)
    m2 = TH1D("jet2m", "Subleading Jet Mass", mj_max/mj_binsize, 0, mj_max)
    mjj = TH1D("dijetmass", "Dijet Mass", mjj_max/mjj_binsize, 0, mjj_max)
    jetm = TH3F("jetmass", "Jet Masses",
                mj_max/mj_binsize, 0, mj_max,
                mj_max/mj_binsize, 0, mj_max,
                mjj_max/mjj_binsize, 0, mjj_max)
    pt1 = TH1D("jet1pt", "Leading Jet pT", 50, 0, 1500)
    pt2 = TH1D("jet2pt", "Subleading Jet pT", 50, 0, 1500)

    # histograms for events where m1 ~ m2
    m_avg = TH1D("jetm_avg", "Avg jetmass where m1 ~ m2", mj_max/mj_binsize, 0, mj_max)
    mjj_avg = TH1D("mjj_avg", "Dijet mass where m1 ~ m2", mjj_max/mjj_binsize, 0, mjj_max)
    jetm_avg = TH2F("jetmass_avg", "Jet masses where m1 ~ m2",
                    mj_max/mj_binsize, 0, mj_max,
                    mjj_max/mjj_binsize, 0, mjj_max)

    for sample, sample_norm in normalization.iteritems():
        directory = "data/user.vbaratha.Pythia8EvtGen_A14NNPDF23LO_jetjet_JZ%sW.%s_JZ%s_histOutput.root" % (sample, args.jobname, sample)
        print "doing one dir"
        for f in iter_outfiles(directory):
            print "doing one file"
            tree = f.Get("aTree")
            for evt in tree:
                try:
                    _m1, _m2, _mjj, p1, p2 = masses(evt)
                    wt = evt.weight * sample_norm
                    m1.Fill(_m1, wt)
                    m2.Fill(_m2, wt)
                    mjj.Fill(_mjj, wt)
                    jetm.Fill(_m1, _m2, _mjj, wt)
                    pt1.Fill(p1, wt)
                    pt2.Fill(p2, wt)
                    if abs(_m1 - _m2) < MASS_DIFF_CUTOFF:
                        mavg = (_m1 + _m2) / 2
                        m_avg.Fill(mavg, wt)
                        mjj_avg.Fill(_mjj, wt)
                        jetm_avg.Fill(mavg, _mjj, wt)
                except IndexError:
                    pass

    f = TFile(args.outfile, "RECREATE")

    m1.Write()
    m2.Write()
    mjj.Write()
    jetm.Write()
    pt1.Write()
    pt2.Write()
    m_avg.Write()
    mjj_avg.Write()
    jetm_avg.Write()

    f.Close()
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Merge background samples from Grid job output")
    parser.add_argument("--jobname", type=str, required=True,
                        help="eg Jun30_1445, part of what you called the job when it was run")
    parser.add_argument("--outfile", type=str, default="merged.root",
                        help="output file name")
    args = parser.parse_args()
    main(args)
