#!/bin/bash

#. /d/Anaconda/etc/profile.d/conda.sh    #here path to the conda prompt
#conda activate polly

python C:/Users/eliza/.PyCharmCE2019.3/config/scratches/scratch_24.py   #here path to the low_base script

for file in /d/march/height/*; do                   #here path to the created in low_base script height dir
name=${file##*/}
sed 's/\r//g' "$file"

cd /d/march/profiles/                               #here path to the created in low_base script profiles dir
while read -r line

#below after -d path to dir where converted files store
do
    #printf '%s\n' "$line"
	for i in $line; do
	echo $i
	polly2scc -p pollyxt_tropos -l Leipzig -t picasso -f $name -d C:/Users/eliza/Desktop/tropos/data/ --range_e 1000 $line --range_b 1000 $line --camp_info C:/Users/eliza/Desktop/polly2scc/config/Leipzig_campaign_info_5.toml; done
	python C:/Users/eliza/.PyCharmCE2019.3/config/scratches/scratch_25.py    # here path to the plot script


done < "$file"
done
for file in C:/Users/eliza/Desktop/tropos/data/*.nc; do rm $file; done       # here delete all files from the converted dir


