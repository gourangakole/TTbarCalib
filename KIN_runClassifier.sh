#!/bin/bash

INPUTFILE="combined_UL17_v2/combined_ttbar.root"

a=(0 1 2)
for i in ${a[@]}; do
    root -b -q "${CMSSW_BASE}/src/RecoBTag/PerformanceMeasurements/test/TTbarCalib/KIN_trainClassifier.C+(\"BDT\",\"${INPUTFILE}\",${i})";
    mv TMVA_BDT_UL17_v2.root TMVA_BDT_UL17_v2_${i}.root;
done
