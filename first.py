#! python

import sys
import os
import zipfile
import glob

print 'Hello, Lea!'

#directory of zipped files
zipdir="/data/lea/HCP_Data_10"


zip_files = glob.glob(zipdir + '/*_Diffusion_preproc.zip')

for n in zip_files:
  dir_name = os.path.split(n)
  subjname=dir_name[1].split('_')
  print subjname[0]


