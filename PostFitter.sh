#!/bin/bash
# Discriminant for scale factors:
tagger=DeepFlavourBDisc #DeepFlavourBDisc #DeepCSVBDisc
# Fit directory
folders=(UL18_fit_dir_nonttXSUP)
#UL18_fit_dir
#UL18_fit_dir_TuneCP5DOWN

# Loop over chosen folders above.
for f in ${folders[@]}; do
  python createSFbSummaryReport.py -i "kin":$f/kindisc_templates/.$tagger\_fits.pck -o $folders\/$tagger\_fits;
done
