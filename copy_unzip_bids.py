#!/usr/bin/env python3

# scp subject by subject into BIDS Derivatives structure

import os, shutil
import zipfile

# define sources, destinations and subject lists
# ['130316', '756055', '129028']

subject_list = ['130316', '756055', '129028']
source_dir = "/home/lea/HCP100sub/"
dest_dir = "/home/lea/Atlas_project/test_unzip/"
source_serv = "lea@10.101.98.86:"
which_file = '_3T_Diffusion_preproc.zip'
if not os.path.exists(dest_dir + 'derivatives'):
  os.mkdir(dest_dir + 'derivatives')

for subject in subject_list:
  print 'Workin on : --> ' + subject
  temp_dir = os.path.join(dest_dir, 'temp')
  if not os.path.exists(temp_dir):
    os.mkdir(temp_dir)

  # Copy
  os.system('scp ' + source_serv + source_dir + subject + which_file + ' ' + dest_dir)
  #print ('scp ' + source_serv + source_dir + subject + which_file + ' ' + dest_dir)

  # Unzip and Remove zipped file
  filename = dest_dir + subject + which_file
  zip_ref = zipfile.ZipFile(filename, 'r')
  zip_ref.extractall(temp_dir)
  zip_ref.close()
  #print 'unzip' + filename
  os.remove(filename)

  # Rename and rearraange
  subj_dir = dest_dir + 'derivatives/sub-' + subject
  os.mkdir(subj_dir)
  os.mkdir(os.path.join(subj_dir,'dwi'))
  os.mkdir(os.path.join(subj_dir,'anat'))
  os.rename(os.path.join(temp_dir,subject,'T1w/Diffusion/data.nii.gz'),(subj_dir + '/dwi/sub-' + subject + '_dwi.nii.gz'))
  #print (os.path.join(temp_dir,subject,'T1w/Diffusion/data.nii.gz'),(subj_dir + '/dwi/sub-' + subject + '_dwi.nii.gz'))
  os.rename(os.path.join(temp_dir,subject,'T1w/Diffusion/bvecs'),(subj_dir + '/dwi/sub-' + subject + '_dwi.bvec'))
  os.rename(os.path.join(temp_dir,subject,'T1w/Diffusion/bvals'),(subj_dir + '/dwi/sub-' + subject + '_dwi.bval'))
  os.rename(os.path.join(temp_dir,subject,'T1w/T1w_acpc_dc_restore_1.25.nii.gz'),(subj_dir + '/anat/sub-' + subject + '_acpc_dc_restore_1.25.nii.gz'))

  shutil.rmtree(os.path.join(temp_dir,subject))
