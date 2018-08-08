import os, shutil, glob
#from mrtrix3 import app, fsl, file, image, path, run

subjectspath = '/home/lea/Atlas_project/preproc_to_template/out/subjects'
subjects = [ os.path.split(x)[-1] for x in glob.glob(os.path.join(subjectspath, '*'))]

sub_subjects = ['127933','188347', '899885', '751348', '146432','116524', '100408', '129028', '208226', '101107' ,'101309', '131722', '212318', '111716', '199655']


load_parc = ('aparc.a2009s+aseg.mif')
roi_labels = ['28','29','46','68','69','70','3','4']

lh_names = ['rois/destrieux/' + str(label) for label in roi_labels]
lh_names = [label + '_lh_dsx.mif' for label in lh_names]
rh_names = ['rois/destrieux/' + str(label) for label in roi_labels]
rh_names = [label + '_rh_dsx.mif' for label in rh_names]

lh_name_string = ' '.join(lh_names)
rh_name_string = ' '.join(rh_names)

maxs = (' -max')
max_string = maxs * (len(lh_names) - 1)



# includes prepost_central and excludes temporal, occipital lobes as well as thalamus
include = ('-include rois/lh_prepost_central_d.mif '
            '-include rois/brainstem_t.mif ')
exclude = ('-exclude rois/lh_temporal_lobe.mif ' 
          '-exclude rois/rh_temporal_lobe.mif '
          '-exclude rois/lh_occipital_lobe.mif '
          '-exclude rois/rh_occipital_lobe.mif '
           '-exclude rois/destrieux/thalamus_lh_dsx.mif '
          '-exclude rois/destrieux/thalamus_rh_dsx.mif ')



for subj in sub_subjects:
	print(' Working on --> ', subj)
	os.chdir(os.path.join(subjectspath, subj ))
	# os.system('mrcalc ' + lh_name_string + ' ' + max_string + ' rois/lh_prepost_central.mif  -quiet -force' )
	# os.system('mrcalc ' + rh_name_string + ' ' + max_string + ' rois/rh_preprost_central.mif  -quiet -force' )
	# os.system('maskfilter -npass 3 rois/lh_prepost_central.mif dilate rois/lh_prepost_central_d.mif -force ')
	os.system('tckgen -select 10000 -seed_cutoff 0.1 -max_attempts_per_seed 500  -seed_image rois/brainstem_t.mif ' + include + ' ' 
		               + exclude + ' fod.mif bundles/cst_l_gen.tck -force') 
