#!/usr/bin/env python

import os, glob
from mrtrix3 import app, fsl, file, image, path, run



subjectspath = '/data/lea/Atlas_project/preproc_to_template/out/subjects'
subjects = [ os.path.split(x)[-1] for x in glob.glob(os.path.join(subjectspath, '*'))]

for subject in subjects :
    print('working on subject ---> ', subject)
    subject_path = os.path.join(subjectspath, subject)
    fod_file = os.path.join(subject_path, 'fod.mif')
    tck_file = os.path.join(subject_path, 'tck_2m.tck')
    print('tckgen ' + fod_file + ' ' +  tck_file + ' -cutoff 0.05 -maxlength 250 -select 2000000 -seed_dynamic ' + fod_file + ' -force')
    run.command('tckgen ' + fod_file + ' ' +  tck_file + ' -cutoff 0.05 -maxlength 250 -select 10000000 -seed_dynamic ' + fod_file + ' -force')
