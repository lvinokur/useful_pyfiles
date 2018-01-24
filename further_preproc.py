#! python

#Run the further pre-processing steps on HCP pre-processed data before template generation

import sys
import os

print 'Hello, Lea!'

#directory of subjects
subjects_dir="/home/lea/HCP_Data_10/Subjects"

#list of subjects to be processed
#subjects=os.listdir(subjects_dir)
subjects=['115320', '105115', '118730', '103414', '113619', '118932', '111312', '110411', '117122']

print subjects
 
#calculate response functions
for subj in subjects: 
  subj_path = subjects_dir + '/' + subj
  os.chdir(subj_path)
  os.system('mrconvert data.nii.gz dwi.mif -fslgrad bvecs bvals -datatype float32 -stride 0,0,0,1 -force')
  os.system('dwi2response dhollander dwi.mif response_wm.txt response_gm.txt response_csf.txt -force')


