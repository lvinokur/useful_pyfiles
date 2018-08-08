import os, shutil, glob
#from mrtrix3 import app, fsl, file, image, path, run

subjectspath = '/home/lea/Atlas_project/preproc_to_template/out/subjects'
subjects = [ os.path.split(x)[-1] for x in glob.glob(os.path.join(subjectspath, '*'))]

sub_subjects = ['127933','188347', '899885', '751348', '146432','116524', '100408', '129028', '208226', '101107' ,'101309', '131722', '212318', '111716', '199655']


load_parc = ('aparc.a2009s+aseg.mif')
# roi1_labels = ['34','33','74']
# # removed 36, added 33 and 73
# roi2_labels = ['13','14','39','40','53','63','15']
# #added 52,62,15

# lh_names1 = [os.path.join('rois','destrieux',(str(label) +'_lh_dsx.mif' )) for label in roi1_labels]
# lh_names2 = [os.path.join('rois','destrieux',(str(label) +'_lh_dsx.mif' )) for label in roi2_labels]

# rh_names1 = [os.path.join('rois','destrieux',(str(label) +'_rh_dsx.mif' )) for label in roi1_labels]
# rh_names2 = [os.path.join('rois','destrieux',(str(label) +'_rh_dsx.mif' )) for label in roi2_labels]

# lh_name_string1 = ' '.join(lh_names1)
# lh_name_string2 = ' '.join(lh_names2)
# rh_name_string1 = ' '.join(rh_names1)
# rh_name_string2 = ' '.join(rh_names2)


# ends only orbitofrontal areas, excludes all other lobes
include = ('-include rois/rh_temp_gyr_d.mif '
           '-include rois/rh_inf_fr_g_d.mif')

exclude = ('-exclude rois/destrieux/hemi_wm_lh_dsx.mif ' # other hemisphere
           '-exclude rois/destrieux/thalamus_rh_dsx.mif ' #thalamus
           '-exclude rois/destrieux/hippocampus_rh.mif '
           '-exclude rois/destrieux/caudate_rh.mif '
           '-exclude rois/destrieux/putamen_rh.mif '
           '-exclude rois/destrieux/18_rh_dsx.mif '
           '-exclude rois/destrieux/17_rh_dsx.mif '
           '-exclude rois/destrieux/48_rh_dsx.mif '
           '-exclude rois/destrieux/49_rh_dsx.mif '
           '-exclude rois/destrieux/50_rh_dsx.mif '
           '-exclude rois/destrieux/44_rh_dsx.mif ' #temporal pole
           '-exclude rois/lh_occipital_lobe.mif ' #
           '-exclude rois/rh_occipital_lobe.mif ')


for subj in sub_subjects:
	print(' Working on --> ', subj)
	os.chdir(os.path.join(subjectspath, subj ))
	# # calculate regions of interest masks
	# maxs = (' -max')
	# max_string = maxs * (len(lh_names1) - 1)
	# os.system('mrcalc ' + lh_name_string1 + ' ' + max_string + ' rois/lh_temp_gyr.mif -quiet -force' )
	# os.system('mrcalc ' + rh_name_string1 + ' ' + max_string + ' rois/rh_temp_gyr.mif -quiet -force' )

	# maxs = (' -max')
	# max_string = maxs * (len(lh_names2) - 1)
	# os.system('mrcalc ' + lh_name_string2 + ' ' + max_string + ' rois/lh_inf_fr_g.mif -quiet -force' )
	# os.system('mrcalc ' + rh_name_string2 + ' ' + max_string + ' rois/rh_inf_fr_g.mif -quiet -force' )
    
    # dilate 
	os.system('maskfilter -npass 2 rois/lh_temp_gyr.mif dilate rois/lh_temp_gyr_d.mif -force ')
	os.system('maskfilter -npass 2 rois/rh_temp_gyr.mif dilate rois/rh_temp_gyr_d.mif -force ')
	os.system('maskfilter -npass 2 rois/lh_inf_fr_g.mif dilate rois/lh_inf_fr_g_d.mif -force ')
	os.system('maskfilter -npass 2 rois/rh_inf_fr_g.mif dilate rois/rh_inf_fr_g_d.mif -force ')
    
    #track generate

	os.system('tckgen -select 10000 -seed_image tractseg_output/1_mask.mif ' + include + ' ' + exclude + 
             ' fod.mif bundles/arcuate_rh_gen.tck -force') 
