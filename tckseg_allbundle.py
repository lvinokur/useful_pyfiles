#!/usr/bin/env python

import os, glob

from mrtrix3 import app, fsl, file, image, path, run

subjectspath = '/data/lea/Atlas_project/preproc_to_template/out/subjects'
subjects = [ os.path.split(x)[-1] for x in glob.glob(os.path.join(subjectspath, '*'))]

for subject in sub_subjects :
    os.chdir(os.path.join(subjectspath,subject))
    maskname = os.path.join('tractseg_output','1_mask.mif')
    output_name = os.path.join('bundles', 'arcuate_tsg_rh.tck')
    run.command('tckgen -select 10000 -seed_image ' + maskname +  ' -mask ' + maskname +  ' fod.mif ' + output_name)


os.chdir(os.path.join(subjectspath,subj))
maskname = os.path.join('tractseg_output','23_mask.mif')
output_name = os.path.join('bundles', 'cerebellar_ped_inf_tsg_rh.tck')
run.command('tckgen -select 10000 -seed_image ' + maskname +  ' -mask ' + maskname +  ' fod.mif ' + output_name + ' -force')

os.chdir(os.path.join(subjectspath,subj))
maskname = os.path.join('tractseg_output','22_mask.mif')
output_name = os.path.join('bundles', 'cerebellar_ped_inf_tsg_lh.tck')
run.command('tckgen -select 10000 -seed_image ' + maskname +  ' -mask ' + maskname +  ' fod.mif ' + output_name + ' -force')
