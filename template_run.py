#!/usr/bin/env python
import os, glob, shutil, sys, inspect, errno

from distutils.spawn import find_executable
from mrtrix3 import app, fsl, file, image, path, run

print ('Hello')

app.init ('Lea Vinokur (lea.vinokur@florey.edu.au)','Calculate a fixel-template based on 100 HCP subjects. '
                                'The analysis pipeline relies primarily on the MRtrix3 software package (www.mrtrix.org).')

app.cmdline.add_argument('in_dir', help='The directory with the input dataset ')
app.cmdline.add_argument('output_dir', help='The directory where the output files '
                                         'should be stored. If you are running group level analysis '
                                         'this folder should be prepopulated with the results of the '
                                         'participant level analysis.')

analysis_level_choices = ['participant1', 'group1', 'participant2', 'group2', 'participant3', 'group3', 'participant4', 'group4']

app.cmdline.add_argument('analysis_level', help='Level of the analysis that will be performed. '
                                                   'Valid choices are: [' + ', '.join(analysis_level_choices) + ']. \nMultiple participant '
                                                   'level analyses can be run independently(in parallel) using the same output_dir.',
                                              choices = analysis_level_choices)


app.cmdline.add_argument('--participant_label', help='The label(s) of the participant(s) that should be analyzed. The label '
                                                 'corresponds to sub-<participant_label> from the BIDS spec '
                                                 '(so it does not include "sub-"). If this parameter is not '
                                                 'provided all subjects should be analyzed. Multiple '
                                                 'participants can be specified with a space separated list.',
                                                  nargs='+')

options = app.cmdline.add_argument_group('Options for this Fibre Density and Cross-section BIDS-App')


options.add_argument('-vox_size', type=float, default='1.25', help='define the voxel size (in mm) to be used during the upsampling step (participant1 analysis level only)')

options.add_argument('-group_subset', help='Define a subset of participants to be used when generating the group-average FOD template and response functions. The subset is to be supplied as a comma separate list. Note the subset should be representable of your entire population and not biased towards one particular group. For example in a patient-control comparison, choose equal numbers of patients and controls. Used in group1 and group2 analysis levels.', nargs=1)

options.add_argument('-num_tracks', type=int, default='20000000', help='define the number of streamlines to be computed '
                                                                        'when performing tractography on the FOD template. '
                                                                        '(group3 analysis level only)')
options.add_argument('-num_tracks_sift', type=int, default='2000000', help='define the number of streamlines to '
                                                                           'remain after performing SIFT on the tractogram'
                                                                           '(group3 analysis level only)')



app.parse()



if app.isWindows():
  app.error('Script cannot be run on Windows due to FSL dependency')


subjects_to_analyze = []
# only for a subset of subjects
if app.args.participant_label:
  subjects_to_analyze = app.args.participant_label
# for all subjects
else:
  subject_dirs = glob.glob(os.path.join(app.args.in_dir, 'sub-*'))
  subjects_to_analyze = [subject_dir.split("-")[-1] for subject_dir in subject_dirs]

# create output subjects directory
all_subjects_dir = os.path.join(app.args.output_dir, 'subjects');
if not os.path.exists(all_subjects_dir):
  os.mkdir(all_subjects_dir)

# create the output template directory
template_dir = os.path.join(app.args.output_dir, 'template')
if not os.path.exists(template_dir):
  os.mkdir(template_dir)

# create a temporary directory for intermediate files
app.makeTempDir()

# read in group subset if supplied
subset = []
if app.args.group_subset:
  subset = app.args.group_subset[0].split(',')


# running participant level 1 (coversion, mask, and bias correction )
if app.args.analysis_level == 'participant1':

  print ('performing intial conversion and bias correction')
  for subject_label in subjects_to_analyze:
    label = 'sub-' + subject_label
    print('running pre-processing for ' + label)

    # Read DWI in BIDS derivatives folder
    all_dwi_images = glob.glob(os.path.join(app.args.in_dir, label, '*dwi', '*_dwi.nii*'))


    # Create output subject directory
    subject_dir = os.path.join(all_subjects_dir, subject_label)
    if not os.path.exists(subject_dir):
      os.mkdir(subject_dir)

    # Check existence output files from this analysis level
    dwi_preproc_file = os.path.join(subject_dir, 'dwi_preproc.mif')
    app.checkOutputPath(dwi_preproc_file)
    dwi_bias_file = os.path.join(subject_dir, 'dwi_preproc_bias.mif')
    app.checkOutputPath(dwi_bias_file)
    output_mask = os.path.join(subject_dir, 'mask.mif')
    app.checkOutputPath(output_mask)

    # DW gradient files
    grad_prefix = os.path.join(app.args.in_dir, label, 'dwi', label + '_dwi')
    if not (os.path.isfile(grad_prefix + '.bval') and os.path.isfile(grad_prefix + '.bvec')):
      grad_prefix = os.path.join(app.args.in_dir, 'dwi')
      if not (os.path.isfile(grad_prefix + '.bval') and os.path.isfile(grad_prefix + '.bvec')):
        app.error('Unable to locate valid diffusion gradient table');
    grad_import_option = ' -fslgrad ' + grad_prefix + '.bvec ' + grad_prefix + '.bval'



    # Stuff DWI gradients in *.mif file
    print ('mrconvert ' + all_dwi_images[0] + grad_import_option + ' ' + dwi_preproc_file)
    run.command('mrconvert ' + all_dwi_images[0] + grad_import_option + ' ' + dwi_preproc_file + ' -force')

    print (' problem here? ')
    # Compute brain mask
    run.command('dwi2mask ' + dwi_preproc_file + ' ' + output_mask + ' -force')

    # Perform Bias Correction
    run.command('dwibiascorrect ' + '-ants ' + '-mask ' + output_mask + ' ' + dwi_preproc_file + ' ' + dwi_bias_file + ' -force')

# running group level 1 (perform intensity normalisation, calculate response functions, average response )
elif app.args.analysis_level == "group1":
  print('performing intensity normalisation')

  intensitynorm_output = os.path.join(template_dir, 'inorm_output')
  if not os.path.exists(intensitynorm_output):
    os.mkdir(intensitynorm_output)
  fa_template = os.path.join(template_dir, 'fa_template.mif')
  app.checkOutputPath(fa_template)
  fa_wm_mask = os.path.join(template_dir, 'fa_wm_mask.mif')
  app.checkOutputPath(fa_wm_mask)

  # TODO Check if outputs exist

  app.gotoTempDir()
  os.mkdir('inorm_input')
  os.mkdir('mask_input')

  # make symlinks to all dwi intensity normalisation inputs in single directory
  for subj in glob.glob(os.path.join(all_subjects_dir, '*')):
    os.symlink(os.path.join(subj, 'dwi_preproc_bias.mif'), os.path.join('inorm_input', os.path.basename(subj) + '.mif'))
    os.symlink(os.path.join(subj, 'mask.mif'), os.path.join('mask_input', os.path.basename(subj) + '.mif'))

  run.command('dwiintensitynorm '  + 'inorm_input ' + 'mask_input ' + intensitynorm_output + ' ' + fa_template + ' ' + fa_wm_mask + ' -force')

  # link back to the files
  for subj in glob.glob(os.path.join(all_subjects_dir, '*')):
    try:
      print()
      os.symlink(os.path.join(intensitynorm_output, os.path.basename(subj) + '.mif'), os.path.join(subj, 'dwi_preproc_bn.mif'))
    except OSError, e:
      if e.errno == errno.EEXIST:
        os.remove(os.path.join(subj, 'dwi_preproc_bn.mif'))
        os.symlink(os.path.join(intensitynorm_output, os.path.basename(subj) + '.mif'), os.path.join(subj, 'dwi_preproc_bn.mif'))

  # file name definition
  dwi_preproc_file = os.path.join(subject_dir, 'dwi_preproc_bn.mif')
  app.checkOutputPath(dwi_preproc_file)
  wm_response_file = os.path.join(subject_dir, 'wm_response.txt')
  app.checkOutputPath(wm_response_file)
  gm_response_file = os.path.join(subject_dir, 'gm_response.txt')
  app.checkOutputPath(gm_response_file)
  csf_response_file = os.path.join(subject_dir, 'csf_response.txt')
  app.checkOutputPath(csf_response_file)

  print('averaging response functions')

  # Check output files exist
  wm_response_file = os.path.join(app.args.output_dir, 'average_wm_response.txt')
  app.checkOutputPath(wm_response_file)
  print('Check variable: wm_response file: ' + wm_response_file)
  gm_response_file = os.path.join(app.args.output_dir, 'average_gm_response.txt')
  app.checkOutputPath(gm_response_file)
  csf_response_file = os.path.join(app.args.output_dir, 'average_csf_response.txt')
  app.checkOutputPath(csf_response_file)


  input_wm_files = glob.glob(os.path.join(all_subjects_dir, '*', 'wm_response.txt'))
  print(input_wm_files)
  input_gm_files = glob.glob(os.path.join(all_subjects_dir, '*', 'gm_response.txt'))
  input_csf_files = glob.glob(os.path.join(all_subjects_dir, '*', 'csf_response.txt'))

  print('Check Command:  average_response ' + ' '.join(input_wm_files) + ' ' + wm_response_file + ' -force')
  run.command('average_response ' + ' '.join(input_wm_files) + ' ' + wm_response_file + ' -force')
  run.command('average_response ' + ' '.join(input_gm_files) + ' ' + gm_response_file + ' -force')
  run.command('average_response ' + ' '.join(input_csf_files) + ' ' + csf_response_file + ' -force')


# running participant level 2 (compute FODs)
elif app.args.analysis_level == "participant2":
  for subject_label in subjects_to_analyze:

    subject_dir = os.path.join(all_subjects_dir, subject_label)
    output_mask = os.path.join(subject_dir, 'mask.mif')
    output_fod = os.path.join(subject_dir, 'fod.mif')
    app.checkOutputPath(output_fod)
    output_gm = os.path.join(subject_dir, 'gm.mif')
    app.checkOutputPath(output_gm)
    output_csf = os.path.join(subject_dir, 'csf.mif')
    app.checkOutputPath(output_csf)

    input_to_csd = os.path.join(subject_dir, 'dwi_preproc_bn.mif')

    # Perform CSD
    run.command('dwi2fod msmt_csd ' + input_to_csd + ' -mask ' + output_mask + ' ' +
                os.path.join(app.args.output_dir, 'average_wm_response.txt') + ' ' +  os.path.join(app._tempDir, subject_label + 'fod.mif') + ' ' +
                os.path.join(app.args.output_dir, 'average_gm_response.txt') + ' ' + os.path.join(app._tempDir, subject_label + 'gm.mif') + ' ' +
                os.path.join(app.args.output_dir, 'average_csf_response.txt') + ' ' + os.path.join(app._tempDir, subject_label + 'csf.mif'))


# running group level 2 (generate FOD template)
elif app.args.analysis_level == 'group2':

  # TODO if user supplies a subset, then only output the template

  # Check if outputs exist
  fod_template = os.path.join(template_dir, 'fod_template.mif')
  app.checkOutputPath(fod_template)

  app.gotoTempDir()
  os.mkdir('fod_input')
  os.mkdir('mask_input')

  # Check if all members of subset exist
  if (len(subset) > 0):
    print('Using a group subset to compute population template' + str(subset))
    subject_labels = [os.path.basename(x) for x in glob.glob(os.path.join(all_subjects_dir, '*'))]
    for subj in subset:
      if subj not in subject_labels:
        app.error('subject label (' + os.path.basename(subj) + ') supplied as part of -group_subset option does exist in subjects directory')
      app.checkOutputPath(os.path.join(all_subjects_dir, subj, 'subject2template_warp.mif'))
      app.checkOutputPath(os.path.join(all_subjects_dir, subj, 'template2subject_warp.mif'))


  # make symlinks to all population_template inputs in single directory
  for subj in glob.glob(os.path.join(all_subjects_dir, '*')):
    if (len(subset) > 0):
      if os.path.basename(subj) in subset:
        os.symlink(os.path.join(subj, 'fod.mif'), os.path.join('fod_input', os.path.basename(subj) + '.mif'))
        os.symlink(os.path.join(subj, 'mask.mif'), os.path.join('mask_input', os.path.basename(subj) + '.mif'))
    else:
      os.symlink(os.path.join(subj, 'fod.mif'), os.path.join('fod_input', os.path.basename(subj) + '.mif'))
      os.symlink(os.path.join(subj, 'mask.mif'), os.path.join('mask_input', os.path.basename(subj) + '.mif'))

  # Compute FOD template
  if (len(subset) > 0):
    run.command('population_template fod_input -mask mask_input ' + os.path.join(app._tempDir, 'tmp.mif'))
    # Set a field in the header of the template to mark it as being generated as a subset or not. This is used in the next step
    run.command('mrconvert ' + os.path.join(app._tempDir, 'tmp.mif') + ' -header_set made_from_subset true ' + fod_template + ' -force')
  else:
    run.command('population_template fod_input -mask mask_input ' + os.path.join(app._tempDir, 'tmp.mif') + ' -warp_dir ' +  os.path.join(app._tempDir, 'warps'))
    run.command('mrconvert ' + os.path.join(app._tempDir, 'tmp.mif') + ' -header_set made_from_subset false ' + fod_template + ' -force')
    # Save all warps since we don't need to generate them in the next step if all subjects were used to make the template
    for subj in [os.path.basename(x) for x in glob.glob(os.path.join(all_subjects_dir, '*'))]:
      run.command('warpconvert -type warpfull2deformation -template ' + fod_template + ' '
                              + os.path.join(app._tempDir, 'warps', subj + '.mif') + ' '
                              + os.path.join(all_subjects_dir, subj, 'subject2template_warp.mif') + ' -force')
      run.command('warpconvert -type warpfull2deformation -from 2 -template ' + os.path.join(all_subjects_dir, subj, 'fod.mif') + ' '
                              + os.path.join(app._tempDir, 'warps', subj + '.mif') + ' '
                              + os.path.join(all_subjects_dir, subj, 'template2subject_warp.mif') + ' -force')


# running participant level 3 (register FODs, and warp masks)
elif app.args.analysis_level == "participant3":

  for subject_label in subjects_to_analyze:
    subject_dir = os.path.join(all_subjects_dir, subject_label)

    # Check existence of output
    mask_template = os.path.join(subject_dir, 'mask_in_template_space.mif')
    app.checkOutputPath(mask_template)

    # if the template was generated with a subset of the whole study, then we still need to register all subjects to that template
    if getHeaderProperty (os.path.join(template_dir, 'fod_template.mif'), 'made_from_subset') == 'true':
      subject2template = os.path.join(subject_dir, 'subject2template_warp.mif')
      app.checkOutputPath(subject2template)
      template2subject = os.path.join(subject_dir, 'template2subject_warp.mif')
      app.checkOutputPath(template2subject)
      # TODO If only a subset of images were used to make the template, then register all images to the template
      run.command('mrregister ' + os.path.join(subject_dir, 'fod.mif') + ' -mask1 ' + os.path.join(subject_dir, 'mask.mif')
                               + ' ' +  os.path.join(template_dir, 'fod_template.mif') + ' -nl_warp '
                               + subject2template + ' ' + template2subject + ' -force')


    # Transform masks into template space. This is used in the group3 analysis level for trimming the
    # final voxek mask to exclude voxels that do not contain data from all subjects
    run.command('mrtransform ' + os.path.join(subject_dir, 'mask.mif') + ' -warp ' + subject2template + ' -interp nearest '
                              + mask_template + ' -force')


# running group level 3 compute voxel and fixel masks, tractography, sift)
elif app.args.analysis_level == "group3":

  voxel_mask = os.path.join(template_dir, 'voxel_mask.mif')
  app.checkOutputPath(voxel_mask)
  fixel_mask = os.path.join(template_dir, 'fixel_mask')
  app.checkOutputPath(fixel_mask)
  tracks = os.path.join(template_dir, 'tracks.tck')
  app.checkOutputPath(tracks)
  tracks_sift = os.path.join(template_dir, 'tracks_sift.tck')
  app.checkOutputPath(tracks_sift)
  fod_template = os.path.join(template_dir, 'fod_template.mif')

  # Check tractography and SIFT input
  num_tracks_sift = 2000000;
  if app.args.num_tracks:
    num_tracks_sift = int(app.args.num_tracks_sift)
  num_tracks = 20000000;
  if app.args.num_tracks:
    num_tracks = int(app.args.num_tracks)
  if num_tracks_sift >= num_tracks:
    app.error('the tracks remaining after SIFT must be less than the number of tracks generated during tractography')

  # Compute voxel mask and intersect with all brain masks to ensure mask voxels are present in all subjects
  all_masks_in_template_space = glob.glob(os.path.join(all_subjects_dir, '*', 'mask_in_template_space.mif'))
  run.command('mrconvert -coord 3 0 ' + fod_template + ' - | mrthreshold - - | mrmath - ' + ' '.join(all_masks_in_template_space)
             + ' min ' + voxel_mask + ' -force')

  # Compute fixel mask
  delFolder(fixel_mask)
  run.command('fod2fixel -mask ' + voxel_mask + ' -fmls_peak_value 0.2 ' + fod_template + ' ' + fixel_mask + ' -force')

  # Perform tractography on the FOD template
  run.command('tckgen -angle 22.5 -maxlen 250 -minlen 10 -power 1.0 ' + fod_template + ' -seed_image '
             + voxel_mask + ' -mask ' + voxel_mask + ' -number ' + str(num_tracks) + ' ' + tracks + ' -force')

  # SIFT the streamlines
  run.command('tcksift ' + tracks + ' ' + fod_template + ' -term_number ' + str(num_tracks_sift) + ' ' + tracks_sift + ' -force')


# Warp FODs, Compute FD, reorient fixels, fixelcorrespondence , compute FC, compute FDC per subject
elif app.args.analysis_level == "participant4":

  for subject_label in subjects_to_analyze:
    subject_dir = os.path.join(all_subjects_dir, subject_label)

    # Fixel output all aligned in template space
    template_fd = os.path.join(template_dir, 'fd')
    app.checkOutputPath(template_fd)
    template_fc = os.path.join(template_dir, 'fc')
    app.checkOutputPath(template_fc)
    template_log_fc = os.path.join(template_dir, 'log_fc', subject_label + '.mif')
    app.checkOutputPath(template_log_fc)
    template_fdc = os.path.join(template_dir, 'fdc', subject_label + '.mif')
    app.checkOutputPath(template_fdc)


    # Transform FOD images (without reorientation)
    run.command('mrtransform -noreorientation ' + os.path.join(subject_dir, 'fod.mif')
                                               + ' -warp ' + os.path.join(subject_dir, 'subject2template_warp.mif') + ' '
                                               + os.path.join(app._tempDir, subject_label + 'fod_warped.mif'))


    # Segment each FOD into fixels and compute AFD integral per fixel
    delFolder(os.path.join(app._tempDir, subject_label + 'fixel_fd'))
    run.command('fod2fixel -afd fd.mif ' + os.path.join(app._tempDir, subject_label + 'fod_warped.mif')
                                        + ' -mask ' + os.path.join(template_dir, 'voxel_mask.mif') + ' '
                                        + os.path.join(app._tempDir, subject_label + 'fixel_fd'))

    # Reorient each fixel's direction (inplace) to account for the spatial tranformation
    run.command('fixelreorient -force ' + os.path.join(app._tempDir, subject_label + 'fixel_fd') + ' '
                                       + os.path.join(subject_dir, 'subject2template_warp.mif') + ' '
                                       + os.path.join(app._tempDir, subject_label + 'fixel_fd'))


    # For each fixel in template space, find the corresponding fixel in the subject and assign its AFD value.
    # Put all subjects AFD in the sample folder under the template directory ready for statistical analysis
    run.command('fixelcorrespondence ' + os.path.join(app._tempDir, subject_label + 'fixel_fd', 'fd.mif') + ' '
                                      + os.path.join(template_dir, 'fixel_mask') + ' '
                                      + template_fd + ' ' + subject_label + '.mif' + ' -force')

    # Compute FC
    run.command('warp2metric ' + os.path.join(subject_dir, 'subject2template_warp.mif')
                              + ' -fc ' + os.path.join(template_dir, 'fixel_mask') + ' '
                              + template_fc + ' ' + subject_label + '.mif' + ' -force')

    # Compute log FC
    if not os.path.exists(os.path.join(template_dir, 'log_fc')):
      os.mkdir(os.path.join(template_dir, 'log_fc'))
    run.command('mrcalc ' + os.path.join(template_fc, subject_label + '.mif') + ' -log ' + template_log_fc + ' -force')
    if not os.path.exists(os.path.join(template_dir, 'fdc')):
      os.mkdir(os.path.join(template_dir, 'fdc'))
    run.command('mrcalc ' + os.path.join(template_fd, subject_label + '.mif') + ' ' + os.path.join(template_fc, subject_label + '.mif')
                         + ' -mult ' + template_fdc + ' -force')

  # Copy index and directions file into log FC and FDC fixel directories
  run.command('cp ' + os.path.join(template_fc, 'index.mif') + ' '
                   + os.path.join(template_fc, 'directions.mif') + ' '
                   + os.path.join(template_dir, 'log_fc'))
  run.command('cp ' + os.path.join(template_fc, 'index.mif') + ' '
                   + os.path.join(template_fc, 'directions.mif') + ' '
                   + os.path.join(template_dir, 'fdc'))

# Perform fixel-based statistical inference in FD, FC and FDC
elif app.args.analysis_level == "group4":
  print('asdf')


app.complete()
