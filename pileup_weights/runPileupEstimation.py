import optparse
import os,sys
import json
import commands
import ROOT
from ROOT import TH1F, TH1D, TFile
import matplotlib.pyplot as plt
import numpy as np

# Find the mixing module version for you
# https://github.com/cms-sw/cmssw/tree/CMSSW_10_6_X/SimGeneral/MixingModule/python
from SimGeneral.MixingModule.mix_2016_25ns_UltraLegacy_PoissonOOTPU_cfi import *
#from SimGeneral.MixingModule.mix_2017_25ns_UltraLegacy_PoissonOOTPU_cfi import *
#from SimGeneral.MixingModule.mix_2018_25ns_UltraLegacy_PoissonOOTPU_cfi import *

"""
steer the script
"""
def main():

    #configuration
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    parser.add_option('--certJson',  dest='certJson',      help='json file with processed runs',          default=None,    type='string')
    parser.add_option('--dataRange', dest='dataRange'  ,   help='name of data range for pileup file name',                  default="",    type='string')
    parser.add_option('--MCName',    dest='MCName'  ,      help='name of MC sample for reweighting histogram name',         default="",    type='string')
    parser.add_option('--mbXsec',    dest='mbXsec'  ,      help='Specify the min bias XS to use when calculating the average pileup.',      default=69200,   type=float)# 2018 average = 69.2mb
    parser.add_option('--mbXsecUnc', dest='mbXsecUnc'  ,   help='minimum bias cross section uncertainty', default=0.046,   type=float)
    parser.add_option('--mcDirs',    dest='mcDirs'  ,      help='directories of MC to build PU',          default="",      type='string')
    parser.add_option('--puJson',    dest='puJson'  ,      help='pileup json file', default='',    type='string')
    (opt, args) = parser.parse_args()

    MCDirs=opt.mcDirs.split(",")
    print('Running on: ', MCDirs)

    temp_file_name = MCDirs[0].split('/')[-1]

    #fig, ax = plt.subplots()
    fig, ax = plt.subplots(2,1,figsize=(8,8), gridspec_kw={'height_ratios': [2,1]}, sharex=True)
    ax[0].set_xlabel('')
    ax[0].set_ylabel('Normalised to unity', fontsize=15.0)
    ax[1].set_xlabel('nPUTrue', fontsize=15.0)
    ax[1].set_ylabel('Normalised to unity', fontsize=15.0)
    # Simulated pileup
    # The distribution retrieved here should be the same pileup distribution that was used in the MC generation
    # Can be taken from central repository but should ensure/check the pileup matches the one used in the MC
    if len(MCDirs)==0:
        NPUBINS=len(mix.input.nbPileupEvents.probValue)
        simPuH=ROOT.TH1F('simPuH','',NPUBINS,float(0),float(NPUBINS))
        for xbin in xrange(0,NPUBINS):
            probVal=mix.input.nbPileupEvents.probValue[xbin]
            simPuH.SetBinContent(xbin,probVal)
    else:
        # MC pileup file from PileupTools github repo
        # Includes PV in vertex counting (i.e. one additional bin)
        #tfile = ROOT.TFile.Open('pileup_2016GH.root')
        tfile = ROOT.TFile.Open('mcPileupUL2018.root')
        simPU_TH1D = tfile.Get('pu_mc')
        simPuH=TH1F('simPuH','', simPU_TH1D.GetNbinsX()-1, 0., simPU_TH1D.GetNbinsX()-1)
        simPuH.SetDirectory(0)
        nvert_x = []
        val_y = []
        # Have to use normalised distributions
        simPU_TH1D.Scale(1./simPU_TH1D.Integral())
        for bins in xrange(1,simPU_TH1D.GetNbinsX()):
            nvert_x.append(simPU_TH1D.GetBinCenter(bins))
            val_y.append(simPU_TH1D.GetBinContent(bins))
            simPuH.SetBinContent(bins,simPU_TH1D.GetBinContent(bins))

        # Generate MC pileup distribution from nPUTrue for pre-selection events via BTagAnalyzer
        NPUBINS=100
        mcFilePuH = TH1F('mcFilePuH', '', 100, 0, 100)
        mcFilePuH.SetDirectory(0)
        for directory in MCDirs:
            print('directory: ', directory)
            fileNames=os.listdir(directory)
            iFile=0
            for fileName in fileNames:
                if iFile%50==0:
                    print "iFile",iFile
                iFile=iFile+1
                if fileName.find(".root")!=-1:
                    tfile=ROOT.TFile.Open(directory+"/"+fileName)
                    if tfile.IsZombie():
                        print('File is zombie. Skipping.')
                        continue
                    puPlus=tfile.Get("allEvents/hPUPlusCount")
                    puNeg=tfile.Get("allEvents/hPUNegCount")
                    mcFilePuH.Add(puPlus)
                    mcFilePuH.Add(puNeg,-1)
                    tfile.Close()
        mcfile_nvert_x = []
        mcfile_val_y = []
        mcFilePuH_99bins = TH1F('mcFilePuH', '', mcFilePuH.GetNbinsX()-1, 0, mcFilePuH.GetNbinsX()-1)
        # Have to use normalised distributions
        mcFilePuH.Scale(1./mcFilePuH.Integral())
        for bins in xrange(1,mcFilePuH.GetNbinsX()):
            mcfile_nvert_x.append(mcFilePuH.GetBinCenter(bins))
            mcfile_val_y.append(mcFilePuH.GetBinContent(bins))
            mcFilePuH_99bins.SetBinContent(bins,mcFilePuH.GetBinContent(bins))

    ax[0].scatter(nvert_x, val_y , c='blue', s=1.5, label='MC (PileupTools git repo)')
    ax[0].scatter(mcfile_nvert_x, mcfile_val_y , c='red', s=1.5, label='MC (btagana hPUCount)')

    # Compute pileup in data assuming
    # https://twiki.cern.ch/twiki/bin/view/CMS/PileupJSONFileforData#Recommended_cross_section
    data_nvert_x = []
    data_val_y = []
    puDist=[]
    puWgts=[]
    ratio_x = []
    ratio_y = []
    MINBIASXSEC={'nom':opt.mbXsec,'up':opt.mbXsec*(1.+opt.mbXsecUnc),'down':opt.mbXsec*(1.-opt.mbXsecUnc)}
    '''for scenario in MINBIASXSEC:
        oFileName="Pileup_"+scenario+"_"+opt.dataRange+".root"
        print 'Creating %s ' % (oFileName)
        if os.path.isfile(oFileName):
            print "pile up target exists"
            continue
        print scenario, 'xsec=',MINBIASXSEC[scenario]
        cmd='python pileupCalc.py -i %s --inputLumiJSON %s --calcMode true --minBiasXsec %f --maxPileupBin %d --numPileupBins %s %s'%(opt.certJson,opt.puJson,MINBIASXSEC[scenario],NPUBINS,NPUBINS,oFileName)
        print cmd
        commands.getstatusoutput(cmd)'''

    # Divide normalised data histograms by normalised simulation
    for scenario in MINBIASXSEC:
        print(scenario)
        #oFileName="Pileup_"+scenario+"_"+opt.dataRange+".root"
        # Data pileup distribution taken from certification files in UltraLegacy directories.
        # 99 bins = number of pileup bins used for generation of MC.
        if scenario == 'nom':
            oFileName='/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/PileUp/UltraLegacy/PileupHistogram-goldenJSON-13tev-2016-preVFP-69200ub-99bins.root'
        if scenario == 'down':
            oFileName='/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/PileUp/UltraLegacy/PileupHistogram-goldenJSON-13tev-2016-preVFP-66000ub-99bins.root'
        if scenario == 'up':
            oFileName='/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/PileUp/UltraLegacy/PileupHistogram-goldenJSON-13tev-2016-preVFP-72400ub-99bins.root'
        fIn=ROOT.TFile.Open(oFileName)
        pileupH=fIn.Get('pileup')
        # Have to use normalised distributions
        pileupH.Scale(1./pileupH.Integral())
        # Add data pileup distribution to puDist
        puDist.append( ROOT.TGraph(pileupH) )
        if scenario == 'nom':
            for bins in xrange(1,pileupH.GetNbinsX()):
                data_nvert_x.append(pileupH.GetBinCenter(bins))
                data_val_y.append(pileupH.GetBinContent(bins))
        puDist[-1].SetName('pu_'+scenario+'_'+opt.MCName)
        # Divide by MC to get pileup wgts
        pileupH.Divide(mcFilePuH_99bins)
        if scenario == 'nom':
            for bins in xrange(1, pileupH.GetNbinsX() ):
                ratio_x.append(pileupH.GetBinCenter(bins))
                ratio_y.append(pileupH.GetBinContent(bins))
        puWgts.append( ROOT.TGraph(pileupH) )
        puWgts[-1].SetName('puwgts_'+scenario+'_'+opt.MCName)
        fIn.Close()

    ax[0].scatter(data_nvert_x, data_val_y , c='green', s=1.5, label='Data (Central certification histos)')
    ax[0].legend()
    ax[1].scatter(ratio_x, ratio_y , c='black', s=1.5)
    plt.savefig("pileup_UL16_preVFP_%s_comparisons.png"%(temp_file_name))
    # Save pileup info to file
    fOut=ROOT.TFile.Open('$CMSSW_BASE/src/RecoBTag/PerformanceMeasurements/test/TTbarCalib/pileup_weights/pileupWgts'+str(opt.dataRange)+'_preVFP.root','UPDATE')
    for gr in puWgts: print(gr); gr.Write()
    for gr in puDist: print(gr); gr.Write()
    fOut.Close()

"""
for execution from another script
"""
if __name__ == "__main__":
    sys.exit(main())
