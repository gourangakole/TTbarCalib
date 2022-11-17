#!/bin/bash
# Discriminant for scale factors:
tagger=DeepFlavourBDisc #DeepFlavourBDisc #DeepCSVBDisc
# Fit directory
folders=('fits_UL16_preVFP_nonTTXSDOWN' 'fits_UL16_preVFP_nonTTXSUP')
# 'fits_UL16_preVFP_nominal' 'fits_UL16_preVFP_erdON' 'fits_UL16_preVFP_hdampDOWN' 'fits_UL16_preVFP_hdampUP' 'fits_UL16_preVFP_mtop171p5' 'fits_UL16_preVFP_mtop173p5' 'fits_UL16_preVFP_TuneCP5down' 'fits_UL16_preVFP_TuneCP5up' 'fits_UL16_preVFP_nonTTXSDOWN' 'fits_UL16_preVFP_nonTTXSUP'


# Loop over chosen folders above.
for f in "${folders[@]}";
do
  echo "running PostFitter for folder $f"
  python createSFbSummaryReport.py -i "kin":$f/kindisc_templates/.$tagger\_fits.pck -o $f\/$tagger\_fits;
done
