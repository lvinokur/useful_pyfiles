#! python

import sys
import os
import glob


print 'Hello, Lea!'

#directory of subjects
subjects_dir = '/home/lea/HCP_Data_10/Subjects'
subjects = ['100307','115320', '105115', '118730', '103414', '113619', '118932', '111312', '110411', '117122']
fods_dir = '/home/lea/HCP_Data_10/Subjects/fods_input'
masks_dir = '/home/lea/HCP_Data_10/Subjects/masks_input'

for subj in subjects:
  print 'Workin on : --> ' + subj
  subj_path = subjects_dir + '/' + subj
  os.chdir(subj_path)
  os.system('ln -sr ' + subj_path + '/fod_bias_norm.mif ' + fods_dir + '/' + subj + '_fodbn.mif')
  os.system('ln -sr ' + subj_path + '/dwi_mask.mif ' + masks_dir + '/' + subj + '_mask.mif')
