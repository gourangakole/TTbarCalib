#!/bin/bash

#INPUTFILE="UL18_v5_updatedttXS_merged/MC13TeV_TTJets_training_combined.root"
INPUTFILE="UL18_v5_updatedttXS_MVA_merged/MC13TeV_TTJets_training_combined.root"

a=(0 1 2)
for i in ${a[@]}; do
    root -b -q "${CMSSW_BASE}/src/RecoBTag/PerformanceMeasurements/test/TTbarCalib/KIN_trainClassifier.C+(\"BDT\",\"${INPUTFILE}\",${i})";
    mv TMVA_BDT_UL18.root TMVA_BDT_UL18_${i}.root;
done
