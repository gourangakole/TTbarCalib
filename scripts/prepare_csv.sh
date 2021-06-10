#!/bin/bash
# Script reads scale factors from sfb_report.tex and evaluates
# uncertainties from SF variations. These can be stored in a new
# .csv file. We can then copy the combined/total uncertainties
# across from kin_calib.csv to the .csv file with the full breakdown
# from this script to create file we want to distribute.

numbins=7 #ptrange-1 entries
ini=0
fin=$numbins
ptrange=(30 50 70 100 140 200 300 600)
# Using the following command:
# $> cat kin_calib.csv | grep central | awk '{printf $11"\n"}' | cut -d "\"" -f 2
# and copy the output to sfval=() beneath.
sfval=(
0.951303899288
0.967128872871
0.972747325897
0.965953826904
0.961486637592
0.955072164536
0.923096776009
0.943701267242
0.951342403889
0.959635078907
0.954578518867
0.950281500816
0.928687632084
0.881035625935
0.918055176735
0.92360240221
0.94087189436
0.938037395477
0.939417600632
0.912486672401
0.888222515583
)
# Remember to change "closure" to "mistag" and "pu" to "pileup" in sfb_report.tex
#syst=("jer qcdscale sel trig jes mistag pileup isrDef fsrDef")
syst=("jes jer trig sel qcdscale pileup isrDef fsrDef mistag")
# Execute this script ./prepare_csv.sh > <tagger>_Kin.csv and follow next 3 steps:
#1. Open kin_calib.csv. All replace all 'up_statistic' with 'up' and all 'up_total' with 'up_statistic'. Do the same for down.
#2. Change statistics -> statistic 0,$s/statistics/statistic/g
#   Invert down_statistic and down, and same for up <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<????
#3. $>cat kin_calib.csv | grep down,
# and
#   $>cat kin_calib.csv | grep up,
# Copy the output in the new .csv file (CSVv2_Kin.csv)
# Finally compare some cases for kin_calib.csv, sfb_report.tex, and <tagger>.csv to make sure
# the results are consistent:
#   $>cat CSVv2_Kin.csv | grep central;
#   $>cat CSVv2_Kin.csv | grep up,;
#   $>cat CSVv2_Kin.csv | grep down,;
#   $>cat sfb_report.tex | grep SF;

#The part related to stat is commented for the moment and taken from the .csv file produced by default
#Make sure that there are not lines like ${\rm SF}_{\rm b}$ & $ [ 988.3 \pm 3.3 \pm 3.5 ] \times10^{-3} $  \\
#They have to appear as ${\rm SF}_{\rm b}$ & $  0.9883 \pm 0.0033 \pm 0.0035 $  \\
#Make sure the following command provides the right output (may need to add a space in pm of sfb_report.tex: 0,$s/pm/pm /g)
#Test it once to see everything is reasonable
#stat=`cat sfb_report.tex | grep SF | awk '{printf "%.12f\n", $8}'`

echo "kin ;OperatingPoint, measurementType, sysType, jetFlavor, etaMin, etaMax, ptMin, ptMax, discrMin, discrMax, formula"
for (( wp=0; wp<3; wp++)); do
 # Central
 p=0
 l=0
 r=1
 for s in ${sfval[@]}; do
  if [[ "$ini" -le "$p" ]] && [[ "$p" -lt "$fin" ]]; then
   echo "$wp, kin, central, 0, -2.4, 2.4, ${ptrange[$l]}, ${ptrange[$r]}, 0, 1, \""${sfval[$p]}"\""
   let l=l+1
   let r=r+1
  fi
  let p=p+1
 done
 #Down
 #Statistics
 #p=0
 #l=0
 #r=1
 #for s in $stat; do
 # if [[ "$ini" -le "$p" ]] && [[ "$p" -lt "$fin" ]]; then
 #  valsys=$(awk "BEGIN {printf \"%.12f\",${sfval[$p]}-$s}")
 #  echo "$wp, kin, down_statistic, 0, -2.4, 2.4, ${ptrange[$l]}, ${ptrange[$r]}, 0, 1, \""$valsys"\""
 #  let l=l+1
 #  let r=r+1
 # fi
 # let p=p+1
 #done

 # Systematics
 for sys in $syst; do
  sy=`cat sfb_report.tex | grep $sys | awk '{printf "%.12f\n", $6}'`
  p=0
  l=0
  r=1
  for s in $sy; do
   if [[ "$ini" -le "$p" ]] && [[ "$p" -lt "$fin" ]]; then
    valsys=$(awk "BEGIN {printf \"%.12f\",${sfval[$p]}-${sfval[$p]}*sqrt($s*$s)}") #sqrt($s*$s) is to make $s positive
    echo "$wp, kin, down_$sys, 0, -2.4, 2.4, ${ptrange[$l]}, ${ptrange[$r]}, 0, 1, \""$valsys"\""
    let l=l+1
    let r=r+1
   fi
   let p=p+1
  done
 done
 #Up
 #Statistics
 #p=0
 #l=0
 #r=1
 #for s in $stat; do
 # if [[ "$ini" -le "$p" ]] && [[ "$p" -lt "$fin" ]]; then
 #  valsys=$(awk "BEGIN {printf \"%.12f\",${sfval[$p]}+$s}")
 #  echo "$wp, kin, up_statistic, 0, -2.4, 2.4, ${ptrange[$l]}, ${ptrange[$r]}, 0, 1, \""$valsys"\""
 #  let l=l+1
 #  let r=r+1
 # fi
 # let p=p+1
 #done
 #Systematics
 for sys in $syst; do
  sy=`cat sfb_report.tex | grep $sys | awk '{printf "%.12f\n", $8}'`
  p=0
  l=0
  r=1
  for s in $sy; do
   if [[ "$ini" -le "$p" ]] && [[ "$p" -lt "$fin" ]]; then
    valsys=$(awk "BEGIN {printf \"%.12f\",${sfval[$p]}+${sfval[$p]}*sqrt($s*$s)}")
    echo "$wp, kin, up_$sys, 0, -2.4, 2.4, ${ptrange[$l]}, ${ptrange[$r]}, 0, 1, \""$valsys"\""
    let l=l+1
    let r=r+1
   fi
   let p=p+1
  done
 done
 let ini=ini+numbins
 let fin=fin+numbins
done
