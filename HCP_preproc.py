#!/usr/bin/env python
import os, glob, shutil, sys, inspect, errno, json

from distutils.spawn import find_executable
from mrtrix3 import app, fsl, file, image, path, run

print ('Hello')

app.init ('Lea Vinokur (lea.vinokur@florey.edu.au)','Receive HCP unprocessed data and output HCP minimally pre-processed data'
                                'The analysis pipeline relies primarily on the MRtrix3 software package (www.mrtrix.org).')

app.cmdline.add_argument('in_dir', help='The directory with the input dataset, with HCP data compliant hirarchy ')

app.cmdline.add_argument('output_dir', help='The directory where the output files ')

app.cmdline.add_argument('-grad_coeffs', help='Provide the path to the gradient coefficients, if not default ')

app.cmdline.add_argument('-participant_label', help='The label(s) of the participant(s) that should be analyzed. The label '
                                                 'corresponds to sub-<participant_label> from the BIDS spec '
                                                 '(so it does not include "sub-"). If this parameter is not '
                                                 'provided all subjects should be analyzed. Multiple '
                                                 'participants can be specified with a space separated list.',
                                                  nargs='+')

app.cmdline.add_argument('-group_subset', help='Define a subset of participants to be used when generating the group-average FOD template and response functions. The subset is to be supplied as a comma separate list. Note the subset should be representable of your entire population and not biased towards one particular group. For example in a patient-control comparison, choose equal numbers of patients and controls. Used in group1 and group2 analysis levels.', nargs=1)

app.cmdline.add_argument('-extra_eddy_args', help='generic string of arguments to be passed to the DiffPreprocPipeline_Eddy.sh script'
                                          ' and and subsequently to the run_eddy.sh script and finally to the command '
                                          ' that actually invokes the eddy binary')

app.parse()


if app.isWindows():
  app.error('Script cannot be run on Windows due to FSL dependency')


subjects_to_analyze = []
# only for a subset of subjects
if app.args.participant_label:
  subjects_to_analyze = app.args.participant_label
# for all subjects
else:
  subject_dirs = glob.glob(os.path.join(app.args.in_dir, '*'))
  subjects_to_analyze = subject_dirs

# create a temporary directory for intermediate files
app.makeTempDir()

# read in group subset if supplied
subset = []
if app.args.group_subset:
  subset = app.args.group_subset[0].split(',')

eddy_args = ''
if app.args.extra_eddy_args:
  eddy_args = '-extra_eddy_args ' + app.args.extra_eddy_args
  print eddy_args


# running preproceding pipeline
print('performing denoising and gibbs ringing correction')

for label in subjects_to_analyze:
  label = os.path.split(label)[-1]
  print('running pre-processing for subject: ' + label)
  unproc_dir = os.path.join (app.args.in_dir, label, 'unprocessed', '3T', 'Diffusion')
  hcp_output_dir = os.path.join (app.args.in_dir, label, 'T1w', 'Diffusion')

  # Read all unprocessed DWI acquisitions
  all_unproc_images = glob.glob(os.path.join(unproc_dir, '*LR.nii*')) + glob.glob(os.path.join(unproc_dir, '*RL.nii*'))

  for unproc_image in all_unproc_images:

    #RUN denoise
    dn_image = os.path.basename(unproc_image).split('.')[0] + '_dn'
    dn_image = os.path.join(unproc_dir, dn_image)
    print('dwidenoise'  + ' ' + unproc_image + ' ' + dn_image + '.nii.gz')
    # TODO run.command('dwidenoise'  + ' ' + unproc_image + ' ' + dn_image + '.nii.gz')

    #RUN unring
    dg_image = os.path.basename(unproc_image).split('.')[0] + '_dndg'
    dg_image = os.path.join(unproc_dir,dg_image)
    print('mrdegibbs'  + ' ' + dn_image + '.nii.gz' + ' ' + dg_image + '.nii.gz')
    # TODO run.command('mrdegibbs'  + ' ' + unproc_image + ' ' + dg_image + '.nii.gz')


  #RUN HCP Pipelines
  print('performing HCP-Pipelines preprocessing')
  pe_dir = '1'
  all_pos_images = glob.glob(os.path.join(unproc_dir, '*LR_dndg.nii*'))
  all_pos_images = '@'.join(all_pos_images)
  all_neg_images = glob.glob(os.path.join(unproc_dir, '*RL_dndg.nii*'))
  all_neg_images = '@'.join(all_neg_images)
  gd_coeffs = '/home/lea/installs/Pipelines-3.21.0/global/config/coeff_SC72C_Skyra.grad'
  echo_spacing = '0.78'
  b0_maxbval = '50'
  # Specify Extra Eddy Argumentss here
  print('/Pipelines-3.21.0/DiffPreprocPipeline.sh' + ' --path=' + app.args.in_dir + ' --subject=' + label + ' --dwiname=Diffusion' + ' --PEdir=' + pe_dir +
  ' --posData=' +  all_pos_images + ' --negData' + all_neg_images + ' --gdcoeffs=' + gd_coeffs + ' --echospacing=' + echo_spacing
  + ' --b0maxbval' + b0_maxbval + ' ' + eddy_args)
  #TODO run.command ('DiffPreprocPipeline.sh' + ' --path=' + app.args.in_dir + ' --subject=' + label + ' --dwiname=Diffusion' + ' --PEdir=' + pe_dir
  # ' --posData=' +  all_pos_images + ' --negData' + all_neg_images + ' --gdcoeffs=' + gd_coeffs + ' --echospacing=' + echo_spacing
  # + ' --b0maxbval' + b0_maxbval + eddy_args)


  #TODO check output

  # Convert to BIDS structure
  subj_output = (app.args.output_dir + '/sub-' + label)
  print('subject output: ' +  subj_output)
  os.mkdir(subj_output)
  os.mkdir(os.path.join(subj_output,'dwi'))
  os.mkdir(os.path.join(subj_output,'anat'))

  dwi_file = (subj_output + '/dwi/' + 'sub-' +label + '_dwi.nii.gz')
  mask_file = (subj_output + '/dwi/' + 'sub-' +label + '_brainmask.nii.gz')
  bvec_file =(subj_output + '/dwi/' + 'sub-' +label + '_dwi.bvec')
  bval_file = (subj_output + '/dwi/' + 'sub-' +label + '_dwi.bval')
  t1w_file = (subj_output + '/anat/' + 'sub-' +label + '_acpc_dc_restore_1.25_T1w.nii.gz')

  print(os.path.join(hcp_output_dir, 'data.nii.gz') + '  --->   ' + dwi_file)
  print(os.path.join(hcp_output_dir, 'nodif_brain.mask.nii.gz') + '  --->  ' + mask_file)
  print(os.path.join(hcp_output_dir, 'bvecs') + ' --->  ' + bvec_file)
  print(os.path.join(hcp_output_dir, 'bvals') + '  --->   ' + bval_file)
  print(os.path.join(app.args.in_dir, label, 'T1w', 'T1w_acpc_dc_restore_1.25.nii.gz') + '  --->  ' + t1w_file)


  # shutil.move(os.path.join(hcp_output_dir, 'data.nii.gz') , dwi_file)
  # shutil.move(os.path.join(hcp_output_dir, 'nodif_brain.mask.nii.gz') , mask_file)
  # shutil.move(os.path.join(hcp_output_dir, 'bvecs') , bvec_file)
  # shutil.move(os.path.join(hcp_output_dir, 'bvals') , bval_file)
  # shutil.move(os.path.join(app.args.in_dir, label, 'T1w', 'T1w_acpc_dc_restore_1.25.nii.gz') , t1w_file)
bids_dic = {
        'BIDSVersion' : '1.0.2',
        'License' : 'This dataset is made available under the Public Domain Dedication and License v1.0, whose full text can be found at http://www.opendatacommons.org/licenses/pddl/1.0/. We hope that all users will follow the ODC Attribution/Share-Alike Community Norms (http://www.opendatacommons.org/norms/odc-by-sa/); in particular, while not legally required, we hope that all users of the data will acknowledge the OpenfMRI project and NSF Grant OCI-1131441 (R. Poldrack, PI) in any publications.' ,
        'Name': 'HCP locally pre-processed data'
        }

print('writing json')
# jsonData = json.dumps(bids_dic)
# print(jsonData)
with open(os.path.join(app.args.output_dir,'dataset_decription.json'), 'w') as f:
    json.dump(bids_dic, f)





app.complete()
