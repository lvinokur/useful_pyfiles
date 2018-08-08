#!/usr/bin/env python

import os, glob

subjectspath = '/data/lea/Atlas_project/preproc_to_template/out/subjects'
subjects = [ os.path.split(x)[-1] for x in glob.glob(os.path.join(subjectspath, '*'))]

for subject in sub_subjects :
    for mask_i in range(72):
        os.chdir(os.path.join(subjectspath,subject))
        maskname = os.path.join('tractseg_output',(str(mask_i) + '_mask.mif'))
        if not os.path.exists('tsg_bundles'):
            os.makedirs('tsg_bundles')
        output_name = os.path.join('tsg_bundles', (str(mask_i) + '_bundle.mif'))
        os.system('tckgen -select 20000 -seed_image ' + maskname +  ' -mask ' + maskname +  ' fod.mif ' + output_name)
