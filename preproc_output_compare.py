#!/usr/bin/env python3
import os, glob, shutil, sys
import zipfile

from mrtrix3 import app, fsl, file, image, path, run

subject_label = '100307'
work_folder = '/home/lea/Temp'
os.chdir(work_folder)

# copy my file + bvecsbvals into folder
my_output_dir = '/home/lea/Results_from_HPC/preprocessing/out'
subj_folder = ('sub-' + subject_label)
img_file = ('sub-' + subject_label + '_dwi.nii.gz')
bvec_file = ('sub-' + subject_label + '_dwi.bvec')
bval_file =('sub-' + subject_label + '_dwi.bval')

shutil.copy(os.path.join(my_output_dir, subj_folder,'dwi', img_file) , work_folder)
shutil.copy(os.path.join(my_output_dir, subj_folder,'dwi', bvec_file) , work_folder)
shutil.copy(os.path.join(my_output_dir, subj_folder,'dwi', bval_file) , work_folder)

# convert to mif

my_mrtrix_file = ('myproc_' + subject_label + '_dwi.mif')
run.command('mrconvert ' +  img_file + ' -fslgrad ' + bvec_file + ' ' + bval_file + ' ' + my_mrtrix_file + ' -force')


# unzip HCP_preproc + bvecsbvals file into same folder
source_dir =  '/home/lea/HCP100sub_aux/'
diffusion_preproc = '_3T_Diffusion_preproc.zip'
filename = subject_label + diffusion_preproc
filename = os.path.join(source_dir, filename)

img_file = os.path.join(subject_label, 'T1w/Diffusion', 'data.nii.gz')
bvec_file = os.path.join(subject_label, 'T1w/Diffusion', 'bvecs')
bval_file = os.path.join(subject_label, 'T1w/Diffusion', 'bvals')

zip_ref1 = zipfile.ZipFile(filename, 'r')
zip_ref1.extract(img_file,work_folder)
zip_ref1.extract(bvec_file,work_folder)
zip_ref1.extract(bval_file,work_folder)

zip_ref1.close()

hcp_mrtrix_file = ('hcpproc_' + subject_label + '_dwi.mif')
run.command('mrconvert ' +  img_file + ' -fslgrad ' + bvec_file + ' ' + bval_file + ' ' + hcp_mrtrix_file + ' -force')

# mrcalc diff image
run.command('mrcalc ' + my_mrtrix_file + ' ' + hcp_mrtrix_file + ' -subtract' + ' ' + subject_label + 'diff_file.mif' )

# extract by-shell volumes (dwiextract)

# calclate adc and md maps (dwi2tesor | tensor2metric)
