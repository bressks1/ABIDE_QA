# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 11:29:47 2023

@author: bressks1
"""

#this script can be used to OPEN cat12 pdf files from a specific subject or site in the browser
#this is useful for doing automated QA because you can open several files at once without having to click through all the subfolders

import os, os.path
import glob 
import seaborn as sns
import numpy as np 
import pandas as pd

os.chdir("P:\\JMQ_Cascio\\MRI_analyses\\ABIDE_RS\\cat12\\ABIDE")

base_dir = "P:\\JMQ_Cascio\\MRI_analyses\\ABIDE_RS\\cat12\\ABIDE\\"
#example file path: "P:\JMQ_Cascio\MRI_analyses\ABIDE_RS\cat12\ABIDE\Caltech_51456\Caltech_51456\ABIDE-x-Caltech_51456-x-Caltech_51456-x-cat12_ss2p0_v2-x-35ce638d-e78d-41ae-9c6f-11433a0ec457\PDF\catreport_t1.pdf"    

qa_list = pd.read_csv("P:\\JMQ_Cascio\\MRI_analyses\\ABIDE_RS\\QA_visualinspection_KSB.csv")  #1/3 of subjects from each site have been randomly selected for QA - this is a list of those subjects 

pdf_list = []
for file in glob.glob(base_dir + '*\\*\\*\\PDF\\catreport_t1.pdf' ):  #this creates a list of ALL subjects in the ABIDE dataset
    pdf_list.append(file)


site_names = ['Caltech', 'CMU', 'KKI', 'Leuven', 'MaxMun', 'NYU', 'OHSU', 'Olin', 'Pitt', 'SDSU', 'Stanford', 'Trinity', 'UCLA', 'UM', 'USM', 'Yale']


subj_list = list(qa_list['MR.ID'])
site_list = []                  #reset the empty list every time you run the loop
for subj in subj_list: 
    if site_names[7] in subj:   #change the number here to open subjects from different sites
        site_list.append(subj)
print(site_list)                #check that the subj are in the correct order - this is the order the pdfs will open in 
print(len(site_list))
for i in site_list: 
    for file in pdf_list: 
        if i in file: 
            os.startfile(file)