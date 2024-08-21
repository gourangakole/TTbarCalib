#==============
# Last used:
# python3 compare_plots.py --inputDir fit_dir_08Aug2024_Summer23BPix_v3 --syst "isrDef"
#==============

#!/usr/bin/env python

import sys
import os
import array
import shutil

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
print (thisdir)
#import config
#from datasets import allsamples
#from plotstyle import SimpleCanvas
# sys.path.append('../../python')
# from plotstyle import *
from plotstyle import SimpleCanvas
from plotstyle import RatioCanvas
from plotstyle import DataMCCanvas
import ROOT


from argparse import ArgumentParser
parser = ArgumentParser()

parser.add_argument("--inputDir", "-i", dest="inputDir", default=None,
                    help="Provide inputDir containing histograms")
parser.add_argument('-s', '--syst',     dest='syst',          help='name of the systematic',    default='jes')

opts = parser.parse_args()

# Name of the systematics (w/o 'up,dn' suffix)
systs = ['jes','jer','isrDef','fsrDef']

if opts.syst not in systs:
    raise ValueError(f"Error: '{opts.syst}' is not in the list, choose from '{', '.join(systs)}'")

#from ROOT import *
ROOT.gROOT.SetBatch(True)
colors = {
    'nom'       : ROOT.kRed,
    'jesup'     : ROOT.kGreen,
    'jesdn'     : ROOT.kBlue,
    'jerup'     : ROOT.kGreen,
    'jerdn'     : ROOT.kBlue,
    'isrDefup'  : ROOT.kCyan,
    'isrDefdn'  : ROOT.kViolet,
    'fsrDefup'  : ROOT.kOrange,
    'fsrDefdn'  : ROOT.kPink+9,
    '1000'   : ROOT.kOrange,
    'TTTo1L' : ROOT.kViolet-4,
    'zg'     :"#99ffaa",
    'wg'     :"#99eeff",
    'efake'  :"#ffee99",
    'hfake'  :"#bbaaff",
    'halo'   :"#ff9933",
    'spike'  :"#666666",
    'vvg'    :"#ff4499",
    'gjets'  :"#ffaacc",
    'minor'  :"#bb66ff",
    'top'    :"#5544ff",
    'zjets'  :"#99ffaa",
    'wjets'  :"#222222",
    'gg'     :"#bb66ff"
    }

histo_xtitle = {
    'DeepB_loose_j1_pt'  : "Leading b-jet p_{T}",
    'DeepB_loose_j2_pt'  : "2^{nd} leading b-jet p_{T}",
    'DeepB_loose_j3_pt'  : "3^{rd} leading b-jet p_{T}",
    'DeepB_loose_j1_eta' : "Leading b-jet #eta",
    'DeepB_loose_j2_eta' : "2^{nd} leading b-jet #eta",
    'DeepB_loose_j3_eta' : "3^{rd} leading b-jet #eta",
    'l1_pt'              : "Leading lepton p_{T}",
    'l1_eta'             : "Leading lepton #eta",
    'j1_pt'              : "Leading jet p_{T}",
    'MET_T1Smear_pt'     : "#slash{E}_{T} [GeV]",
    'j2_pt'              : "2^{nd} leading jet p_{T}",
    'j3_pt'              : "3^{rd} leading jet p_{T}",
    'j1_eta'             : "Leading jet #eta",
    'j2_eta'             : "2^{nd} leading jet #eta",
    'j3_eta'             : "3^{rd} leading jet #eta"
}


def makePlot(inDir, tagger, hname, syst, year="2018", isNorm=True):

    wRatio = True

    lumi = 9.450 #2023BPix lumi

    #Get histograms
    root_file = ROOT.TFile("../%s/kindisc_templates/%s.root"%(inDir,tagger))
    h_all = {}
    # systs = ['nom','jesup','jesdn','isrDefup','isrDefdn','fsrDefup','fsrDefdn']

    systs = ['nom',syst+'up',syst+'dn']
    print (100*"=")
    print (systs)

    for sys in systs:
        print ("adding histogram for: "+ sys)
        htmp = hname
        if sys != 'nom':
            htmp = hname+sys
        h_all[sys] = root_file.Get("%s"%htmp)

    if wRatio:
        canvas = RatioCanvas(" "," ",lumi*1000)
        # canvas = DataMCCanvas(" "," ", 41500)
        canvas.ytitle = 'Events'
        canvas.xtitle = 'kinematic discriminator'
    else:
        canvas = SimpleCanvas(" "," ",lumi*1000)
        canvas.ytitle = 'Events'
        canvas.xtitle = 'kinematic discriminator'
    canvas.legend.setPosition(0.7, 0.7, 0.9, 0.9)

    # Adding to canvas
    for i, key in enumerate(h_all):
        key = systs[i]
        print ("sample:-> ", key, " and Name: ->", h_all[key].GetName())
        h_all[key].Scale(lumi*1000)
        if key != 'nom':
             h_all[key].Scale(h_all['nom'].Integral()/h_all[key].Integral()) #normalize histogram to nominal
        canvas.legend.add(h_all[key], title = key, opt = 'LP', color = colors[key], fstyle = 0, lwidth = 2)
        canvas.addHistogram(h_all[key], drawOpt = 'HIST E')

    # Add text
    canvas.addText("=2 jets", 0.25, 0.7, 0.28, 0.8)
    canvas.addText("=3 jets", 0.55, 0.7, 0.58, 0.8)
    canvas.addText("=4 jets", 0.85, 0.7, 0.88, 0.8)

    canvas.applyStyles()
    if wRatio:
        canvas.printWeb(inDir, tagger+"_"+hname+"_"+syst, logy = False)
    else:
        canvas.printWeb(inDir, tagger+"_"+hname+"_"+syst, logy = False)

# Main
if __name__ == "__main__":
    # plottting
    taggers = ['DeepFlavourBDisc']

    # histogramming naming convension:
    # flav = [b, c, other]
    # pass = [1-5] (WP's for a tagger)
    # slice = [0-5 (sometime 6)] : it represents the pt bins of the jet

    histos = ['b_pass1_slice0'] #,'b_pass1_slice1','b_pass1_slice2','b_pass1_slice3','b_pass1_slice4','b_pass1_slice5']
    for tag in taggers:
        for hist in histos:
            makePlot(opts.inputDir, tag, hist, opts.syst)
