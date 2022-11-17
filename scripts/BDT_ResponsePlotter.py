######################################
#      BDT_ResponsePlotter.py
######################################
#             JTW
#       IHEP Beijing, CERN
######################################
# Script to make BDT training plots
# from output TMVA_XXX.root files.
# Resulting plots:
# 1.) Overtraining plot.
#
######################################
# Usage: python BDT_ResponsePlotter.py
######################################

import ROOT
from ROOT import TFile, TTree, gDirectory, gROOT, TH1, TAttMarker, TLegend, TCanvas


def main():

    ptordered_classifiers = [0,1,2]
    for idx, x in enumerate(ptordered_classifiers):


	input_file_name='/afs/cern.ch/work/j/jthomasw/private/IHEP/BTV/CMSSW/UL16/CMSSW_10_6_20/src/RecoBTag/PerformanceMeasurements/test/TTbarCalib/training_v3/TMVA_BDT_UL16_v2_%s.root'%(x)
        input_file = TFile.Open(input_file_name)

        Histo_training_BDTRepsonse = ROOT.TH1D('Histo_training_BDTRepsonse','BDT Response (Train)',40,-1.0,1.0)
        Histo_testing_BDTRepsonse = ROOT.TH1D('Histo_testing_BDTRepsonse','BDT Response (Test)',40,-1.0,1.0)

        TrainTree = input_file.Get("TrainTree")
        TestTree = input_file.Get("TestTree")

        TrainTree.Project("Histo_training_BDTRepsonse","BDT")
        TestTree.Project("Histo_testing_BDTRepsonse","BDT")

        Histo_training_BDTRepsonse.SetMarkerStyle(20)
        Histo_testing_BDTRepsonse.SetMarkerStyle(22)

        Histo_training_BDTRepsonse.SetMarkerColor(4)
        Histo_testing_BDTRepsonse.SetMarkerColor(6)

        Histo_training_BDTRepsonse.SetFillStyle(3001)
        Histo_testing_BDTRepsonse.SetFillStyle(3001)

        Histo_training_BDTRepsonse.SetFillColor(4)
        Histo_testing_BDTRepsonse.SetFillColor(6)

        c1 = ROOT.TCanvas("c1","",1000,600)
        p1 = ROOT.TPad('p1','p1',0.0,0.2,1.0,1.0)
        p1.Draw()
        p1.SetRightMargin(0.1)
        p1.SetLeftMargin(0.15)
        p1.SetTopMargin(0.1)
        p1.SetBottomMargin(0.1)
        p1.cd()
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetOptTitle(0)
        ptordered_classifiers_label = ['leading','subleading','others']
        histogram_title = "BDT Over-training test: %s" %(ptordered_classifiers_label[x])
        Histo_training_BDTRepsonse.GetYaxis().SetTitle("Counts/Bin")
        Histo_training_BDTRepsonse.Draw('EHIST')
        Histo_testing_BDTRepsonse.Draw("EPSAME")

        c1.cd(1).BuildLegend( 0.8,  0.7,  0.99,  0.99,"","LP").SetFillColor(0)

        # Add custom title
        l1=ROOT.TLatex()
        l1.SetNDC()
        l1.DrawLatex(0.35,0.94,histogram_title)

        c1.cd()
        p2 = ROOT.TPad('p2','p2',0.0,0.0,1.0,0.2)
        p2.Draw()
        p2.SetRightMargin(0.1)
        p2.SetLeftMargin(0.15)
        p2.SetTopMargin(0.01)
        p2.SetBottomMargin(0.4)
        p2.SetGridx(True)
        p2.SetGridy(True)
        p2.cd()

        ratioframe=Histo_training_BDTRepsonse.Clone('ratioframe')
        ratioframe.Divide(Histo_testing_BDTRepsonse)
        ratioframe.GetYaxis().SetTitle('Train/Test')
        ratioframe.GetYaxis().SetRangeUser(0.46,1.54)
        ratioframe.GetYaxis().SetNdivisions(6)
        ratioframe.GetYaxis().SetLabelSize(0.18)
        ratioframe.GetYaxis().SetTitleSize(0.2)
        ratioframe.GetYaxis().SetTitleOffset(0.3)
        ratioframe.GetXaxis().SetTitle("BDT Response")
        ratioframe.GetXaxis().SetLabelSize(0.18)
        ratioframe.GetXaxis().SetTitleSize(0.2)
        ratioframe.GetXaxis().SetTitleOffset(0.8)
        ratioframe.SetFillStyle(0)
        ratioframe.SetMarkerStyle(2)
        ratioframe.SetMarkerColor(1)
        ratioframe.Draw('P')

        c1.cd()
        c1.Modified()
        c1.Update()
        c1.Print('training_v3/TMVA_BDT_UL16_v2_%s.png' %(x))

main()
