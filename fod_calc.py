#! python

# After response function estimation: calculate average response, calculate FOD images, perform mtbin 

import sys
import os

print 'Hello, Lea!'

#directory of subjects
subjects_dir="/home/lea/HCP_Data_10/Subjects"

#list of subjects to be processed
#subjects=os.listdir(subjects_dir)
subjects=['100307','115320', '105115', '118730', '103414', '113619', '118932', '111312', '110411', '117122']



for subj in subjects: 
  print 'Workin on : --> ' + subj
  subj_path = subjects_dir + '/' + subj
  os.chdir(subj_path)
  # mrconver the mask to mif format
  os.system('mrconvert nodif_brain_mask.nii.gz dwi_mask.mif -datatype float32 -force')
  # calculate FOD
  os.system('dwi2fod msmt_csd dwi.mif ../group_average_response_wm.txt fod.mif ../group_average_response_gm.txt gm.mif ../group_average_response_csf.txt csf.mif -mask dwi_mask.mif -force')
  # run mtbin 
  os.system('mtbin fod.mif fod_bias_norm.mif gm.mif gm_bias_norm.mif csf.mif csf_bias_norm.mif -force')
  

print 'Finished!'




