#!/bin/bash
#INPUTFILE="training_samples_HIPM/MC13TeV_TTJets_combined.root"
#OUTPUTDIR="training_HIPM"
#INPUTFILE="MC13TeV_TTJets_SL_test.root"
#INPUTFILE="gkole_test_30Oct2023_TTto1L_v2/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8.root"
#OUTPUTDIR="training_test_Summer2022_v1"

#INPUTFILE="gkole_test_23Nov2023_TTto2L2Nu_Training_v1/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8.root"
#OUTPUTDIR="training_test_23Nov2023_Summer2022_v1"
INPUTFILE="Summer23preBPix_for_training_v1/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8.root" #Summer2023 file
OUTPUTDIR="Summer23preBPix_for_training_v1"
a=(0 1 2)
for i in ${a[@]}; do
    root -b -q "${CMSSW_BASE}/src/TTbarCalib/KIN_trainClassifier.C+(\"${INPUTFILE}\",${i})";
    mkdir ${OUTPUTDIR}
    mv TMVA_BDT_Summer2023.root ${OUTPUTDIR}/TMVA_BDT_Summer2023_${i}.root; # gkole: the names are hardcodes in the C+ file
    #mv TMVA_BDT_test.root ${OUTPUTDIR}/TMVA_BDT_test_${i}.root;
done
