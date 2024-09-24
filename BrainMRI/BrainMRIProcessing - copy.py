from itertools import dropwhile
import numpy as np
import subprocess
import fnmatch
import shutil
import codecs
import math
import sys
import os
from flask import Flask, render_template, jsonify, request
import threading
import json


app = Flask(__name__)

datadir = ""  # 定义全局变量

@app.route('/upload', methods=['POST'])
def upload():
    global datadir  # 声明使用全局变量
    data = request.get_json()
    file_path = data.get('path')

    if file_path and os.path.isdir(file_path):
        datadir = file_path  # 更新全局变量
        return jsonify({'message': 'data path set successfully', 'datadir': datadir})
    else:
        return jsonify({'message': 'Invalid data path'}), 400

@app.route('/clear', methods=['POST'])
def clear():
    global datadir
    if datadir:
        datadir = ""  # 清空全局变量
        return jsonify({'message': 'data path cleared successfully'})
    else:
        return jsonify({'message': 'No data path to clear'}), 400

# 执行脚本命令
@app.route('/runcmd', methods = ['GET'])
def excute_cmd():
    try:
        # 执行命令
        result = subprocess.run(['python', 'BrainMRIProcessing.py'], capture_output=True, text=True)
        output = result.stdout
        error = result.stderr

        # 返回结果
        return jsonify({
            'output': output,
            'error': error,
            'return_code': result.returncode
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500



TmplateFSL = "/usr/local/freesurfer/7.4.1/Freesurfer_MNI152_Template"
MRtrix3loc = "/home/ac/mrtrix3"
FreeSurferloc = "/usr/local/freesurfer/7.4.1"
TmplateFreeSrufer = "/usr/local/freesurfer/7.4.1/Freesurfer_MNI152_Template"
Tenser_statistics = ["L1","L2","L3","MO","S0","ADC","FA","AD","RD","CS","CP","CL","VALUE","VECTOR"]
Tract_Locat = ["Left","Right","Whole"]

datadir = "/home/ac/BrainAnalysis/BrainData/3104-2011-02-14"


def SourceDataPreprocess( root_subject ):
    patten_DTI = "DTI_Processing"
    patten_T1 = "T1_source_bert"
    DTI = 0
    T1 = 0
    os.chdir( root_subject )

    for filename in os.listdir( root_subject ):
        if fnmatch.fnmatch( filename, patten_DTI):
            DTI = 1
            print ("DTI=1")

    for filename in os.listdir( root_subject ):
        if fnmatch.fnmatch( filename, patten_T1):
            T1 = 1
            print ("T1=1")


    for filename in os.listdir( root_subject ):
        if filename.endswith( "_DTI" ) and ( DTI == 0):
            DTI_source = filename
            subprocess.call("mrconvert" + " " + DTI_source + " " + "DTI_source.nii.gz" , shell=True)
            subprocess.call("dwidenoise" + " " + DTI_source + " " + DTI_source+"_denoise.mif", shell=True)
            subprocess.call("dwifslpreproc" + " " + DTI_source+"_denoise.mif" + " "+DTI_source+"_denoise_preproc.mif"+" "+"-rpe_none"+" "+"-pe_dir"+" "+"j-" , shell=True)
            subprocess.call("dwibiascorrect"  + " " + "fsl" + " " + DTI_source + "_denoise_preproc.mif" + " " + DTI_source+"_denoise_preproc_biascorr.mif", shell=True)
            subprocess.call("mrinfo" + " " + DTI_source + "_denoise_preproc_biascorr.mif" + " " +"-export_grad_fsl" + " " + DTI_source + "_denoise_preproc_biascorr.bvecs" + " " +  DTI_source + "_denoise_preproc_biascorr.bvals" , shell=True)
            subprocess.call("mrconvert" + " " + DTI_source+"_denoise_preproc_biascorr.mif" + " " + DTI_source+"_denoise_preproc_biascorr.nii.gz" , shell=True)
            subprocess.call("mkdir" + " " + "DTI_Processing", shell=True)
            subprocess.call("cp" + " " + DTI_source+"_denoise_preproc_biascorr.nii.gz"+ " " + "DTI_processed.nii.gz", shell=True)
            subprocess.call("cp" + " " + DTI_source+"_denoise_preproc_biascorr.bvecs"+ " " + "DTI_processed.bvecs", shell=True)
            subprocess.call("cp" + " " + DTI_source+"_denoise_preproc_biascorr.bvals"+ " " + "DTI_processed.bvals", shell=True)
            subprocess.call("mv" + " " + DTI_source+"_denoise.mif"+ " " + "DTI_Processing", shell=True)
            subprocess.call("mv" + " " + DTI_source+"_denoise_preproc.mif"+ " " + "DTI_Processing", shell=True)
            subprocess.call("mv" + " " + DTI_source+"_denoise_preproc_biascorr.mif"+ " " + "DTI_Processing", shell=True)
            subprocess.call("mv" + " " + DTI_source+"_denoise_preproc_biascorr.nii.gz"+ " " + "DTI_Processing", shell=True)
            subprocess.call("mv" + " " + DTI_source+"_denoise_preproc_biascorr.bvecs"+ " " + "DTI_Processing", shell=True)
            subprocess.call("mv" + " " + DTI_source+"_denoise_preproc_biascorr.bvals"+ " " + "DTI_Processing", shell=True)

    for filename in os.listdir( root_subject ):
        if filename.endswith( "T1" ) and ( T1 == 0 ):
            print(filename)
            T1_source = filename
            subprocess.call("mrconvert " + " " + T1_source + " " + "T1_source.nii.gz", shell=True)
            subprocess.call("SUBJECTS_DIR="+ root_subject +"; recon-all" + " " +"-i"+ " " +"T1_source.nii.gz"+ " " + "-s" + " "+ "T1_source_bert" + " " + "-all" + " " + "-openmp 8", shell=True)



### Register WM_mask to DTI function:
### argument: root_subject is the root path of the current subject
def RegFS2DTI( root_subject ):
    os.chdir( root_subject )
    subprocess.call("mkdir" + " " + "RegFS_to_DTI", shell=True)
    subprocess.call("mrconvert" + " " +"T1_source_bert/mri/wm.seg.mgz"+ " " + root_subject +"/RegFS_to_DTI/wm.seg.nii.gz", shell=True)
    subprocess.call("flirt" + " " +"-in"+ " " + "RegFS_to_DTI/wm.seg.nii.gz"+" " + "-ref"+ " " + "DTI_processed.nii.gz"+ " " + "-omat"+ " " + "RegFS_to_DTI/wm.segFS_to_DTI.mat", shell=True)
    subprocess.call("flirt" + " " +"-in"+ " " + "RegFS_to_DTI/wm.seg.nii.gz"+" " + "-ref"+ " " + "DTI_processed.nii.gz"+ " " + "-applyxfm"+ " " + "-init"+ " " + "RegFS_to_DTI/wm.segFS_to_DTI.mat"+ " " + "-out" +" " + "RegFS_to_DTI/FS_wmmask.nii.gz", shell=True)


### ACT preprocess function:
### argument: root_subject is the root path of the current subject
def ACTPreprocess( root_subject ):
    os.chdir( root_subject )
    subprocess.call("mkdir" + " " + "ACT", shell=True)
    subprocess.call("5ttgen" + " " + "fsl"+ " " + "T1_source_bert/mri/orig.mgz"+ " " + "ACT/t1_orig_5TT_nocrop.mif" " " + "-nocrop", shell=True)
    subprocess.call("5tt2vis" + " " + "ACT/t1_orig_5TT_nocrop.mif"+ " " + "ACT/t1_orig_5TT_nocrop_vis.mif", shell=True)
    subprocess.call("5tt2gmwmi" + " " +"ACT/t1_orig_5TT_nocrop.mif"+ " " + "ACT/t1_orig_5TT_nocrop_gmwmi.mif", shell=True)
    subprocess.call("mrconvert" + " " +"-coord"+ " " + "3"+" " + "2"+ " " + "ACT/t1_orig_5TT_nocrop.mif"+ " " + "ACT/t1_orig_5TT_nocrop_wm4d.mif", shell=True)
    subprocess.call("mrmath" + " " +"ACT/t1_orig_5TT_nocrop_wm4d.mif"+ " " + "mean"+" " + "-axis"+ " " + "3"+ " " + "ACT/t1_orig_5TT_nocrop_wm.mif", shell=True)
    subprocess.call("mrconvert" + " " +"ACT/t1_orig_5TT_nocrop_wm.mif"+ " " + "ACT/5TT_wmmask.nii.gz", shell=True)
    subprocess.call("flirt" + " " +"-in"+ " " + "ACT/5TT_wmmask.nii.gz"+" " + "-ref"+ " " + "DTI_processed.nii.gz"+ " " + "-omat"+ " " + "ACT/5TTwmmask_to_DTI.mat", shell=True)
    subprocess.call("flirt" + " " +"-in"+ " " + "ACT/5TT_wmmask.nii.gz"+" " + "-ref"+ " " + "DTI_processed.nii.gz"+ " " + "-applyxfm"+ " " + "-init"+ " " + "ACT/5TTwmmask_to_DTI.mat"+ " " + "-out" +" " + "ACT/5TT_wmmask.nii.gz", shell=True)


### estimate fiber orientation distributions function:
### argument: root_subject is the root path of the current subject
def FODestimate( root_subject ):
    os.chdir( root_subject )
    subprocess.call("dwi2response" + " " +"tournier"+ " " + "DTI_processed.nii.gz"+" " + "DTI_processed_response.txt"+ " " + "-fslgrad"+ " " + "DTI_processed.bvecs"+ " " + "DTI_processed.bvals", shell=True)
    subprocess.call("dwi2mask" + " " +"DTI_processed.nii.gz"+ " " + "DTI_processed_wholebrainmask.mif"+" " + "-fslgrad"+ " " + "DTI_processed.bvecs"+ " " + "DTI_processed.bvals", shell=True)
    subprocess.call("dwi2fod" + " " +"csd"+ " " + "DTI_processed.nii.gz"+" " + "DTI_processed_response.txt"+ " " + "DTI_processed_FSwmmask_fod.mif"+ " " + "-mask"+ " " + "RegFS_to_DTI/FS_wmmask.nii.gz" + " "+  "-fslgrad"+ " " + "DTI_processed.bvecs"+ " " + "DTI_processed.bvals", shell=True)
    subprocess.call("dwi2fod" + " " +"csd"+ " " + "DTI_processed.nii.gz"+" " + "DTI_processed_response.txt"+ " " + "DTI_processed_5TTwmmask_fod.mif"+ " " + "-mask"+ " " + "ACT/5TT_wmmask.nii.gz" + " "+ "-fslgrad"+ " " + "DTI_processed.bvecs"+ " " + "DTI_processed.bvals", shell=True)
    # subprocess.call("mrview" + " " + "DTI_processed.nii.gz"+" " + "-odf.load_sh"+ " " + "DTI_processed_FSwmmask_fod.mif", shell=True)


### Deterministic Tractography Tensor_Det:(MRtrix3)
### argument: root_subject is the root path of the current subject
def GenTracts_DetermininsticTensorDet( root_subject ):
    os.chdir( root_subject )
    subprocess.call("mkdir" + " " + "Output_Deterministic_TensorDet", shell=True)
    subprocess.call("tckgen" + " " +"-algorithm"+ " " + "Tensor_Det"+" " + "DTI_processed.nii.gz"+ " " + "Output_Deterministic_TensorDet/DTI_processed_TensorDet_FSwmmask_seedimage_0.5M.tck"+ " " + "-seed_image"+ " " + "RegFS_to_DTI/FS_wmmask.nii.gz"+ " " + "-mask"+ " " + "RegFS_to_DTI/FS_wmmask.nii.gz"+ " " + "-select"+ " " + "500000"+ " "+ "-fslgrad"+ " " + "DTI_processed.bvecs"+ " " + "DTI_processed.bvals", shell=True)
    subprocess.call("tckconvert" + " " +"Output_Deterministic_TensorDet/DTI_processed_TensorDet_FSwmmask_seedimage_0.5M.tck"+ " " + "Output_Deterministic_TensorDet/DTI_processed_TensorDet_FSwmmask_seedimage_0.5M.vtk", shell=True)
    subprocess.call("tcksift" + " " + "Output_Deterministic_TensorDet/DTI_processed_TensorDet_FSwmmask_seedimage_0.5M.tck"+" " + "DTI_processed_FSwmmask_fod.mif"+ " " + "Output_Deterministic_TensorDet/DTI_processed_TensorDet_FSwmmask_seedimage_0.5M_sift0.1M.tck"+ " " + "-term_number"+ " " + "100000", shell=True)
    subprocess.call("tckconvert" + " " +"Output_Deterministic_TensorDet/DTI_processed_TensorDet_FSwmmask_seedimage_0.5M_sift0.1M.tck"+ " " + "Output_Deterministic_TensorDet/DTI_processed_TensorDet_FSwmmask_seedimage_0.5M_sift0.1M.vtk", shell=True)


### Automatically-constrained Tractography  seed_dynamic:(MRtrix3)
### argument: root_subject is the root path of the current subject
def GenTracts_ACTseedGMWMI( root_subject ):
    os.chdir( root_subject )
    subprocess.call("mkdir" + " " + "Output_ACT", shell=True)
    subprocess.call("tckgen" + " " +"-act"+ " " + "ACT/t1_orig_5TT_nocrop.mif"+" " + "DTI_processed_5TTwmmask_fod.mif"+ " " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck"+ " " + "-seed_gmwmi"+ " " + "ACT/t1_orig_5TT_nocrop_gmwmi.mif"+ " " + "-select"+ " " + "500000"+ " "+ "-fslgrad"+ " " + "DTI_processed.bvecs"+ " " + "DTI_processed.bvals", shell=True)
    subprocess.call("tckconvert" + " " +"Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck"+ " " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.vtk", shell=True)
    subprocess.call("tcksift" + " " +"-act"+ " " + "ACT/t1_orig_5TT_nocrop.mif"+" " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck"+ " " + "DTI_processed_5TTwmmask_fod.mif"+ " " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M.tck"+ " " + "-term_number"+ " " + "100000", shell=True)
    subprocess.call("tckconvert" + " " +"Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M.tck"+ " " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M.vtk", shell=True)


### Probablistic Tractography Tensor_Prob:(MRtrix3)
### argument: root_subject is the root path of the current subject
def GenTracts_ProbabilisticTensorProb( root_subject ):
    os.chdir( root_subject )
    subprocess.call("mkdir" + " " + "Output_Probabilistic_Tensor_Prob", shell=True)
    subprocess.call("tckgen" + " " +"-algorithm"+ " " + "Tensor_Prob"+" " + "DTI_processed.nii.gz"+ " " + "Output_Probabilistic_Tensor_Prob/DTI_processed_TensorProb_FSwmmask_seedimage_0.5M.tck"+ " " + "-seed_image"+ " " + "RegFS_to_DTI/FS_wmmask.nii.gz"+ " " + "-mask"+ " " + "RegFS_to_DTI/FS_wmmask.nii.gz"+ " " + "-select"+ " " + "500000"+ " "+ "-fslgrad"+ " " + "DTI_processed.bvecs"+ " " + "DTI_processed.bvals", shell=True)
    subprocess.call("tckconvert" + " " +"Output_Probabilistic_Tensor_Prob/DTI_processed_TensorProb_FSwmmask_seedimage_0.5M.tck"+ " " + "Output_Probabilistic_Tensor_Prob/DTI_processed_TensorProb_FSwmmask_seedimage_0.5M.vtk", shell=True)
    subprocess.call("tcksift" + " " + "Output_Probabilistic_Tensor_Prob/DTI_processed_TensorProb_FSwmmask_seedimage_0.5M.tck"+" " + "DTI_processed_FSwmmask_fod.mif"+ " " + "Output_Probabilistic_Tensor_Prob/DTI_processed_TensorProb_FSwmmask_seedimage_0.5M_sift0.1M.tck"+ " " + "-term_number"+ " " + "100000", shell=True)
    subprocess.call("tckconvert" + " " +"Output_Probabilistic_Tensor_Prob/DTI_processed_TensorProb_FSwmmask_seedimage_0.5M_sift0.1M.tck"+ " " + "Output_Probabilistic_Tensor_Prob/DTI_processed_TensorProb_FSwmmask_seedimage_0.5M_sift0.1M.vtk", shell=True)


### Register T1 image( in FreeSurfer space ) to MNI152 space
### argument: root_subject is the root path of the current subject
def RegT12MNI152( root_subject ):
    os.chdir( root_subject )
    subprocess.call("mkdir" + " " + "RegT1_to_MNI152", shell=True)
    subprocess.call("mrconvert" + " " + "T1_source_bert/mri/brain.mgz"+" " + "RegT1_to_MNI152/brainFS.nii.gz", shell=True)
    subprocess.call("mrconvert" + " " + "T1_source_bert/mri/orig.mgz"+" " + "RegT1_to_MNI152/T1FS.nii.gz", shell=True)

    subprocess.call("flirt" + " " +"-in"+ " " + "RegT1_to_MNI152/brainFS.nii.gz"+" " + "-ref"+ " " + TmplateFSL + "/MNI152_T1_1mm_brain.nii"+ " " + "-omat"+ " " + "RegT1_to_MNI152/brainFS_toMNI152FSL.mat", shell=True)
    subprocess.call("flirt" + " " +"-in"+ " " + "RegT1_to_MNI152/brainFS.nii.gz"+" " + "-ref"+ " " + TmplateFSL + "/MNI152_T1_1mm_brain.nii"+ " " + "-applyxfm"+ " " + "-init"+ " " + "RegT1_to_MNI152/brainFS_toMNI152FSL.mat"+ " " + "-out" +" " + "RegT1_to_MNI152/brainFS_in_MNI152FSL.nii.gz", shell=True)
    subprocess.call("flirt" + " " +"-in"+ " " + "RegT1_to_MNI152/T1FS.nii.gz"+" " + "-ref"+ " " + TmplateFSL + "/MNI152_T1_1mm.nii"+ " " + "-applyxfm"+ " " + "-init"+ " " + "RegT1_to_MNI152/brainFS_toMNI152FSL.mat"+ " " + "-out" +" " + "RegT1_to_MNI152/T1FS_in_MNI152FSL.nii.gz", shell=True)



# ##########################################################################################################################################################################
# ####===============================                              Warp fiber tracts(.tck) to MNI152                            =======================================####
# ##########################################################################################################################################################################
# # #
# #
# # # #--------------------------------------------------------------------------------------------------------------------------------------------#
# # # #                                                      Warp Method 1:    suitable for Disease_3T_liu_yan                                    #
# # # #--------------------------------------------------------------------------------------------------------------------------------------------#
# #
# #
# # # subprocess.call("mkdir" + " " + "Regtck_to_MNI152", shell=True)
# # # os.chdir("Regtck_to_MNI152")
# # #
# # # # ANTS registration:(ANTS)
# # # subprocess.call("mkdir" + " " + "ANTS", shell=True )
# # # os.chdir("ANTS")
# # # subprocess.call("ANTS 3 -m CC[/home/chqxu/MNI152_Template_FSL/MNI152_T1_1mm.nii, ../../RegT1_to_MNI152/T1FS.nii.gz, 1, 5] -t SyN[0.5] -r Gauss[2,0] -o T1FS_to_MNI152FSL_synants.nii -i 30x90x20 --use-Histogram-Matching", shell=True)
# # # os.chdir("..")
# # #
# # # # Create an initial warp image:(MRtrix3
# # # subprocess.call("mkdir" + " " + "WarpMNI152FSL", shell=True)
# # # subprocess.call("mkdir" + " " + "MNI152FSL2tck", shell=True)
# # # subprocess.call("warpinit" + " " +TmplateFSL + "/MNI152_T1_1mm.nii"+ " " + "WarpMNI152FSL/WarpMNI152FSL-[].nii", shell=True)
# # #
# # # # Use ANTS to warp the IDs:(ANTS)
# # # subprocess.call("for i in {0..2}; do WarpImageMultiTransform 3 WarpMNI152FSL/WarpMNI152FSL-${i}.nii MNI152FSL2tck/MNI152FSL2tck-${i}.nii -R /home/chqxu/MNI152_Template_FSL/MNI152_T1_1mm.nii -i ANTS/T1FS_to_MNI152FSL_synantsAffine.txt ANTS/T1FS_to_MNI152FSL_synantsInverseWarp.nii; done", shell=True)
# # # subprocess.call("WarpImageMultiTransform 3 WarpMNI152FSL/WarpMNI152FSL-0.nii MNI152FSL2tck/MNI152FSL2tck-0.nii -R /home/chqxu/MNI152_Template_FSL/MNI152_T1_1mm.nii -i ANTS/T1FS_to_MNI152FSL_synantsAffine.txt ANTS/T1FS_to_MNI152FSL_synantsInverseWarp.nii", shell=True)
# # # subprocess.call("WarpImageMultiTransform 3 WarpMNI152FSL/WarpMNI152FSL-1.nii MNI152FSL2tck/MNI152FSL2tck-1.nii -R /home/chqxu/MNI152_Template_FSL/MNI152_T1_1mm.nii -i ANTS/T1FS_to_MNI152FSL_synantsAffine.txt ANTS/T1FS_to_MNI152FSL_synantsInverseWarp.nii", shell=True)
# # # subprocess.call("WarpImageMultiTransform 3 WarpMNI152FSL/WarpMNI152FSL-2.nii MNI152FSL2tck/MNI152FSL2tck-2.nii -R /home/chqxu/MNI152_Template_FSL/MNI152_T1_1mm.nii -i ANTS/T1FS_to_MNI152FSL_synantsAffine.txt ANTS/T1FS_to_MNI152FSL_synantsInverseWarp.nii", shell=True)
# # #
# # #
# # # subprocess.call("warpcorrect" + " " +"MNI152FSL2tck/MNI152FSL2tck-[].nii "+ " " + "MNI152FSL2tck/MNI152FSL2tck_correct.mif", shell=True)
# # # # Deterministic-Tensor_Det
# # # subprocess.call("tcknormalise" + " " +"../Output_Deterministic_TensorDet/DTI_processed_TensorDet_FSwmmask_seedimage_0.5M_sift0.1M.tck"+ " " + "MNI152FSL2tck/MNI152FSL2tck_correct.mif"+ " " + "../Output_Deterministic_TensorDet/DTI_processed_TensorDet_FSwmmask_seedimage_0.5M_sift0.1M_warpMNI152FSL.tck", shell=True)
# # # # ACT-seed_dynamic
# # # subprocess.call("tcknormalise" + " " +"../Output_ACT/DTI_processed_ACT_5TTwmmask_seed_dynamic_0.5M_sift0.1M.tck"+ " " + "MNI152FSL2tck/MNI152FSL2tck_correct.mif"+ " " + "../Output_ACT/DTI_processed_ACT_5TTwmmask_seed_dynamic_0.5M_sift0.1M_warpMNI152FSL.tck", shell=True)
# # # # ACT-seed_gmwmi
# # # subprocess.call("tcknormalise" + " " +"../Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M.tck"+ " " + "MNI152FSL2tck/MNI152FSL2tck_correct.mif"+ " " + "../Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M_warpMNI152FSL.tck", shell=True)
# # # os.chdir("..")
# # # subprocess.call("ls", shell = True)
#
# #
# # # ##--------------------------------------------------------------------------------------------------------------------------------------------#
# # # ##                                                      Warp Method 2:    suitable for PPMI Data                                    #
# # # ##--------------------------------------------------------------------------------------------------------------------------------------------#
# # #
# # subprocess.call("mkdir" + " " + "Regtck_to_MNI152", shell=True)
# # os.chdir("Regtck_to_MNI152")
#
# # # FIXED="../../RegT1_to_MNI152/T1FS.nii.gz"
# # # MOVING=TmplateFSL + "/MNI152_T1_1mm.nii"
#
# # subprocess.call("mkdir" + " " + "ANTS", shell=True )
# # os.chdir("ANTS")
# #
# # subprocess.call("antsRegistration \
# #     --verbose 1 \
# #     --dimensionality 3 \
# #     --output transforms \
# #     --initial-moving-transform [ ../../RegT1_to_MNI152/T1FS.nii.gz, /home/chqxu/MNI152_Template_FSL/MNI152_T1_1mm.nii, 1 ] \
# #     --initialize-transforms-per-stage 0 \
# #     --interpolation LanczosWindowedSinc \
# #     --transform Affine[ 0.1 ] \
# #     --metric MI[ ../../RegT1_to_MNI152/T1FS.nii.gz, /home/chqxu/MNI152_Template_FSL/MNI152_T1_1mm.nii, 1, 32, Regular, 0.25 ] \
# #     --convergence [ 1000x500x250x0, 1e-06, 10 ] \
# #     --smoothing-sigmas 3x2x1x0vox \
# #     --shrink-factors 8x4x2x1 \
# #     --use-estimate-learning-rate-once 1 \
# #     --use-histogram-matching 1 \
# #     --transform GaussianDisplacementField[0.1,1,1] \
# #     --metric MI[ ../../RegT1_to_MNI152/T1FS.nii.gz, /home/chqxu/MNI152_Template_FSL/MNI152_T1_1mm.nii, 1, 32, Regular, 0.25 ] \
# #     --convergence [ 1000x500x250x0, 1e-06, 10 ] \
# #     --smoothing-sigmas 3x2x1x0vox \
# #     --shrink-factors 8x4x2x1 \
# #     --use-estimate-learning-rate-once 1 \
# #     --use-histogram-matching 1 \
# #     --winsorize-image-intensities [ 0.005, 0.955 ] | tee -a ants.log", shell=True )
# #
# # os.chdir("..")
# #
# # subprocess.call("mkdir" + " " + "WarpMNI152FSL", shell=True)
# # subprocess.call("mkdir" + " " + "MNI152FSL2tck", shell=True)
# # subprocess.call("warpinit /home/chqxu/MNI152_Template_FSL/MNI152_T1_1mm_mrpad10.nii WarpMNI152FSL/WarpMNI152FSL-[].nii.gz -force", shell=True )
# #
# # subprocess.call("antsApplyTransforms -d 3 -i WarpMNI152FSL/WarpMNI152FSL-0.nii.gz -o MNI152FSL2tck/MNI152FSL2tck-0.nii.gz  -r ../RegT1_to_MNI152/T1FS.nii.gz -t ANTS/transforms0GenericAffine.mat -f 123456789", shell=True)
# # subprocess.call("mrcalc MNI152FSL2tck/MNI152FSL2tck-0.nii.gz  123456789 -eq nan MNI152FSL2tck/MNI152FSL2tck-0.nii.gz  -if MNI152FSL2tck/MNI152FSL2tck-0.nii.gz  -force", shell=True)
# #
# # subprocess.call("antsApplyTransforms -d 3 -i WarpMNI152FSL/WarpMNI152FSL-1.nii.gz -o MNI152FSL2tck/MNI152FSL2tck-1.nii.gz  -r ../RegT1_to_MNI152/T1FS.nii.gz -t ANTS/transforms0GenericAffine.mat -f 123456789", shell=True)
# # subprocess.call("mrcalc MNI152FSL2tck/MNI152FSL2tck-1.nii.gz  123456789 -eq nan MNI152FSL2tck/MNI152FSL2tck-1.nii.gz  -if MNI152FSL2tck/MNI152FSL2tck-1.nii.gz  -force", shell=True)
# #
# # subprocess.call("antsApplyTransforms -d 3 -i WarpMNI152FSL/WarpMNI152FSL-2.nii.gz -o MNI152FSL2tck/MNI152FSL2tck-2.nii.gz  -r ../RegT1_to_MNI152/T1FS.nii.gz -t ANTS/transforms0GenericAffine.mat -f 123456789", shell=True)
# # subprocess.call("mrcalc MNI152FSL2tck/MNI152FSL2tck-2.nii.gz  123456789 -eq nan MNI152FSL2tck/MNI152FSL2tck-2.nii.gz  -if MNI152FSL2tck/MNI152FSL2tck-2.nii.gz  -force", shell=True)
#
# #
# # # Recombine the warp file
# # subprocess.call("warpcorrect -force MNI152FSL2tck/MNI152FSL2tck-[].nii.gz MNI152FSL2tck/MNI152FSL2tck_correct.mif", shell = True)
#
# # subprocess.call("mrtransform /home/chqxu/MNI152_Template_FSL/MNI152_T1_1mm_mrpad10.nii -warp MNI152FSL2tck/MNI152FSL2tck_correct.mif MNI152FSL2tck/MNI152_transformed.mif", shell = True)
# #
# # subprocess.call("tcknormalise ../Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M.tck MNI152FSL2tck/MNI152FSL2tck_correct.mif ../Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M_warpMNI152FSL.tck -force", shell = True)
# # subprocess.call("tckconvert" + " " +"../Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M_warpMNI152FSL.tck"+ " " + "../Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M_warpMNI152FSL.vtk -force", shell=True)
# #
# # os.chdir("..")
# #
# # #
#
# #
# ##########################################################################################################################################################################
# ####===============================                              Inter-Registration: MNI152 to T1                           =======================================####
# ##########################################################################################################################################################################
# ## calculate registration matrix
### Register  MNI152 space to T1 image( in FreeSurfer space )
### argument: root_subject is the root path of the current subject
def RegMNI1522T1( root_subject ):
    os.chdir( root_subject )
    subprocess.call("mkdir" + " " + "RegMNI152_to_T1", shell=True)
    subprocess.call("mrconvert" + " " + "T1_source_bert/mri/brain.mgz"+" " + "RegMNI152_to_T1/brainFS.nii.gz", shell=True)
    subprocess.call("mrconvert" + " " + "T1_source_bert/mri/orig.mgz"+" " + "RegMNI152_to_T1/T1FS.nii.gz", shell=True)

    subprocess.call("flirt" + " " +"-in"+ " " + TmplateFSL + "/MNI152_T1_1mm_brain.nii"+" " + "-ref"+ " " + "RegMNI152_to_T1/brainFS.nii.gz" + " " + "-omat"+ " " + "RegMNI152_to_T1/MNI152FSL_to_brainFS.mat", shell=True)
    subprocess.call("flirt" + " " +"-in"+ " " + TmplateFSL + "/MNI152_T1_1mm_brain.nii"+" " + "-ref"+ " " + "RegMNI152_to_T1/brainFS.nii.gz" + " " + "-applyxfm"+ " " + "-init"+ " " + "RegMNI152_to_T1/MNI152FSL_to_brainFS.mat"+ " " + "-out" +" " + "RegMNI152_to_T1/MNI152FSL_in_brainFS.nii.gz", shell=True)
    subprocess.call("flirt" + " " +"-in"+ " " +  TmplateFSL + "/MNI152_T1_1mm.nii"+" " + "-ref"+ " " + "RegMNI152_to_T1/T1FS.nii.gz" + " " + "-applyxfm"+ " " + "-init"+ " " + "RegMNI152_to_T1/MNI152FSL_to_brainFS.mat"+ " " + "-out" +" " + "RegMNI152_to_T1/MNI152FSL_T1FS.nii.gz", shell=True)

# # SN region registration
def SNRegMNI1522T1( root_subject ):
    os.chdir( root_subject )
    subprocess.call("mkdir" + " " + "RegMNI152_to_T1/SN", shell=True)
    subprocess.call("transformconvert" + " " +"RegMNI152_to_T1/MNI152FSL_to_brainFS.mat"+ " " +  TmplateFSL + "/MNI152_T1_1mm_brain.nii"+" " + "RegMNI152_to_T1/brainFS.nii.gz"+ " " + "flirt_import" + " " + "RegMNI152_to_T1/MNI152FSL_to_brainFS_Mrtrix3format.txt", shell=True)
    subprocess.call("mrtransform" + " " +TmplateFSL + "/Substantia_Nigra/lh_SN_cluster3_1_ncut_1.nii.gz"+ " " + "-linear" +" " + "RegMNI152_to_T1/MNI152FSL_to_brainFS_Mrtrix3format.txt"+ " " + "RegMNI152_to_T1/SN/lh_SN_1.nii.gz", shell=True)
    subprocess.call("mrtransform" + " " +TmplateFSL + "/Substantia_Nigra/lh_SN_cluster3_2_ncut_1.nii.gz"+ " " + "-linear" +" " + "RegMNI152_to_T1/MNI152FSL_to_brainFS_Mrtrix3format.txt"+ " " + "RegMNI152_to_T1/SN/lh_SN_2.nii.gz", shell=True)
    subprocess.call("mrtransform" + " " +TmplateFSL + "/Substantia_Nigra/lh_SN_cluster3_3_ncut_1.nii.gz"+ " " + "-linear" +" " + "RegMNI152_to_T1/MNI152FSL_to_brainFS_Mrtrix3format.txt"+ " " + "RegMNI152_to_T1/SN/lh_SN_3.nii.gz", shell=True)
    subprocess.call("mrtransform" + " " +TmplateFSL + "/Substantia_Nigra/rh_SN_cluster3_1_ncut.nii.gz"+ " " + "-linear" +" " + "RegMNI152_to_T1/MNI152FSL_to_brainFS_Mrtrix3format.txt"+ " " + "RegMNI152_to_T1/SN/rh_SN_1.nii.gz", shell=True)
    subprocess.call("mrtransform" + " " +TmplateFSL + "/Substantia_Nigra/rh_SN_cluster3_2_ncut.nii.gz"+ " " + "-linear" +" " + "RegMNI152_to_T1/MNI152FSL_to_brainFS_Mrtrix3format.txt"+ " " + "RegMNI152_to_T1/SN/rh_SN_2.nii.gz", shell=True)
    subprocess.call("mrtransform" + " " +TmplateFSL + "/Substantia_Nigra/rh_SN_cluster3_3_ncut.nii.gz"+ " " + "-linear" +" " + "RegMNI152_to_T1/MNI152FSL_to_brainFS_Mrtrix3format.txt"+ " " + "RegMNI152_to_T1/SN/rh_SN_3.nii.gz", shell=True)

# ### LR_3ROIs_groupALL region registration
# subprocess.call("mkdir" + " " + "RegMNI152_to_T1/LR_3ROIs_groupALL", shell=True)
# subprocess.call("mrtransform" + " " +TmplateFSL + "/Substantia_Nigra/Tracts_lr_3ROIs_MPM_thre0.01_groupALL_combine.nii.gz"+ " " + "-linear" +" " + "RegMNI152_to_T1/MNI152FSL_to_brainFS_Mrtrix3format.txt"+ " " + "RegMNI152_to_T1/LR_3ROIs_groupALL/LR_3ROIs_groupALL.nii.gz", shell=True)

## generate SN fiber
def GenSNTracts( root_subject ):
    os.chdir( root_subject )
    subprocess.call("mkdir" + " " + "RegMNI152_to_T1/SN/SN_ACT_seedgmwmi", shell=True)
    subprocess.call("tckedit" + " " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/lh_SN_1.nii.gz"+ " " + "RegMNI152_to_T1/SN/SN_ACT_seedgmwmi/lh_SN_1.tck", shell=True)
    subprocess.call("tckedit" + " " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/lh_SN_2.nii.gz"+ " " + "RegMNI152_to_T1/SN/SN_ACT_seedgmwmi/lh_SN_2.tck", shell=True)
    subprocess.call("tckedit" + " " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/lh_SN_3.nii.gz"+ " " + "RegMNI152_to_T1/SN/SN_ACT_seedgmwmi/lh_SN_3.tck", shell=True)
    subprocess.call("tckedit" + " " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/rh_SN_1.nii.gz"+ " " + "RegMNI152_to_T1/SN/SN_ACT_seedgmwmi/rh_SN_1.tck", shell=True)
    subprocess.call("tckedit" + " " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/rh_SN_2.nii.gz"+ " " + "RegMNI152_to_T1/SN/SN_ACT_seedgmwmi/rh_SN_2.tck", shell=True)
    subprocess.call("tckedit" + " " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/rh_SN_3.nii.gz"+ " " + "RegMNI152_to_T1/SN/SN_ACT_seedgmwmi/rh_SN_3.tck", shell=True)
    subprocess.call("tckedit" + " " + "RegMNI152_to_T1/SN/SN_ACT_seedgmwmi/lh_SN_1.tck"+ " " + "RegMNI152_to_T1/SN/SN_ACT_seedgmwmi/lh_SN_2.tck"+ " " + "RegMNI152_to_T1/SN/SN_ACT_seedgmwmi/lh_SN_3.tck"+ " " + "RegMNI152_to_T1/SN/SN_ACT_seedgmwmi/Left_SN.tck", shell=True)
    subprocess.call("tckedit" + " " + "RegMNI152_to_T1/SN/SN_ACT_seedgmwmi/rh_SN_1.tck"+ " " + "RegMNI152_to_T1/SN/SN_ACT_seedgmwmi/rh_SN_2.tck"+ " " + "RegMNI152_to_T1/SN/SN_ACT_seedgmwmi/rh_SN_3.tck"+ " " + "RegMNI152_to_T1/SN/SN_ACT_seedgmwmi/Right_SN.tck", shell=True)
    subprocess.call("tckedit" + " " + "RegMNI152_to_T1/SN/SN_ACT_seedgmwmi/Left_SN.tck"+ " " + "RegMNI152_to_T1/SN/SN_ACT_seedgmwmi/Right_SN.tck"+ " " + "RegMNI152_to_T1/SN/SN_ACT_seedgmwmi/Whole_SN.tck", shell=True)
    subprocess.call("tckedit" + " " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/lh_SN_1.nii.gz"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/lh_SN_2.nii.gz"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/lh_SN_3.nii.gz"+ " " + "RegMNI152_to_T1/SN/SN_ACT_seedgmwmi/lh_SN_SelfConnect.tck", shell=True)
    subprocess.call("tckedit" + " " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/rh_SN_1.nii.gz"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/rh_SN_2.nii.gz"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/rh_SN_3.nii.gz"+ " " + "RegMNI152_to_T1/SN/SN_ACT_seedgmwmi/rh_SN_SelfConnect.tck", shell=True)


# #
# ##########################################################################################################################################################################
# ####===============================                              Tract-Based Spatial Statistics (TBSS)                         =======================================####
# ##########################################################################################################################################################################
# #
def GenTensorInfo( root_subject ):
    os.chdir( root_subject )
    subprocess.call("mkdir" + " " + "TBSS", shell=True)
    subprocess.call("mkdir" + " " + "TBSS/DTIFIT", shell=True)
    subprocess.call("mkdir" + " " + "TBSS/TBSS_Steps", shell=True)
    ## V1, V2, V3, L1, L2, L3, MD, FA, MO, S0
    subprocess.call("dtifit" + " " +"-k"+ " " + "DTI_processed.nii.gz"+" " + "-o"+ " " + "TBSS/DTIFIT/DTI_processed"+ " " + "-m"+ " " + "ACT/5TT_wmmask.nii.gz"+ " " + "-r"+ " " + "DTI_processed.bvecs" +" " + "-b" +" " + "DTI_processed.bvals", shell=True)
    subprocess.call("dwi2tensor" + " " +"DTI_processed.nii.gz"+ " " + "DTI_processed_tensor.mif"+ " "+ "-fslgrad"+ " " + "DTI_processed.bvecs"+ " " + "DTI_processed.bvals", shell=True)
    ##-adc(MD), -fa, -ad, -rd, -cl, -cp, -cs, -value, -vector
    subprocess.call("tensor2metric" + " " +"DTI_processed_tensor.mif"+ " " + "-fa"+ " " + "TBSS/DTIFIT/DTI_processed_FA.nii.gz"+ " " + "-adc"+ " " + "TBSS/DTIFIT/DTI_processed_ADC.nii.gz"+ " " + "-ad"+ " " + "TBSS/DTIFIT/DTI_processed_AD.nii.gz"+ " " +"-rd"+ " " + "TBSS/DTIFIT/DTI_processed_RD.nii.gz"+ " " +"-cl"+ " " + "TBSS/DTIFIT/DTI_processed_CL.nii.gz"+ " " +"-cp"+ " " + "TBSS/DTIFIT/DTI_processed_CP.nii.gz"+ " " +"-cs"+ " " + "TBSS/DTIFIT/DTI_processed_CS.nii.gz"+ " " +"-value"+ " " + "TBSS/DTIFIT/DTI_processed_VALUE.nii.gz"+ " " +"-vector"+ " " + "TBSS/DTIFIT/DTI_processed_VECTOR.nii.gz"+ " " +"-mask"+ " " + "ACT/5TT_wmmask.nii.gz"+" "+ "-force", shell=True)


# def TBSS( root_subject ):
#     os.chdir( root_subject )
#     subprocess.call("cp" + " " + "TBSS/DTIFIT/DTI_processed_FA.nii.gz"+ " " + "TBSS/TBSS_Steps/", shell=True)
#     os.chdir("TBSS/TBSS_Steps")
#     subprocess.call("tbss_1_preproc" + " " + "DTI_processed_FA.nii.gz", shell=True)
#     subprocess.call("tbss_2_reg" + " " + "-T", shell=True)
#     subprocess.call("tbss_3_postreg" + " " + "-S", shell=True)
#     os.chdir("stats")
#     subprocess.call("tbss_4_prestats" + " " + "0.2", shell=True)
#     os.chdir("..")
#     os.chdir("..")
#     os.chdir("..")



# # # ------------------------- Sample values of an associated image along tracks.(MRtrix) ------------------------- #
# subprocess.call("mkdir" + " " + "TBSS/TBSS_Diffusion_MNI152", shell=True)
#
# subprocess.call("tcksample" + " " +"Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M_warpMNI152FSL.tck"+ " " + "TBSS/TBSS_Steps/stats/all_FA.nii.gz"+" " + "TBSS/TBSS_Diffusion_MNI152/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M_warpMNI152FSLBSS_FA.txt" + " " +"-force", shell=True)
# subprocess.call("tcksample" + " " +"Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M_warpMNI152FSL.tck"+ " " + "TBSS/TBSS_Steps/stats/all_FA.nii.gz"+" " + "TBSS/TBSS_Diffusion_MNI152/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M_warpMNI152FSLBSS_FA_mean.txt"+ " " + "-stat_tck"+ " " + "mean" + " " +"-force", shell=True)
# subprocess.call("tcksample" + " " +"Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M.tck"+ " " + "TBSS/DTIFIT/DTI_processed_FA.nii.gz"+" " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M_FA.txt" + " " +"-force", shell=True)
# subprocess.call("tcksample" + " " +"Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M.tck"+ " " + "TBSS/DTIFIT/DTI_processed_FA.nii.gz"+" " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M_FA_mean.txt"+ " " + "-stat_tck"+ " " + "mean" + " " +"-force", shell=True)
#
# # # # # ------------------------- Using non-FA Images in TBSS.(FSL) ----------------------------- #
# Tenser_statistics = ["L1","L2","L3","MO","S0","ADC","AD","RD","CS","CP","CL","VALUE","VECTOR"]
# for i in range(len(Tenser_statistics)):
#     subprocess.call("mkdir" + " " + "TBSS/TBSS_Steps/" + Tenser_statistics[i], shell=True)
#     subprocess.call("cp" + " " + "TBSS/DTIFIT/DTI_processed_" + Tenser_statistics[i] + ".nii.gz"+ " " + "TBSS/TBSS_Steps/" + Tenser_statistics[i] + "/DTI_processed_FA.nii.gz", shell=True)
#     os.chdir("TBSS/TBSS_Steps")
#     subprocess.call("tbss_non_FA" + " " + Tenser_statistics[i], shell=True)
#     # subprocess.call("tcksample" + " " +"../../Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M_warpMNI152FSL.tck"+ " " + "../../TBSS/TBSS_Steps/stats/all_" + Tenser_statistics[i] + ".nii.gz"+" " + "../../TBSS/TBSS_Diffusion_MNI152/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M_warpMNI152FSLBSS_" + Tenser_statistics[i] + ".txt" + " " +"-force", shell=True)
#     # subprocess.call("tcksample" + " " +"../../Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M_warpMNI152FSL.tck"+ " " + "../../TBSS/TBSS_Steps/stats/all_" + Tenser_statistics[i] + ".nii.gz"+" " + "../../TBSS/TBSS_Diffusion_MNI152/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M_warpMNI152FSLBSS_" + Tenser_statistics[i] + "_mean.txt"+ " " + "-stat_tck"+ " " + "mean" + " " +"-force", shell=True)
#     subprocess.call("tcksample" + " " +"../../Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M.tck"+ " " + "../../TBSS/DTIFIT/DTI_processed_" + Tenser_statistics[i] + ".nii.gz"+" " + "../../Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M_" + Tenser_statistics[i] + ".txt" + " " +"-force", shell=True)
#     subprocess.call("tcksample" + " " +"../../Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M.tck"+ " " + "../../TBSS/DTIFIT/DTI_processed_" + Tenser_statistics[i] + ".nii.gz"+" " + "../../Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M_sift0.1M_" + Tenser_statistics[i] + "_mean.txt"+ " " + "-stat_tck"+ " " + "mean" + " " +"-force", shell=True)
#     os.chdir("..")
#     os.chdir("..")


# # ##########################################################################################################################################################################
# # ####===============================                   Create Brain Volume, Surface, and Connectome for Rendering               =======================================####
# # ##########################################################################################################################################################################
# # #
#
# subprocess.call("mkdir" + " " + "Volume", shell=True)
# subprocess.call("mkdir" + " " + "Volume/CorticalLabels", shell=True)
# subprocess.call("mkdir" + " " + "Volume/CorticalLabels_Volume", shell=True)
# #
# # # ################################################################################
# # # ##                       ACT Tractography and Connecome                       ##
# # # ################################################################################

## ----------- Generate cortical labels connectome and tracts ( fs_default )------------####
## Connectome Generation:(Here shows in subject space)(MRtrix3)

def GenRegionConnectome( root_subject ):
    os.chdir( root_subject )
    subprocess.call("mkdir" + " " + "Connectome", shell=True)
    subprocess.call("tcksift2" + " " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck"+ " " + "DTI_processed_5TTwmmask_fod.mif"+" " + "Connectome/DTI_processed_ACT_5TTwmmask_seedgmwmi_weights.csv"+ " " + "-act"+ " " + "ACT/t1_orig_5TT_nocrop.mif", shell=True)
    subprocess.call("labelconvert" + " " +"T1_source_bert/mri/aparc+aseg.mgz"+ " " + FreeSurferloc + "/FreeSurferColorLUT.txt" + " " + MRtrix3loc + "/share/mrtrix3/labelconvert/fs_default.txt"+ " " + "Connectome/aparc+aseg_Desikan_Killany_nodes.nii", shell=True)
    subprocess.call("tck2connectome" + " " +"Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck"+ " " + "Connectome/aparc+aseg_Desikan_Killany_nodes.nii"+" " + "Connectome/connectome_ACT.csv"+ " " + "-out_assignments" + " " + "Connectome/assignments_ACT.txt", shell=True)
    subprocess.call("mkdir" + " " + "Connectome/ACT_Region2Region", shell=True)
    n = 84
    for num in range( 1, n+1 ):
        subprocess.check_call("connectome2tck" + " " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck" + " " + "Connectome/assignments_ACT.txt" + " " + "Connectome/ACT_Region2Region/edge_tracks_ -nodes" + " " + str(num) + " " + "-files" + " " + "per_edge" + " " + "-keep_self " + "-force", shell=True)

    # merge all the fiber in one region together
    n = 84
    subprocess.call("mkdir" + " " + "Connectome/ACT_Region", shell=True)
    for i in range( 1, n+1 ):
        subprocess.call("tckedit" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i)  + "-1.tck"+ " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i)  + "-2.tck"  + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-3.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i)  + "-4.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-5.tck"+ " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-6.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-7.tck"+ " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-8.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-9.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-10.tck"  + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-11.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-12.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-13.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-14.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-15.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-16.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-17.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-18.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-19.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-20.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-21.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-22.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-23.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-24.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-25.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-26.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-27.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-28.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-29.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-30.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-31.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-32.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-33.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-34.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-35.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-36.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-37.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-38.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-39.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-40.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-41.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-42.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-43.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-44.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-45.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-46.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-47.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-48.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-49.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-50.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-51.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-52.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-53.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-54.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-55.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-56.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-57.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-58.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-59.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-60.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-61.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-62.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-63.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-64.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-65.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-66.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-67.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-68.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-69.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-70.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-71.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-72.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-73.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-74.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-75.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-76.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-77.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-78.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-79.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-80.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-81.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-82.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-83.tck" + " " + "Connectome/ACT_Region2Region/edge_tracks_" + str(i) + "-84.tck"+ " " +  "Connectome/ACT_Region/edge_tracks_" + str(i) + ".tck"+ " " + "-force", shell=True)


# ### ----------- Generate lobes connectome and tracts (fs2lobes_cingsep_labels)------------####
# #Connectome Generation:(Here shows in subject space)(MRtrix3)
def GenLobeConnectome( root_subject ):
    os.chdir( root_subject )
    subprocess.call("labelconvert" + " " +"T1_source_bert/mri/aparc+aseg.mgz"+ " " + FreeSurferloc + "/FreeSurferColorLUT.txt"+" " +  MRtrix3loc + "/share/mrtrix3/labelconvert/fs2lobes_cingsep_convert.txt"+ " " + "Connectome/aparc+aseg_Desikan_Killany_fs2lobes_cingsep_nodes.nii", shell=True)
    subprocess.call("tck2connectome" + " " +"Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck"+ " " + "Connectome/aparc+aseg_Desikan_Killany_fs2lobes_cingsep_nodes.nii"+" " + "Connectome/connectome_ACT_fs2lobes_cingsep.csv"+ " " + "-out_assignments" + " " + "Connectome/assignments_ACT_fs2lobes_cingsep.txt", shell=True)
    subprocess.call("mkdir" + " " + "Connectome/ACT_Region2Region_fs2lobes_cingsep", shell=True)
    n = 14
    for num in range( 1, n+1 ):
        subprocess.check_call("connectome2tck" + " " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck" + " " + "Connectome/assignments_ACT_fs2lobes_cingsep.txt" + " " + "Connectome/ACT_Region2Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_ -nodes" + " " + str(num) + " " + "-files" + " " + "per_edge" + " " + "-keep_self " + "-force", shell=True)

    subprocess.call("mkdir" + " " + "Connectome/ACT_Region_fs2lobes_cingsep", shell=True)
    n = 14
    for i in range( 1, n+1 ):
        subprocess.call("tckedit" + " " + "Connectome/ACT_Region2Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_" + str(i)  + "-1.tck"+ " " + "Connectome/ACT_Region2Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_" + str(i)  + "-2.tck"  + " " + "Connectome/ACT_Region2Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_" + str(i) + "-3.tck" + " " + "Connectome/ACT_Region2Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_" + str(i)  + "-4.tck" + " " + "Connectome/ACT_Region2Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_" + str(i) + "-5.tck"+ " " + "Connectome/ACT_Region2Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_" + str(i) + "-6.tck" + " " + "Connectome/ACT_Region2Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_" + str(i) + "-7.tck"+ " " + "Connectome/ACT_Region2Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_" + str(i) + "-8.tck" + " " + "Connectome/ACT_Region2Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_" + str(i) + "-9.tck" + " " + "Connectome/ACT_Region2Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_" + str(i) + "-10.tck"  + " " + "Connectome/ACT_Region2Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_" + str(i) + "-11.tck" + " " + "Connectome/ACT_Region2Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_" + str(i) + "-12.tck" + " " + "Connectome/ACT_Region2Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_" + str(i) + "-13.tck" + " " + "Connectome/ACT_Region2Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_" + str(i) + "-14.tck" + " " +  "Connectome/ACT_Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_" + str(i) + ".tck"+ " " + "-force", shell=True)



# # #### ----------- calculate node coordinates ------------####
# # # # nodes coordinates
# def CalNodeCoord( root_subject ):
#     os.chdir( root_subject )
#     subprocess.call("mkdir" + " " + "Connectome/ACT_Region_fs2lobes_cingsep_nodes_positions", shell=True)
#     subprocess.call("warpinit" + " " + "Connectome/aparc+aseg_Desikan_Killany_fs2lobes_cingsep_nodes.nii" + " " + "Connectome/aparc+aseg_Desikan_Killany_fs2lobes_cingsep_nodes_positions.mif", shell=True)
#     subprocess.call("mrcalc Connectome/aparc+aseg_Desikan_Killany_fs2lobes_cingsep_nodes.nii 5 -eq Connectome/ACT_Region_fs2lobes_cingsep_nodes_positions/node_5.nii", shell=True)
#     subprocess.call("mrstats Connectome/aparc+aseg_Desikan_Killany_fs2lobes_cingsep_nodes_positions.mif -mask Connectome/ACT_Region_fs2lobes_cingsep_nodes_positions/node_5.nii -output mean", shell=True)

# # #
# # #################################################################################################################################################################
# # ##                         PD related Region: Putamen/Caudate/Thalamus/Hippocampus/Pallidum/Subcortical  -- ACT Tractography()                                 ##
# # #################################################################################################################################################################

def GenRegionFibers( root_subject ):
    os.chdir( root_subject )
    PD_Region_ACT = 'PD_Regions_ACT_seedgmwmi'

    subprocess.call("mkdir" + " " + PD_Region_ACT, shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/Cingulate", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/CorpusCallosum", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/Subcortical", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/Putamen", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/Caudate", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/Thalamus", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/Hippocampus", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/Pallidum", shell=True)
    # subprocess.call("mkdir" + " " + PD_Region_ACT + "/SubstantiaNigra", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/Amygdala", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/Accumbens", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/bankssts", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/caudalanteriorcingulate", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/caudalmiddlefrontal", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/cuneus", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/entorhinal", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/fusiform", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/inferiorparietal", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/inferiortemporal", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/isthmuscingulate", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/lateraloccipital", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/lateralorbitofrontal", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/lingual", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/medialorbitofrontal", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/middletemporal", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/parahippocampal", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/paracentral", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/parsopercularis", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/parsorbitalis", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/parstriangularis", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/pericalcarine", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/postcentral", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/posteriorcingulate", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/precentral", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/precuneus", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/rostralanteriorcingulate", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/rostralmiddlefrontal", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/superiorfrontal", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/superiorparietal", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/superiortemporal", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/supramarginal", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/frontalpole", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/temporalpole", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/transversetemporal", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/insula", shell=True)
    subprocess.call("mkdir" + " " + PD_Region_ACT + "/Cerebellum", shell=True)

    for filename in os.listdir(root_subject+'/'+ PD_Region_ACT ):
        if filename == "Subcortical":
            subprocess.call("cp" + " " + "Connectome/ACT_Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_7.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
            subprocess.call("cp" + " " + "Connectome/ACT_Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_8.tck"+ " " + PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
            subprocess.call("cp" + " " + "Connectome/ACT_Region2Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_7-7.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
            subprocess.call("cp" + " " + "Connectome/ACT_Region2Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_8-8.tck"+ " " + PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" +".tck", shell=True)
        else:
            if filename == "Thalamus":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_36.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_43.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_36-36.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_43-43.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "Caudate":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_37.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_44.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_37-37.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_44-44.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "Putamen":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_38.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_45.tck"+ " "+  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_38-38.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_45-45.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "Pallidum":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_39.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_46.tck"+ " "+  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_39-39.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_46-46.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "Hippocampus":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_40.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_47.tck"+ " "+  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_40-40.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_47-47.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "Amygdala":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_41.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_48.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_41-41.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_48-48.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "Accumbens":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_42.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_49.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_42-42.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_49-49.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "bankssts":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_1.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_50.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_1-1.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_50-50.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "caudalanteriorcingulate":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_2.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_51.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_2-2.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_51-51.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "caudalmiddlefrontal":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_3.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_52.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_3-3.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_52-52.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "cuneus":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_4.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_53.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_4-4.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_53-53.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "entorhinal":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_5.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_54.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_5-5.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_54-54.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "fusiform":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_6.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_55.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_6-6.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_55-55.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "inferiorparietal":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_7.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_56.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_7-7.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_56-56.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "inferiortemporal":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_8.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_57.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_8-8.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_57-57.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "isthmuscingulate":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_9.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_58.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_9-9.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_58-58.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "lateraloccipital":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_10.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_59.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_10-10.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_59-59.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "lateralorbitofrontal":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_11.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_60.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_11-11.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_60-60.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "lingual":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_12.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_61.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_12-12.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_61-61.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "medialorbitofrontal":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_13.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_62.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_13-13.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_62-62.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "middletemporal":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_14.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_63.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_14-14.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_63-63.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "parahippocampal":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_15.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_64.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_15-15.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_64-64.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "paracentral":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_16.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_65.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_16-16.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_65-65.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "parsopercularis":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_17.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_66.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_17-17.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_66-66.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "parsorbitalis":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_18.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_67.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_18-18.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_67-67.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "parstriangularis":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_19.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_68.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_19-19.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_68-68.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "pericalcarine":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_20.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_69.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_20-20.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_69-69.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "postcentral":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_21.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_70.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_21-21.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_70-70.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "posteriorcingulate":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_22.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_71.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_22-22.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_71-71.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "precentral":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_23.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_72.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_23-23.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_72-72.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "precuneus":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_24.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_73.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_24-24.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_73-73.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "rostralanteriorcingulate":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_25.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_74.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_25-25.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_74-74.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "rostralmiddlefrontal":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_26.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_75.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_26-26.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_75-75.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "superiorfrontal":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_27.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_76.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_27-27.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_76-76.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "superiorparietal":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_28.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_77.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_28-28.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_77-77.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "superiortemporal":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_29.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_78.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_29-29.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_78-78.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "supramarginal":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_30.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_79.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_30-30.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_79-79.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "frontalpole":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_31.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_80.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_31-31.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_80-80.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "temporalpole":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_32.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_81.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_32-32.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_81-81.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "transversetemporal":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_33.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_82.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_33-33.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_82-82.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "insula":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_34.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_83.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_34-34.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_83-83.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            elif filename == "Cerebellum":
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_35.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region/edge_tracks_84.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_35-35.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
                subprocess.call("cp" + " " + "Connectome/ACT_Region2Region/edge_tracks_84-84.tck"+ " " +  PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)
            # elif filename == "SubstantiaNigra":
            #          subprocess.call("tckedit" + " " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/lh_SN_1.nii.gz"+ " " + PD_Region_ACT+'/' + filename + "/lh_SN_1.tck", shell=True)
            #          subprocess.call("tckedit" + " " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/lh_SN_2.nii.gz"+ " " + PD_Region_ACT+'/' + filename + "/lh_SN_2.tck", shell=True)
            #          subprocess.call("tckedit" + " " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/lh_SN_3.nii.gz"+ " " + PD_Region_ACT+'/' + filename + "/lh_SN_3.tck", shell=True)
            #          subprocess.call("tckedit" + " " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/rh_SN_1.nii.gz"+ " " + PD_Region_ACT+'/' + filename + "/rh_SN_1.tck", shell=True)
            #          subprocess.call("tckedit" + " " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/rh_SN_2.nii.gz"+ " " + PD_Region_ACT+'/' + filename + "/rh_SN_2.tck", shell=True)
            #          subprocess.call("tckedit" + " " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/rh_SN_3.nii.gz"+ " " + PD_Region_ACT+'/' + filename + "/rh_SN_3.tck", shell=True)

            #          subprocess.call("tckedit" + " " + PD_Region_ACT+'/' + filename + "/lh_SN_1.tck"+ " " + PD_Region_ACT+'/' + filename + "/lh_SN_2.tck"+ " " + PD_Region_ACT+'/' + filename + "/lh_SN_3.tck"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck", shell=True)
            #          subprocess.call("tckedit" + " " + PD_Region_ACT+'/' + filename + "/rh_SN_1.tck"+ " " + PD_Region_ACT+'/' + filename + "/rh_SN_2.tck"+ " " + PD_Region_ACT+'/' + filename + "/rh_SN_3.tck"+ " " + PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck", shell=True)
            #          subprocess.call("tckedit" + " " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/lh_SN_1.nii.gz"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/lh_SN_2.nii.gz"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/lh_SN_3.nii.gz"+ " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck", shell=True)
            #          subprocess.call("tckedit" + " " + "Output_ACT/DTI_processed_ACT_5TTwmmask_seedgmwmi_0.5M.tck"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/rh_SN_1.nii.gz"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/rh_SN_2.nii.gz"+ " " + "-include" + " " + "RegMNI152_to_T1/SN/rh_SN_3.nii.gz"+ " " + PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck", shell=True)

        subprocess.call("tckedit" + " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + ".tck"+ " " + PD_Region_ACT+'/' + filename + "/Right_" + filename + ".tck"+ " " + PD_Region_ACT+'/'+filename+"/Whole_"+filename+".tck", shell=True)
        subprocess.call("tckedit" + " " + PD_Region_ACT+'/' + filename + "/Left_" + filename + "_SelfConnect" + ".tck"+ " " + PD_Region_ACT+'/' + filename + "/Right_" + filename + "_SelfConnect" + ".tck"+ " " + PD_Region_ACT+'/'+filename+"/Whole_"+filename + "_SelfConnect" + ".tck", shell=True)

    for filename in os.listdir(root_subject+'/'+ PD_Region_ACT ):
        if filename == "Cingulate":
            subprocess.call("tckedit" + " " + "Connectome/ACT_Region/edge_tracks_2.tck"+ " " + "Connectome/ACT_Region/edge_tracks_9.tck"+ " " + "Connectome/ACT_Region/edge_tracks_22.tck"+ " " + "Connectome/ACT_Region/edge_tracks_25.tck"+ " " + "Connectome/ACT_Region/edge_tracks_51.tck"+ " " + "Connectome/ACT_Region/edge_tracks_58.tck"+ " " + "Connectome/ACT_Region/edge_tracks_71.tck"+ " " + "Connectome/ACT_Region/edge_tracks_74.tck" + " " + PD_Region_ACT + "/Cingulate" + "/"+ "Cingulate.tck", shell=True)
        elif filename == "CorpusCallosum":
            subprocess.call("tckedit" + " " + "Connectome/ACT_Region2Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_1-14.tck"+ " " + "Connectome/ACT_Region2Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_2-13.tck"+ " " + "Connectome/ACT_Region2Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_3-12.tck"+ " " + "Connectome/ACT_Region2Region_fs2lobes_cingsep/edge_tracks_fs2lobes_cingsep_4-11.tck"+ " "+ PD_Region_ACT + "/CorpusCallosum"+ "/"+ "CorpusCallosum.tck", shell=True)
        else: pass

def Tck2VTK( root_subject ):
    os.chdir( root_subject )
    PD_Region_ACT = 'PD_Regions_ACT_seedgmwmi'
    for filename in os.listdir(root_subject+'/'+ PD_Region_ACT ):
        if filename == "Cingulate":
            subprocess.call("tckconvert" + " " + PD_Region_ACT + "/Cingulate" + "/"+ "Cingulate.tck"+ " " +PD_Region_ACT + "/Cingulate" + "/"+ "Cingulate.vtk"+ " " + "-force", shell=True)
        elif filename == "CorpusCallosum":
            subprocess.call("tckconvert" + " " + PD_Region_ACT + "/CorpusCallosum"+ "/"+ "CorpusCallosum.tck"+ " " +PD_Region_ACT + "/CorpusCallosum"+ "/"+ "CorpusCallosum.vtk", shell=True)
        else:
            for j in range(len(Tract_Locat)):
                subprocess.call("tckconvert" + " " +PD_Region_ACT+'/' + filename + "/"+ Tract_Locat[j] +"_" + filename + ".tck"+ " " +PD_Region_ACT+'/' + filename + "/"+ Tract_Locat[j] +"_" + filename + ".vtk", shell=True)
                subprocess.call("tckconvert" + " " +PD_Region_ACT+'/' + filename + "/"+ Tract_Locat[j] +"_" + filename + "_SelfConnect" + ".tck"+ " " +PD_Region_ACT+'/' + filename + "/"+ Tract_Locat[j] +"_" + filename + "_SelfConnect" + ".vtk", shell=True)

def GenTractsStatistic( root_subject ):
    os.chdir( root_subject )
    PD_Region_ACT = 'PD_Regions_ACT_seedgmwmi'
    for filename in os.listdir(root_subject+'/'+ PD_Region_ACT ):
        if os.path.isdir( root_subject+'/'+ PD_Region_ACT + '/' + filename ):
            if (filename == "Cingulate")or(filename == "CorpusCallosum"):
                for i in range(len(Tenser_statistics)):
                    subprocess.call("tcksample" + " " + PD_Region_ACT+'/' + filename + "/"+ filename + ".tck"+ " " + "TBSS/DTIFIT/DTI_processed_" + Tenser_statistics[i] + ".nii.gz"+" " + PD_Region_ACT+'/' + filename + "/"+ filename + "_" + Tenser_statistics[i] + ".txt", shell=True)
                    subprocess.call("tcksample" + " " +PD_Region_ACT+'/' + filename + "/"+ filename + ".tck"+ " " + "TBSS/DTIFIT/DTI_processed_" + Tenser_statistics[i] + ".nii.gz"+" " + PD_Region_ACT+'/' + filename + "/"+ filename + "_" + Tenser_statistics[i] + "_mean.txt"+ " " + "-stat_tck"+ " " + "mean", shell=True)
            else:
                for i in range(len(Tenser_statistics)):
                    for j in range(len(Tract_Locat)):
                        subprocess.call("tcksample" + " " +PD_Region_ACT+'/' + filename + "/"+ Tract_Locat[j] +"_" + filename + ".tck"+ " " + "TBSS/DTIFIT/DTI_processed_" + Tenser_statistics[i] + ".nii.gz"+" " + PD_Region_ACT+'/' + filename + "/"+ Tract_Locat[j] +"_" + filename + "_" + Tenser_statistics[i] + ".txt", shell=True)
                        subprocess.call("tcksample" + " " +PD_Region_ACT+'/' + filename + "/"+ Tract_Locat[j] +"_" + filename + ".tck"+ " " + "TBSS/DTIFIT/DTI_processed_" + Tenser_statistics[i] + ".nii.gz"+" " + PD_Region_ACT+'/' + filename + "/"+ Tract_Locat[j] +"_" + filename + "_" + Tenser_statistics[i] + "_mean.txt"+ " " + "-stat_tck"+ " " + "mean", shell=True)
                        subprocess.call("tcksample" + " " +PD_Region_ACT+'/' + filename + "/"+ Tract_Locat[j] +"_" + filename + "_SelfConnect" +".tck"+ " " + "TBSS/DTIFIT/DTI_processed_" + Tenser_statistics[i] + ".nii.gz"+" " + PD_Region_ACT+'/' + filename + "/"+ Tract_Locat[j] +"_" + filename + "_SelfConnect" + "_" + Tenser_statistics[i] + ".txt", shell=True)
                        subprocess.call("tcksample" + " " +PD_Region_ACT+'/' + filename + "/"+ Tract_Locat[j] +"_" + filename + "_SelfConnect" +".tck"+ " " + "TBSS/DTIFIT/DTI_processed_" + Tenser_statistics[i] + ".nii.gz"+" " + PD_Region_ACT+'/' + filename + "/"+ Tract_Locat[j] +"_" + filename + "_SelfConnect" + "_" + Tenser_statistics[i] + "_mean.txt"+ " " + "-stat_tck"+ " " + "mean", shell=True)


############################################################
# PD_Region_ACT = 'PD_Regions_ACT_seedgmwmi'
#
# Tenser_statistics_FSL = ["FA","L1","L2","L3","MO","S0","ADC","AD","RD","CS","CP","CL","VALUE","VECTOR"]
# Tenser_statistics_MRtrix = ["ADC", "FA", "AD", "RD","CL","CP","CS", "VALUE","VECTOR" ]
# Tract_Locat = ["Whole"]
#
# for filename in os.listdir(root+'/'+ PD_Region_ACT ):
#     if os.path.isdir( root+'/'+ PD_Region_ACT + '/' + filename ):
#         # generate statistics
#         if (filename == "Cingulate")or(filename == "CorpusCallosum"):
#             for i in range(len(Tenser_statistics_FSL)):
#                 subprocess.call("tcksample" + " " + PD_Region_ACT+'/' + filename + "/"+ filename + ".tck"+ " " + "TBSS/DTIFIT/DTI_processed_" + Tenser_statistics_FSL[i] + ".nii.gz"+" " + PD_Region_ACT+'/' + filename + "/"+ filename + "_" + Tenser_statistics_FSL[i] + ".txt", shell=True)
#         else:
#             for i in range(len(Tenser_statistics_FSL)):
#                 for j in range(len(Tract_Locat)):
#                     subprocess.call("tcksample" + " " +PD_Region_ACT+'/' + filename + "/"+ Tract_Locat[j] +"_" + filename + ".tck"+ " " + "TBSS/DTIFIT/DTI_processed_" + Tenser_statistics_FSL[i] + ".nii.gz"+" " + PD_Region_ACT+'/' + filename + "/"+ Tract_Locat[j] +"_" + filename + "_" + Tenser_statistics_FSL[i] + ".txt", shell=True)
#                     subprocess.call("tcksample" + " " +PD_Region_ACT+'/' + filename + "/"+ Tract_Locat[j] +"_" + filename + "_SelfConnect" +".tck"+ " " + "TBSS/DTIFIT/DTI_processed_" + Tenser_statistics_FSL[i] + ".nii.gz"+" " + PD_Region_ACT+'/' + filename + "/"+ Tract_Locat[j] +"_" + filename + "_SelfConnect" + "_" + Tenser_statistics_FSL[i] + ".txt", shell=True)



# # #------------------------- Cortial Labels volume Generation ------------------------#
# #
# subprocess.call("SUBJECTS_DIR="+ root +"; mri_annotation2label --subject T1_source_bert/ --hemi lh --outdir" + " " + root + "/Volume/CorticalLabels", shell=True)
# subprocess.call("SUBJECTS_DIR="+ root +"; mri_annotation2label --subject T1_source_bert/ --hemi rh --outdir" + " " + root + "/Volume/CorticalLabels", shell=True)
#
# # # transform those labels into the space that you need(here is the native space)
# subprocess.call("SUBJECTS_DIR="+ root +"; tkregister2 --mov T1_source_bert/mri/rawavg.mgz --noedit --s T1_source_bert/ --regheader --reg"+ " " + root + "/Volume/CorticalLabels_register.dat", shell=True)
#
# # #creates nii.gz volume from a label or set of labels
# CorticalLabels_path = root + '/Volume/CorticalLabels'
# for filename in os.listdir(CorticalLabels_path):
#     head=filename.split(".")
#     if ( head[0] == 'lh'):
#         subprocess.call("SUBJECTS_DIR="+ root +"; mri_label2vol --label" + " " + root + "/Volume/CorticalLabels/"+ filename  + " " + "--temp  T1_source_bert/mri/rawavg.mgz --subject T1_source_bert/ --hemi lh --o"+ " " + root + "/Volume/CorticalLabels_Volume/"+ filename + ".nii.gz "+ " " + "--proj frac 0 1 .1 --fillthresh .3 --reg"+ " " + root + "/Volume/CorticalLabels_register.dat", shell=True)
#     if (head[0] == 'rh'):
#         subprocess.call("SUBJECTS_DIR="+ root +"; mri_label2vol --label" + " " + root + "/Volume/CorticalLabels/"+ filename  + " " + "--temp  T1_source_bert/mri/rawavg.mgz --subject T1_source_bert/ --hemi rh --o"+ " " + root + "/Volume/CorticalLabels_Volume/"+ filename + ".nii.gz "+ " " + "--proj frac 0 1 .1 --fillthresh .3 --reg"+ " " + root + "/Volume/CorticalLabels_register.dat", shell=True)

# # #------------------- White matter surface Creation(FreeSurfer)---------------------#
#
def GenSurface( root_subject ):
    os.chdir( root_subject )
    subprocess.call("mkdir" + " " + "Surface", shell=True)
    subprocess.call("cp" + " " + "T1_source_bert/surf/rh.pial"+ " " + "Surface/T1_source_BrainSurf_rh.pial", shell=True)
    subprocess.call("cp" + " " + "T1_source_bert/surf/lh.pial"+ " " + "Surface/T1_source_BrainSurf_lh.pial", shell=True)
    subprocess.call("mris_convert" + " " + "Surface/T1_source_BrainSurf_lh.pial"+ " " + "Surface/T1_source_BrainSurf_lh.stl", shell=True)
    subprocess.call("mris_convert" + " " + "Surface/T1_source_BrainSurf_rh.pial"+ " " + "Surface/T1_source_BrainSurf_rh.stl", shell=True)
# # then Manually add lh.stl and rh.stl together  wholebrain.stl
#
# ################################################################################################################################################################
# # removefile(root, "DTI_Processing" )




##
def FiberGeneration( root_subject ):
    SourceDataPreprocess( root_subject )
    RegFS2DTI( root_subject )
    ACTPreprocess( root_subject )
    FODestimate( root_subject )
    GenTracts_ACTseedGMWMI( root_subject )
    RegT12MNI152( root_subject )
    GenTensorInfo( root_subject )
    GenRegionConnectome( root_subject )
    GenLobeConnectome( root_subject )
    GenRegionFibers( root_subject )
    Tck2VTK( root_subject )
    GenTractsStatistic( root_subject )
    GenSurface( root_subject )


FiberGeneration(datadir)