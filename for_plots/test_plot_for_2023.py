#==============
# Last used:
# python3 test_plot_for_2023.py
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
from plotstyle import SimpleCanvas
from plotstyle import RatioCanvas


import ROOT
#from ROOT import *
ROOT.gROOT.SetBatch(True)

histo_xtitle = {
    'emu_leadjpt'   : "Leading jet p_{T} [GeV]",
    'emu_leadjeta'  : "Pseudo-rapidity",
    'emu_njets'     : "Jet multiplicity",
    'emu_npvGood'   : "No. of Good PVs",
    'emu_npv'       : "No. of PVs",
    'emu_met'       : "Puppi MET [GeV]"
}
def makePlot(mass, hname, xmin, xmax, isNorm=True):
    
    wRatio = True
    inputDir = '/afs/cern.ch/user/g/gkole/work/BTV_Calibration/CMSSW_13_0_6/src/TTbarCalib/for_plots/2023preBPix_v3/'
    # Get histograms
    # file_tt = ROOT.TFile("%s/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8_0.root"%(inputDir)) #single file
    # file_tt = ROOT.TFile("%s/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8_10files.root"%(inputDir))
    file_tt = ROOT.TFile("%s/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8.root"%(inputDir))
    
    file_data = ROOT.TFile("%s/MuonEGRun2023C-22Sep2023.root"%(inputDir))
    
    h_TTto2L = file_tt.Get("%s"%hname)
    h_TTto2L_total_events = file_tt.Get("events")
    h_MuonEG = file_data.Get("%s"%hname)
    

    # hmm.Rebin(5)
    
    h_TTto2L.SetLineColor(ROOT.kGreen)
    h_MuonEG.SetLineColor(ROOT.kBlack)
    lumiC = 5.0707
    lumiD = 3.0063
    lumi = 17.650 #2023 lumi
    
    # print "hmm.Integral(): ", hmm.Integral()
    if isNorm:
        h_TTto2L.Scale(h_MuonEG.Integral()/h_TTto2L.Integral())
    else:
        h_TTto2L.Scale((96.9*lumi*1000)/h_TTto2L_total_events.GetBinContent(1)) # 96.9 is TTto2L XS
    
    if wRatio:
        canvas = RatioCanvas("","",lumi*1000)
        canvas.xtitle = histo_xtitle[hname]
    else:
        canvas = SimpleCanvas("","",lumi*1000)
        canvas.xtitle = histo_xtitle[hname]

    #Legend position
    canvas.legend.setPosition(0.7, 0.7, 0.9, 0.9)
    canvas.legend.add('h_TTto2L', title = 'TTTo2L', opt = 'LP', color = ROOT.kGreen, fstyle = 3003, lwidth = 3)
    canvas.legend.add('h_MuonEG', title = 'Data', opt = 'P', color = ROOT.kBlack,  fstyle = 3003, lwidth = 0)
    
    canvas.addHistogram(h_TTto2L, drawOpt = 'HIST E')
    canvas.addHistogram(h_MuonEG, drawOpt = 'E1')
    
    canvas.applyStyles()
    if isNorm:
        canvas.printWeb('2023_Norm_v3', hname, logy = False)
    else:
        canvas.printWeb('2023_v3', hname, logy = False)

if __name__ == "__main__":
    makePlot("1000","emu_leadjpt",0,500,True)
    makePlot("1000","emu_leadjpt",0,500,False)
    makePlot("1000","emu_leadjeta",0,500,True)
    makePlot("1000","emu_leadjeta",0,500,False)
    makePlot("1000","emu_njets",0,500,True)
    makePlot("1000","emu_njets",0,500,False)
    makePlot("1000","emu_npvGood",0,50,True)
    makePlot("1000","emu_npvGood",0,50,False)
    makePlot("1000","emu_npv",0,50,True)
    makePlot("1000","emu_npv",0,50,False)
    makePlot("1000","emu_met",0,50,True)
    makePlot("1000","emu_met",0,50,False)
    
    
