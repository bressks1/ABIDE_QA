# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 14:40:59 2023

@author: bressks1
"""
# Created by Alisa Zoltowski on May 20, 2022
# Updated on August 22, 2022
# Modified by K Bress on July 5, 2023 
# original script: P:\Zoltowski\MRI_Analyses\AutismRestingState\QA\Scripts\final_mri_exclusion.r

## This script merges QA inclusion/exclusion data from 2 processing steps:
# 1: Conprep motion metric summary (FD, DVARs, jointspikes)
# 2: CAT12 IQR and IQR grade

#In prior versions of this script a 3rd step (manual visual inspection) was included (cat12 structural QA, connprep coregistration QA, motion tracking file)
#This was replaced by automated extracted of the IQR value and grade

#Thresholds are applied to identify subjects who meet QA inclusion/exclusion criteria based on these processing metrics 
#

#imports
#IMPORTS 
import pandas as pd
import os
import io
import os
import glob
import csv
import numpy
from datetime import datetime

#define FD, DVARS file 
motion_summ = pd.read_csv('P:\JMQ_Cascio\MRI_analyses\ABIDE_RS\Motion\motion_summary_062323.csv') 
#this file has 16 cols, 1039 rows (including column labels)
#col 1 (index 0) is the MR.ID 

cat12_summ = pd.read_csv('P:\JMQ_Cascio\MRI_analyses\ABIDE_RS\cat12\cat12_summary_070323.csv')
#this file has 3 cols, 991 rows (including column labels)
#col 1 (index 0) is the MR.ID 

#merge the two dataframes based on common values in MR.ID column
qa_data = pd.merge(motion_summ, cat12_summ, on='MR.ID')  #this keeps only rows where there are common MR.IDs from both df
#qa_data = pd.merge(cat12_summ, motion_summ, on='MR.ID', how='left')  #this keeps all the rows from the motion df and adds values where MR.ID matches
print(qa_data)
#check that qa_data contains 1038 rows, 18 columns

qa_data.to_csv('P:/JMQ_Cascio/MRI_analyses/ABIDE_RS/all_QA_values.csv')  #write to csv 


#Why are there 1038 MR.ID in the motion_summary.csv, but 989 MR.ID in the cat12_summary.csv?
motion_id = motion_summ.loc[:, 'MR.ID'] #1038 
cat12_id = cat12_summ.loc[:, 'MR.ID'] #989 

list1 = motion_summ["MR.ID"].values.tolist()
print(len(list1))  #prints the number of MR.IDs in the motion summary csv  #1038
print(len(set(list1))) #prints the number of unique MR.IDs (nonduplicates) in the motion summary csv #989
#there are duplicate MR.ID in the motion_summary.csv file 

list2 = cat12_summ["MR.ID"].values.tolist()
print(len(list2))

#APPLY TRESHOLDS 

#Add columns to all_qa_values.csv: 
#This script will write a 1 (yes) or 0 (no) for every row of these columns
    #Included: whether or not subj is included based on QA tresholds
    #excluded_medMotion: subject exluded because median motion values were above threshold
    #excluded_outliers: subject excluded because jointSpikes percent was above threshold
    #exclude_IQR_value: subject excluded because IQR value was below threshold
    #exclude_IRQ_grade: subject excluded because IQR grade was below threshold
#In prior versions of this script 3 other columns were added: Exclude_normalize, ProcessingErrors, and Exclude_Coreg
#These columns are not created here because manual visual inspection of cat12 normalizaiton and conprep coreg was not performed

#add columns
qa_data['Included'] = ''
qa_data['excluded_medMotion'] = ''
qa_data['excluded_outliers'] = ''
qa_data['excluded_IQR_value'] = ''

#EXCLUSION CRITERIA
#exclude for med motion if...FD for all frames/volumes >0.5mm
#exclude for outliers if...JointSpikesCount percent > ?? (% frames/volumes FD>1mm or DVARS>5% is over 20% of scan time)
#exclude for IQR value if...IQR<70
#exclude for IQR grade if...?

#For every row in apply_thresholds
#if:   #fdMedian >0.5....then write a 1 in 'excluded_medMotion'
       #jointSpikeCount_Con_percent>=0.2....then write a 1 in 'excluded_outliers'
       #IQR < 70....then write a 1 in 'excluded_IQR_value'
       
#if:   #There is a 1 in 'excluded_medMotion', 'excluded_outliers', or 'excluded_IQR_value'...then write a 0 in 'Included'

#Get rid of % sign in IQR column and convert from string to integer
apply_thresholds = qa_data
apply_thresholds['IQR'] = list(map(lambda x: x[:-1], apply_thresholds['IQR'].values)) #get rid of percent
apply_thresholds['IQR'] = [float(x) for x in apply_thresholds['IQR'].values] #convert to float


for index, row in apply_thresholds.iterrows():
    if apply_thresholds.at[index, 'fdMedian'] > 0.5 :        #if the subject has fdMedian > 0.5, write 1 in the 'excluded_medMotion' column
        apply_thresholds.at[index, 'excluded_medMotion']=1
    elif apply_thresholds.at[index, 'fdMedian'] < 0.5 :
        apply_thresholds.at[index, 'excluded_medMotion']=0
    
    if apply_thresholds.at[index, 'IQR'] < 70 :              #if the subject has IQR < 70, write 1 in the 'excluded_IQR_value' column
        apply_thresholds.at[index, 'excluded_IQR_value']=1
    elif apply_thresholds.at[index, 'IQR'] > 70 :              
        apply_thresholds.at[index, 'excluded_IQR_value']=0
    
    if apply_thresholds.at[index, 'jointSpikeCount_Con_percent']>0.2 :   #if the subject has jointSpikeCount_Con_percent > 20%....then write a 1 in 'excluded_outliers' column
        apply_thresholds.at[index, 'excluded_outliers']=1
    elif apply_thresholds.at[index, 'jointSpikeCount_Con_percent']<=0.2:
        apply_thresholds.at[index, 'excluded_outliers']=0
    
    if (apply_thresholds.at[index, 'excluded_medMotion']==1) or (apply_thresholds.at[index, 'excluded_IQR_value']==1) or (apply_thresholds.at[index, 'excluded_outliers']==1) :  #if the subject has been excluded for any reason, write a 0 in the 'Included column'
        apply_thresholds.at[index, 'Included']=0  
    elif (apply_thresholds.at[index, 'excluded_medMotion']==0) and (apply_thresholds.at[index, 'excluded_IQR_value']==0) and (apply_thresholds.at[index, 'excluded_outliers']==0):
        apply_thresholds.at[index, 'Included']=1
    
included = apply_thresholds['Included'].values.tolist()
included.count(1) #returns the number of subjects who passed the QA 

date = datetime.today().strftime('%m%d%y')
apply_thresholds.to_csv('P:/JMQ_Cascio/MRI_analyses/ABIDE_RS/ABIDE_QA_results_' + date + '.csv')

#Next step: demographic/site summary: 
#produce summary of the site distribution/demographics (age, gender) for icluded participants
    # read in prior file and create histogram of age by group
        #all_QA_demog = read.csv("/Volumes/PSR/Zoltowski/MRI_Analyses/AutismRestingState/XNATInventory/AutismResting_ALL_QA_070622.csv", stringsAsFactors = FALSE)
    # filter included participants by group
        #included_asd = all_QA_demog_edited[all_QA_demog_edited$Group=="ASD" & all_QA_demog_edited$Included==1,]
        #included_td = all_QA_demog_edited[all_QA_demog_edited$Group=="TD" & all_QA_demog_edited$Included==1,]
    # plots: 
        #histogram of site by group
            #hist(included_td$site,xlab="Site",main="TD")
            #hist(included_asd$site,xlab="Site",main="ASD")
        #histogram of sex by group: 
            #hist(included_td$sex,xlab="Sex",main="TD")
            #hist(included_asd$sex,xlab="Sex",main="ASD")
        #histogram of age by group
            #hist(included_td$Age,xlab="Age (years)",main="TD")
            #hist(included_asd$Age,xlab="Age (years)",main="ASD")



ORIGINAL SCRIPT for reference: 
    
## Part 1: Main data tracking/merge
#OLD - from original script 
# read in 3 files (cat12 structural QA, connprep coregistration QA, motion tracking file):
#cat12 = read.csv("/Volumes/PSR/Cascio_Lab/Zoltowski/MRI_Analyses/AutismRestingState/Cat12QA/AutismResting_Cat12_QA.csv", stringsAsFactors = FALSE)
#coreg = read.csv("/Volumes/PSR/Cascio_Lab/Zoltowski/MRI_Analyses/AutismRestingState/ConnprepQA/Connprep_QA_Tracking_082222.csv", stringsAsFactors = FALSE)
#motion_demog = read.csv("/Users/alisazoltowski/WorkMacDocuments/LatestDocs/Projects/ASDREST/AutismResting_BestVersions_082222.csv")
# merge the 3 files:
#connprep_demog = merge(motion_demog,coreg,by="MR.ID",all.x=TRUE)
#all_QA_demog = merge(connprep_demog,cat12,by="MR.ID",all.x=TRUE)

#added connprep coreg_exclude variable here, but did cat12 variables prior
# also- add variable of processing errors
#all_QA_demog$ProcessingErrors = ifelse(is.na(all_QA_demog$conncalcID),1,0)
#all_QA_demog$Exclude_Coreg = ifelse(all_QA_demog$CoregistrationQuality=="Poor",1,0)
# add variable summing up total # issues
#all_QA_demog$ExcludeNumIssues = rowSums(all_QA_demog[,c("excluded_medMotion","excluded_outliers", "Exclude_IQR","Exclude_Coreg","Exclude_Normalize","ProcessingErrors")],na.rm=TRUE)
#all_QA_demog$Included = ifelse(all_QA_demog$ExcludeNumIssues > 0,0,1)


# remove "included_motion" variable, since "included" is now complete going forward
# 8/22/22: decided that structural scan num probably not needed since this 
# is blank for so many with just 1 scan
#all_QA_demog = all_QA_demog[,!names(all_QA_demog) %in% c('included_motion','WhichScan','ExcludeNumIssues')]

#8/22/22: order variables so all "exclude" columns togetther
#all_QA_demog = all_QA_demog[,c(1:12,15:16,21,13:14,17:20)]

# save!! 
#write.csv(all_QA_demog,"/Volumes/PSR/Cascio_Lab/Zoltowski/MRI_Analyses/AutismRestingState/XNATInventory/AutismResting_ALL_QA_082222.csv",row.names=FALSE)

## Part 1b (Done May/June 2022)
# Missing data check- compare to initial tracking spreadsheet
#autism_demog = read.csv("/Volumes/PSR/Zoltowski/MRI_Analyses/AutismRestingState/XNATInventory/AutismRestingDemographics_020822.csv", stringsAsFactors = FALSE)
#all_QA_demog = read.csv("/Volumes/PSR/Zoltowski/MRI_Analyses/AutismRestingState/XNATInventory/AutismResting_ALL_QA_070622.csv",stringsAsFactors = FALSE)
#lab drive version: need to filter out invalid study IDs/pilot participants
#autism_valid = autism_demog[!is.na(autism_demog$studyID),] 
#missing_MRs = autism_valid$MR.ID[!autism_valid$uid %in% all_QA_demog$uid]
#missing_xnat = data.frame("MR.ID"=missing_MRs)

# save this info
#write.csv(missing_xnat,"/Volumes/PSR/Zoltowski/MRI_Analyses/AutismRestingState/XNATInventory/missing_processing_070622.csv",row.names=FALSE)

###########

## Part 2: Demographic summary, post inclusion/exclusion decisions
# read in prior file and create histogram of age by group
#all_QA_demog = read.csv("/Volumes/PSR/Zoltowski/MRI_Analyses/AutismRestingState/XNATInventory/AutismResting_ALL_QA_070622.csv", stringsAsFactors = FALSE)

# filter included participants by group
#included_asd = all_QA_demog_edited[all_QA_demog_edited$Group=="ASD" & all_QA_demog_edited$Included==1,]
#included_td = all_QA_demog_edited[all_QA_demog_edited$Group=="TD" & all_QA_demog_edited$Included==1,]

# plots: histogram of age, by group
#hist(included_td$Age,xlab="Age (years)",main="TD")
#hist(included_asd$Age,xlab="Age (years)",main="ASD")

###########

## Part 3: For empathy analyses, merge QA data with MET data
# read in QA file, MET file
#all_QA_demog = read.csv("/Volumes/PSR/Zoltowski/MRI_Analyses/AutismRestingState/XNATInventory/AutismResting_ALL_QA_070622.csv", stringsAsFactors = FALSE)
#met_participants = read.csv("/Users/alisazoltowski/WorkMacDocuments/LatestDocs/Projects/ASDREST/Empathy/MET_RSDemographics_42122.csv")

# get list of MR.IDs from MET file
#met_uids = na.omit(unique(met_participants$uid))

# filter previous file to just include MET ids
#met_QA_demog = all_QA_demog[all_QA_demog$uid %in% met_uids,]

# count: included participants
#sum(met_QA_demog$Included, na.rm = TRUE)

# check exclusion values per reason (total= 76/93 included)
#sum(met_QA_demog$excluded_outliers, na.rm = TRUE) #4
#sum(met_QA_demog$excluded_medMotion, na.rm = TRUE) #3
#sum(met_QA_demog$Exclude_IQR, na.rm = TRUE) #2
#sum(met_QA_demog$Exclude_Normalize, na.rm = TRUE) #2
#sum(met_QA_demog$Exclude_Coreg==1, na.rm = TRUE) #1
#sum(met_QA_demog$ProcessingErrors, na.rm=TRUE) #7
 
# save
#write.csv(met_QA_demog,"/Volumes/PSR/Cascio_Lab/Zoltowski/MRI_Analyses/AutismRestingState/Empathy/MET_RS_QA_082222.csv",row.names=FALSE)


