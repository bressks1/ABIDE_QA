# ABIDE_QA
QA pipeline for the ABIDE Dataset 

What are our thresholds for excluding data? 
We exclude if...
- FD (median value for all brain volumes) > 0.5mm
- Joint SpikesCount (# of brain volumes where FD > 1mm or DVARS > 5 percent) is greater than 20% of total scan time
- IQR <70
- Poor quality on visual inspection of normalization/brain extraction (cat12) or coregistration (conprep)
- Processing errors

To run this processing pipeline you will need to download the following XNAT assessors: 
- Process label: connprep-asdr-dv_v2, Assessors: FD.txt and DVARS.txt
- Process lavel: cat12_ss2p0_v2, Assessors: PDF

[1] Extract FD and DVARS values, calculate JointSpikes - use script FD_DVARS_extract_values_loop.py 
[2] Extract IQR and GRADE - use script cat12_extract_values_loop.py 
[3] Merge outputs of Steps 1 & 2, and apply tresholds to exclude subjects based on the criteria stated above - merge_and_apply_tresholds.py
[3] Randomly select subjects for manual QA - use script QA_selection.R 
[4] Perform manual QA, open cat12 PDFs in browser - use script open_cat12_PDFs.py to open PDFs in browser so you don't have to click through subfolders 

   
  
