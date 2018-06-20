#!/usr/bin/env python

import os, glob
from mrtrix3 import app, fsl, file, image, path, run

subjectspath = '/data/lea/Atlas_project/preproc_to_template/out/subjects'
subjects = [ os.path.split(x)[-1] for x in glob.glob(os.path.join(subjectspath, '*'))]

destrieux = ('/home/lea/Dropbox/Atlas/Destrieux_lobe_indices_corrected.txt')
with open(destrieux) as f:
    lobes = f.readlines()
lobes = [x.strip() for x in lobes]
areas = list(range(1,76))

lobe_indx=dict(zip(areas,lobes))

frontal = []
parietal = []
temporal = []
occipital = []
for k, v in lobe_indx.items():
    iv=int(v)
    if iv == 1:
        frontal.append(k)
    elif iv == 2:
        parietal.append(k)
    elif iv == 3:
        temporal.append(k)
    elif iv == 4:
        occipital.append(k)
    elif iv == 0:
        print('42 is the answer')
    else:
        print('this is wrong')

for subject in subjects :
    os.chdir(os.path.join(subjectspath,subject))
    print (' Working On -->  ', subject)
    lh_names = ['rois/destrieux/' + str(label) for label in frontal]
    lh_names = [label + '_lh_dsx.mif' for label in lh_names]
    rh_names = ['rois/destrieux/' + str(label) for label in frontal]
    rh_names = [label + '_rh_dsx.mif' for label in rh_names]
    lh_name_string = ' '.join(lh_names)
    rh_name_string = ' '.join(rh_names)
    maxs = (' -max')
    max_string = maxs * (len(lh_names) - 1)
    run.command('mrcalc ' + lh_name_string + ' ' + max_string + ' rois/lh_frontal_lobe.mif -force' )
    run.command('mrcalc ' + rh_name_string + ' ' + max_string + ' rois/rh_frontal_lobe.mif -force' )

    lh_names = ['rois/destrieux/' + str(label) for label in parietal]
    lh_names = [label + '_lh_dsx.mif' for label in lh_names]
    rh_names = ['rois/destrieux/' + str(label) for label in parietal]
    rh_names = [label + '_rh_dsx.mif' for label in rh_names]
    lh_name_string = ' '.join(lh_names)
    rh_name_string = ' '.join(rh_names)
    maxs = (' -max')
    max_string = maxs * (len(lh_names) - 1)
    run.command('mrcalc ' + lh_name_string + ' ' + max_string + ' rois/lh_parietal_lobe.mif -force' )
    run.command('mrcalc ' + rh_name_string + ' ' + max_string + ' rois/rh_parietal_lobe.mif -force' )

    lh_names = ['rois/destrieux/' + str(label) for label in temporal]
    lh_names = [label + '_lh_dsx.mif' for label in lh_names]
    rh_names = ['rois/destrieux/' + str(label) for label in temporal]
    rh_names = [label + '_rh_dsx.mif' for label in rh_names]
    lh_name_string = ' '.join(lh_names)
    rh_name_string = ' '.join(rh_names)
    maxs = (' -max')
    max_string = maxs * (len(lh_names) - 1)
    run.command('mrcalc ' + lh_name_string + ' ' + max_string + ' rois/lh_temporal_lobe.mif -force' )
    run.command('mrcalc ' + rh_name_string + ' ' + max_string + ' rois/rh_temporal_lobe.mif -force' )

    lh_names = ['rois/destrieux/' + str(label) for label in occipital]
    lh_names = [label + '_lh_dsx.mif' for label in lh_names]
    rh_names = ['rois/destrieux/' + str(label) for label in occipital]
    rh_names = [label + '_rh_dsx.mif' for label in rh_names]
    lh_name_string = ' '.join(lh_names)
    rh_name_string = ' '.join(rh_names)
    maxs = (' -max')
    max_string = maxs * (len(lh_names) - 1)
    run.command('mrcalc ' + lh_name_string + ' ' + max_string + ' rois/lh_occipital_lobe.mif -force' )
    run.command('mrcalc ' + rh_name_string + ' ' + max_string + ' rois/rh_occipital_lobe.mif -force' )
