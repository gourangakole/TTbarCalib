#!/bin/bash
#INPUTFILE="training_samples_HIPM/MC13TeV_TTJets_combined.root"
#OUTPUTDIR="training_HIPM"
INPUTFILE="MC13TeV_TTJets_SL_test.root"
OUTPUTDIR="training_test"
a=(0 1 2)
for i in ${a[@]}; do
    root -b -q "${CMSSW_BASE}/src/RecoBTag/PerformanceMeasurements/test/TTbarCalib/KIN_trainClassifier.C+(\"${INPUTFILE}\",${i})";
    mkdir ${OUTPUTDIR}
    mv TMVA_BDT_UL16_HIPM.root ${OUTPUTDIR}/TMVA_BDT_UL16_HIPM_${i}.root; # gkole: the names are hardcodes in the C+ file
    #mv TMVA_BDT_test.root ${OUTPUTDIR}/TMVA_BDT_test_${i}.root;
done
