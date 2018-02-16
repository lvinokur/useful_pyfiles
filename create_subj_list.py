#! python

# generate subject list file

import csv
import os
import glob

print 'Hello, Lea, checking which subjects are missing'

#directory of zipped files
#main_dir="/home/lea/HCP100sub"
main_dir="/home/lea/Results_from_HPC/preprocessing/out"


files = glob.glob(main_dir + '/sub-*')

filenames = [os.path.split(n) for n in files]
subject_names = [n[1].split('-') for n in filenames]
subject_names = [n[1] for n in subject_names]


print subject_names
