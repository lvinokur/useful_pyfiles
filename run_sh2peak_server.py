#!/usr/bin/env python

import os, glob

print ('initializing')
subjectspath = '/home/lea/Atlas_project/preproc_to_template/out/subjects'
subjects = [ os.path.split(x)[-1] for x in glob.glob(os.path.join(subjectspath, '*'))]

for subject in subjects :
    print('working on subject ---> ', subject)
    subject_path = os.path.join(subjectspath, subject)
    fod_file = os.path.join(subject_path, 'fod.mif')
    peaks_file = os.path.join(subject_path, 'peaks.nii.gz')
    os.system('sh2peaks  ' + fod_file + ' ' peaks_file +  ' -force')