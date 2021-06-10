#!/bin/bash
# Discriminant for scale factors:
tagger=DeepFlavourBDisc #DeepFlavourBDisc #DeepCSVBDisc
# Fit directory
folders=(fit_dir_UL17_XSUp)
#fit_dir_UL17_v3
#fit_dir_UL17_TuneCP5down/
#fit_dir_UL17_TuneCP5up/
#fit_dir_UL17_hdampDOWN/
#fit_dir_UL17_hdampUP/
#fit_dir_UL17_mtop171p5/
#fit_dir_UL17_mtop173p5/
#fit_dir_UL17_XSDown
#fit_dir_UL17_XSUp

# Loop over chosen folders above.
for f in ${folders[@]}; do
  python createSFbSummaryReport.py -i "kin":$f/kindisc_templates/.$tagger\_fits.pck -o $folders\/$tagger\_fits;
done
