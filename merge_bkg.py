import sys
import os
import argparse

from operator import itemgetter

from ROOT import TH1, TH3F, TH2F, TH1F, TFile, TLorentzVector

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


def leading_subleading(evt):
    """
    Return the indices of the leading and subleading jets in the event. Raise ValueError
    if evt contains <2 jets
    """
    sort_order = [i[0] for i in sorted(enumerate(evt.JetPt), key=itemgetter(1))]
    i, j = sort_order[-1], sort_order[-2]
    while evt.JetM[i] == evt.JetM[j]:
        j -= 1
    if j < 0:
        raise ValueError("Event contains <2 jets")
    return i, j
    

def masses(evt, i, j):
    """
    Return the i'th jet mass, the j'th jet mass, and their invariant mass
    """
    i, j = leading_subleading(evt)
    lead_vector = TLorentzVector()
    lead_vector.SetPtEtaPhiM(evt.JetPt[i], evt.JetEta[i], evt.JetPhi[i], evt.JetM[i])
    subl_vector = TLorentzVector()
    subl_vector.SetPtEtaPhiM(evt.JetPt[j], evt.JetEta[j], evt.JetPhi[j], evt.JetM[j])
    return evt.JetM[i], evt.JetM[j], (lead_vector + subl_vector).Mag()


def main(args):
    lumi = 40e6 # = 40 fb^-1 (there are 6 orders of magnitude between femto- and nano-)
    normalization = {
        # i: xsec (nb) * filt_eff * kfactor / nevents * lumi (nb^-1)
        7: .016215 * 3.9216e-4 * 1 / 1770193 * lumi,
        6: .25753 * 9.4106e-4 * 1 / 1893389 * lumi,
        5: 4.5535 * 9.2196e-4 * 1 / 7977567 * lumi,
        4: 254.63 * 5.3015e-4 * 1 / 7975217 * lumi,
        3: 26454 * 3.1956e-4 * 1 / 7349799 * lumi,
    }

    TH1.SetDefaultSumw2()

    # "Regular" histograms
    m1 = TH1F("jet1m", "Leading Jet Mass", mj_max/mj_binsize, 0, mj_max)
    m2 = TH1F("jet2m", "Subleading Jet Mass", mj_max/mj_binsize, 0, mj_max)
    mjj = TH1F("dijetmass", "Dijet Mass", mjj_max/mjj_binsize, 0, mjj_max)
    jetm = TH3F("jetmass", "Jet Masses",
                mj_max/mj_binsize, 0, mj_max,
                mj_max/mj_binsize, 0, mj_max,
                mjj_max/mjj_binsize, 0, mjj_max)
    pt1 = TH1F("jet1pt", "Leading Jet pT", 50, 0, 1500)
    pt2 = TH1F("jet2pt", "Subleading Jet pT", 50, 0, 1500)

    # histograms for events where m1 ~ m2
    m_avg = TH1F("jetm_avg", "Avg jetmass where m1 ~ m2", mj_max/mj_binsize, 0, mj_max)
    mjj_avg = TH1F("mjj_avg", "Dijet mass where m1 ~ m2", mjj_max/mjj_binsize, 0, mjj_max)
    jetm_avg = TH2F("jetmass_avg", "Jet masses where m1 ~ m2",
                    mj_max/mj_binsize, 0, mj_max,
                    mjj_max/mjj_binsize, 0, mjj_max)

    # histograms separated by qq/qg/gg events. Index is number of gluons (0, 1, or 2)
    separated_jetm = {
        0: TH2F("jetm_qq", "Avg jet mass (m1 ~ m2) for qq events",
                mj_max/mj_binsize, 0, mj_max,
                mjj_max/mjj_binsize, 0, mjj_max),
        1: TH2F("jetm_qg", "Avg jet mass (m1 ~ m2) for qg events",
                mj_max/mj_binsize, 0, mj_max,
                mjj_max/mjj_binsize, 0, mjj_max),
        2: TH2F("jetm_gg", "Avg jet mass (m1 ~ m2) for gg events",
                mj_max/mj_binsize, 0, mj_max,
                mjj_max/mjj_binsize, 0, mjj_max),
    }
    separated_mjj = {
        0: TH1F("mjj_qq", "Dijet mass for qq events", mjj_max/mjj_binsize, 0, mjj_max),
        1: TH1F("mjj_qg", "Dijet mass for qg events", mjj_max/mjj_binsize, 0, mjj_max),
        2: TH1F("mjj_gg", "Dijet mass for gg events", mjj_max/mjj_binsize, 0, mjj_max),
    }
    separated_m1 = {
        0: TH1F("jet1m_qq", "Leading jet mass for qq events", mj_max/mj_binsize, 0, mj_max),
        1: TH1F("jet1m_qg", "Leading jet mass for qg events", mj_max/mj_binsize, 0, mj_max),
        2: TH1F("jet1m_gg", "Leading jet mass for gg events", mj_max/mj_binsize, 0, mj_max),
    }
    separated_m2 = {
        0: TH1F("jet2m_qq", "Subleading jet mass for qq events", mj_max/mj_binsize, 0, mj_max),
        1: TH1F("jet2m_qg", "Subleading jet mass for qg events", mj_max/mj_binsize, 0, mj_max),
        2: TH1F("jet2m_gg", "Subleading jet mass for gg events", mj_max/mj_binsize, 0, mj_max),
    }
    separated_pt1 = {
        0: TH1F("jet1pt_qq", "Leading jet pT for qq events", 50, 0, 1500),
        1: TH1F("jet1pt_qg", "Leading jet pT for qg events", 50, 0, 1500),
        2: TH1F("jet1pt_gg", "Leading jet pT for gg events", 50, 0, 1500),
    }
    separated_pt2 = {
        0: TH1F("jet2pt_qq", "Subleading jet pT for qq events", 50, 0, 1500),
        1: TH1F("jet2pt_qg", "Subleading jet pT for qg events", 50, 0, 1500),
        2: TH1F("jet2pt_gg", "Subleading jet pT for gg events", 50, 0, 1500),
    }

    for sample, sample_norm in normalization.iteritems():
        directory = "data/user.vbaratha.Pythia8EvtGen_A14NNPDF23LO_jetjet_JZ%sW.%s_JZ%s_histOutput.root" % (sample, args.jobname, sample)
        print "doing one dir"
        for f in iter_outfiles(directory):
            print "doing one file"
            tree = f.Get("aTree")
            for evt in tree:
                try:
                    i, j = leading_subleading(evt)
                    _m1, _m2, _mjj = masses(evt, i, j)
                    p1, p2 = evt.JetPt[i], evt.JetPt[j]
                    wt = evt.weight * sample_norm

                    # Fill "regular" histograms
                    m1.Fill(_m1, wt)
                    m2.Fill(_m2, wt)
                    mjj.Fill(_mjj, wt)
                    jetm.Fill(_m1, _m2, _mjj, wt)
                    pt1.Fill(p1, wt)
                    pt2.Fill(p2, wt)

                    # Fill histograms separated by qq/qg/gg events
                    num_gluons = sum(1 for pdgid in [evt.JetType[i], evt.JetType[j]] if pdgid == 21)
                    separated_mjj[num_gluons].Fill(_mjj, wt)
                    separated_m1[num_gluons].Fill(_m1, wt)
                    separated_m2[num_gluons].Fill(_m2, wt)
                    separated_pt1[num_gluons].Fill(p1, wt)
                    separated_pt2[num_gluons].Fill(p2, wt)

                    # Fill histograms for events where m_j1 ~ m_j2
                    if abs(_m1 - _m2) < MASS_DIFF_CUTOFF:
                        mavg = (_m1 + _m2) / 2
                        m_avg.Fill(mavg, wt)
                        mjj_avg.Fill(_mjj, wt)
                        jetm_avg.Fill(mavg, _mjj, wt)
                        separated_jetm[num_gluons].Fill(mavg, _mjj, wt)
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
    for i in range(3):
        separated_jetm[i].Write()
        separated_mjj[i].Write()
        separated_m1[i].Write()
        separated_m2[i].Write()
        separated_pt1[i].Write()
        separated_pt2[i].Write()

    f.Close()
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Merge background samples from Grid job output")
    parser.add_argument("--jobname", type=str, required=True,
                        help="eg Jun30_1445, part of what you called the job when it was run")
    parser.add_argument("--outfile", type=str, default="merged.root",
                        help="output file name")
    args = parser.parse_args()
    main(args)
