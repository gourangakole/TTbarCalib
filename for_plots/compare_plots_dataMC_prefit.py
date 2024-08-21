#==============
# Last used:
# python3 compare_plots_dataMC_prefit.py --inputDir fit_dir_08Aug2024_Summer23BPix_v3
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
opts = parser.parse_args()

#from ROOT import *
ROOT.gROOT.SetBatch(True)
colors = {
    'nom'    : ROOT.kRed,
    'jesup'  : ROOT.kGreen,
    'jesdn'  : ROOT.kBlue,
    '800'    : ROOT.kCyan,
    '1000'   : ROOT.kOrange,
    'TTTo1L' : ROOT.kViolet-4,
    'b'      : ROOT.kRed,
    'c'      : ROOT.kGreen,
    'other'  : ROOT.kBlue,
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


def makePlot(inDir, tagger, hname, year="2018", isNorm=True):

    wRatio = True

    lumi = 9.450 #2023BPix lumi

    #Get histograms
    root_file = ROOT.TFile("../%s/kindisc_templates/%s.root"%(inDir,tagger))
    h_all = {}
    systs = ['nom'] #,'jesup','jesdn']
    flavs = ['b', 'c', 'other', 'data']

    for sys in systs:
        for flav in flavs:
            print ("adding histogram for: "+ sys + " and flav: "+ flav)
            htmp = flav+'_'+hname
            if sys != 'nom':
                htmp = hname+sys
            h_all[flav] = root_file.Get("%s"%htmp)

    if wRatio:
        # canvas = RatioCanvas(" "," ",41500)
        canvas = DataMCCanvas(" "," ", lumi*1000)
        canvas.ytitle = 'Events'
        canvas.xtitle = 'kinematic discriminator'
    else:
        canvas = SimpleCanvas(" "," ", lumi*1000)
        canvas.ytitle = 'Events'
        canvas.xtitle = 'kinematic discriminator'
    canvas.legend.setPosition(0.7, 0.7, 0.9, 0.9)

    # Adding to canvas
    for i, key in enumerate(h_all):
        key = flavs[i]
        if key != 'data':
            h_all[key].Scale(lumi*1000)
            canvas.addStacked(h_all[key], title = "%s"%(key), color = colors[key])
        else:
            canvas.addObs(h_all[key])
        print ("Name:-> ", h_all[key].GetName(), " and Integral: ->", h_all[key].Integral())

        # if key != 'nom':
        #      h_all[key].Scale(h_all['nom'].Integral()/h_all[key].Integral()) #normalize histogram to nominal
        # canvas.legend.add(h_all[key], title = key, opt = 'LP', color = colors[key], fstyle = 0, lwidth = 2)
        # canvas.addHistogram(h_all[key], drawOpt = 'HIST E')

    # Add text
    canvas.addText("=2 jets", 0.25, 0.7, 0.28, 0.8)
    canvas.addText("=3 jets", 0.55, 0.7, 0.58, 0.8)
    canvas.addText("=4 jets", 0.85, 0.7, 0.88, 0.8)

    canvas.applyStyles()
    if wRatio:
        canvas.printWeb(inDir, tagger+"_"+hname, logy = False)
    else:
        canvas.printWeb(inDir, tagger+"_"+hname, logy = False)

# Main
if __name__ == "__main__":
    # plottting
    taggers = ['DeepFlavourBDisc']

    # histogramming naming convension:
    # flavs = ['b', 'c', 'other', 'data']
    # pass = [1-5] (WP's for a tagger)
    # slice = [0-5 (sometime 6)] : it represents the pt bins of the jet

    histos = ['pass1_slice0','pass1_slice1','pass1_slice2','pass1_slice3','pass1_slice4','pass1_slice5','pass1_slice6']
    for tag in taggers:
        for hist in histos:
            makePlot(opts.inputDir, tag, hist)
