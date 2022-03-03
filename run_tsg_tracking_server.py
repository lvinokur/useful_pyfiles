
import os, glob
#from mrtrix3 import app, fsl, file, image, path, run

print ('initializing')

subjectspath = '/home/lea/Atlas_project/preproc_to_template/out/subjects'
warpspath = '/home/lea/Atlas_project/preproc_to_template/out/warps'
tck_warps_path = '/home/lea/Atlas_project/preproc_to_template/out/tck_warps'
base_path = '/home/lea/Atlas_project/preproc_to_template/out'
template_path = '/home/lea/Atlas_project/preproc_to_template/out/template'
fixel_mask = os.path.join(template_path,'fixelmask_06')

subjects = [ os.path.split(x)[-1] for x in glob.glob(os.path.join(subjectspath, '*'))]
subjects = ['127933', '188347', '899885', '751348', '116524', '100408', '129028', '208226', '101107', '101309', '131722',
            '212318', '111716', '199655', '118528', '672756', '654754', '178950', '792564', '192540', '151223', '198451',
            '151526', '110411', '190031', '105014', '138534', '397760', '221319', '139637', '239944', '146432', '162733', '366446']


bundle_names = [os.path.split(x)[-1] for x in glob.glob(os.path.join(subjectspath,subjects[0], 'tractseg_output', 'bundle_segmentations', '*.nii.gz'))]
bundle_names = [x.split('.')[0] for x in bundle_names]
bundle_names.sort()
print(bundle_names)

for subject in subjects :
    os.chdir(os.path.join(subjectspath,subject))
    if not os.path.exists('tsg_bundles'):
        os.makedirs('tsg_bundles')
    tck_warp = os.path.join(tck_warps_path,('tck_' + subject + '.mif'))
    print(' Working on Subject ---> ',subject )
    for bundle in bundle_names :
        print('Tracking : ', bundle)
        maskname = os.path.join('tsg_masks',(bundle + '.mif'))
        dilated_mask = os.path.join('tsg_masks',(bundle + '_dilated.mif'))
        begining = os.path.join('tsg_masks',(bundle + '_b.mif'))
        ending = os.path.join('tsg_masks',(bundle + '_e.mif'))

        tckgen_name = os.path.join('tsg_bundles', (bundle + '_50k.tck'))
        tck_warped = os.path.join('tsg_bundles',(bundle + '50k_warped.tck'))
        fixel_file = (bundle + '_' + subject + '.mif')
        fixel_folder = os.path.join(template_path,'fixel_bundles_20k_ends_dl')
        os.system('maskfilter -npass 1 ' + maskname + ' dilate ' + dilated_mask + ' -force')
        include = (' -seed_image '  + maskname + ' -include ' + begining + ' -include ' + ending + ' -mask ' + dilated_mask )
        os.system('tckgen -select 20000 ' + include + ' fod.mif ' + tckgen_name + ' -force')
        os.system('tcktransform ' + tckgen_name + ' ' + tck_warp + ' ' + tck_warped + ' -force')
        os.system('tck2fixel ' + tck_warped + ' ' + fixel_mask + ' ' + fixel_folder + ' ' + fixel_file + ' -force')
