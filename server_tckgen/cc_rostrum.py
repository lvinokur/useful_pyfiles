import os, shutil, glob
#from mrtrix3 import app, fsl, file, image, path, run

subjectspath = '/home/lea/Atlas_project/preproc_to_template/out/subjects'
subjects = [ os.path.split(x)[-1] for x in glob.glob(os.path.join(subjectspath, '*'))]

#sub_subjects = [ '101107', '101309', '131722', '212318', '111716', '199655']
sub_subjects = ['127933','188347', '899885', '751348', '146432','116524', '100408', '129028', '208226']



# ends only orbitofrontal areas, excludes all other lobes 
include = ('-include rois/lh_orbitofrontal_trim.mif '
            '-include rois/rh_orbitofrontal_trim.mif ')
exclude = ('-exclude rois/lh_temporal_lobe.mif ' 
          '-exclude rois/rh_temporal_lobe.mif '
          '-exclude rois/lh_parietal_lobe.mif '
          '-exclude rois/rh_parietal_lobe.mif '
          '-exclude rois/lh_occipital_lobe.mif '
          '-exclude rois/rh_occipital_lobe.mif ')


for subj in sub_subjects:
	os.chdir(os.path.join(subjectspath, subj ))
	print(' Working on --->   ' + subj)
	os.system('tckgen -select 10000 -seed_image rois/CC_trans.mif ' + include + ' ' + exclude + ' fod.mif bundles/cc_rstrm_gen_t.tck -force')
	os.system('tckedit bundles/cc_rstrm_gen_t.tck ' + include + ' -ends_only bundles/cc_rstrm_gen_tc.tck -force')