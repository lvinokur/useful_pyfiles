#!/usr/bin/env python

import os, glob

subjectspath = '/home/lea/Atlas_project/preproc_to_template/out/subjects'
subjects = [ os.path.split(x)[-1] for x in glob.glob(os.path.join(subjectspath, '*'))]

for subject in subjects :
	print(' Working on Subject ---> ',subject )
	os.chdir(os.path.join(subjectspath,subject))
	for mask_i in range(72):
		print(' Bundle : ' , mask_i )
		maskname = os.path.join('tractseg_output',(str(mask_i) + '_mask.mif'))
		if not os.path.exists('tsg_bundles'):
			os.makedirs('tsg_bundles')
		output_name = os.path.join('tsg_bundles', (str(mask_i) + '_bundle.tck'))
		os.system('tckgen -select 20000 -seed_image ' + maskname +  ' -mask ' + maskname +  ' fod.mif ' + output_name)
