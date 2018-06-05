#!/usr/bin/env python

import os, glob

print ('initializing')
subjectspath = '/home/lea/Atlas_project/preproc_to_template/out/subjects'
subjects = [ os.path.split(x)[-1] for x in glob.glob(os.path.join(subjectspath, '*'))]

for subject in subjects :
    print('working on subject ---> ', subject)
    subject_path = os.path.join(subjectspath, subject)
    fod_file = os.path.join(subject_path, 'fod.mif')
    tck_file = os.path.join(subject_path, 'tck_10m.tck')
    print('tckgen ' + fod_file + ' ' +  tck_file + ' -cutoff 0.05 -maxlength 250 -select 5000000 -seed_dynamic ' + fod_file + ' -force')
    os.system('tckgen ' + fod_file + ' ' +  tck_file + ' -cutoff 0.05 -maxlength 250 -select 10000000 -seed_dynamic ' + fod_file + ' -force')
