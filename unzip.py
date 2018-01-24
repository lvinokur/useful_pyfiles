#!/usr/bin/env python

# unzip files in a directory
# in general for HCP data i don't have to specify each subject name directory and just unzip directly into the "mother" directory

import os, shutil, glob
import zipfile


source_dir = "/home/lea/HCP100sub/"
dest_dir = "/data/lea/Atlas_project/test_docker_preproc/"
files_list = [os.path.basename(unproc_path) for unproc_path in glob.glob(os.path.join(source_dir, '*_3T_Diffusion_unproc.zip'))]
subject_list = [subject_num.split("_")[0] for subject_num in files_list]
if not os.path.exists(dest_dir):
  os.mkdir(dest_dir)

os.chdir(source_dir)

#ovveride subj list
subject_list = ['130316', '756055', '129028']
print subject_list

for subject in subject_list:
  print 'Workin on : --> ' + subject
  diffusion_unproc = '_3T_Diffusion_unproc.zip'
  strctural_preproc = '_3T_Structural_preproc.zip'
  # Copy
  print subject + diffusion_unproc
  print dest_dir
  shutil.copy((subject + diffusion_unproc) , dest_dir)
  shutil.copy((subject + strctural_preproc) , dest_dir)
  # os.system('cp ' + source_serv + source_dir + subject + which_file + ' ' + dest_dir)

  # Unzip and Remove zipped file
  filename1 = dest_dir + subject + diffusion_unproc
  zip_ref1 = zipfile.ZipFile(filename1, 'r')
  zip_ref1.extractall(dest_dir)
  zip_ref1.close()

  filename2 = dest_dir + subject + strctural_preproc
  zip_ref2 = zipfile.ZipFile(filename2, 'r')
  zip_ref2.extractall(dest_dir)
  zip_ref2.close()

  #print 'unzip' + filename
  os.remove(filename1)
  os.remove(filename2)
