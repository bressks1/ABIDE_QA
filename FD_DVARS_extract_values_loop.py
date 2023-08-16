# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 13:45:32 2023

@author: bressks1
"""

# Modified from Alisa Zoltowski on 06/23 by Jennifer Quinde Zlibut
# From original document: 
## This script loops through participants with connprep output, downloaded from XNAT
## And summarizes motion from fd, dvars
## Created by Alisa Zoltowski 3/10/22
### Modified to include output based on volumes. Percent jointSpikes from fd and dvars

import os
import glob
import csv
import numpy
from datetime import datetime

baseDir = "/Volumes/Cascio_lab/JMQ_Cascio/MRI_analyses/ABIDE_RS/Motion"
basesubjDir = baseDir + "/Subjs"
basefeatDir = baseDir + "/Preprocessing"
baseDir

# Define function to detect outliers
# Adapted from code online to return volume, rather than value,
# of outlying FD or DVARS
def detect_outlier(data):
    # find q1 and q3 values
    q1, q3 = numpy.percentile(sorted(data), [25, 75])

    # compute IRQ
    iqr = q3 - q1

    # find lower and upper bounds
    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)

    outliers = [i for i, x in enumerate(data) if x <= lower_bound or x >= upper_bound]

    return outliers

# get list of all subject folders within FD folder
# edited path 8/19/22 from /MOTION/ASDREST/* previously
subjectFiles = sorted(glob.glob(baseDir + '/ABIDE/*'))

# set up motion summary file, dated with current date
summaryDate = datetime.today().strftime('%m%d%y')
motionSummary = baseDir + "/motion_summary_" + summaryDate + ".csv"
# create initial labels
with open(motionSummary, 'a') as csvfile:
    motion_writer = csv.writer(csvfile, quotechar='|', quoting=csv.QUOTE_MINIMAL)
    motion_writer.writerow(['MR.ID', 'connprepID', 'fdMean', 'fdMedian', 'fdMax', 'fdSpikeCount_Con',
                            'fdSpikeCount_Lib','dvarsMean', 'dvarsMedian', 'dvarsMax', 'dvarsSpikeCount_Con',
                            'dvarsSpikeCount_Lib','jointSpikeCount_Con', 'jointSpikeCount_Lib','jointSpikeCount_Con_percent','jointSpikeCount_Lib_percent'])


# summarize fd, dvars motion parameters:
for subject in subjectFiles:

    # loop through all iterations of connprep to:
    # 1) summarize average, maximum FD and DVARS
    # 2) calculate outlying frames as FD > 0.2 or DVARS > 0.03
    # Sources: Parkes et al., 2018; Power et al. 2013
    ## Edited 6/29/22: for population generalizability, focus on FD > 1mm
    # or DVARS > 0.05
    # 3) and write to motion summary csv

    # first: get all connprep subfolders for subject
    subjectID = os.path.basename(subject)
    connprepVersions = glob.glob(subject + '/*/*')

    for connprep in connprepVersions:
        # get the id associated with that version
        connprepID = connprep.split('-x-')[4]

        # find FD, DVARS files
        fdFile = connprep + "/FD/FD.txt"
        dvarsFile = connprep + "/DVARS/DVARS.txt"
        fdData = []
        dvarsData = []

        # First, if FD file exists, loop through to read in data:
        if os.path.exists(fdFile):
            #loop through framewise displacement file and read values
            with open(fdFile) as fd:
                fd_reader = csv.reader(fd, delimiter=' ', skipinitialspace=True)
                for line in fd_reader:
                    fdData.append(float(line[0]))

            # calculate average and maximum motion per FD
            fdMean = numpy.average(fdData)
            fdMedian = numpy.median(fdData)
            fdMax = max(fdData)
            # calculate FD 'spikes' above 0.2 threshold (Parkes et al., 2018)
            # or 1mm (e.g., anxiety papers) or 1 voxel (e.g., Richardson et al. 2018)
            fdArray = numpy.asarray(fdData)
            fdSpikes_Con = fdArray > 1
            fdSpikeCount_Con = fdSpikes_Con.sum()
            # calculate FD 'spikes' as individual outlier (used in FSL implementation)
            fdOutliers = detect_outlier(fdData)
            fdSpikeCount_Lib = len(fdOutliers)
            



        # otherwise, fill in NA for the following values
        else:
            fdMean = 'NA'
            fdMedian = 'NA'
            fdMax = 'NA'
            fdSpikeCount_Con = 'NA'
            fdSpikeCount_Lib = 'NA'
            jointSpikeCount_Con = 'NA'
            jointSpikeCount_Lib = 'NA'
            

        # Second, if DVARS file exists, loop through to read data
        if os.path.exists(dvarsFile):
            # loop through DVARS file and read values
            with open(dvarsFile) as dvars:
                dvars_reader = csv.reader(dvars, delimiter=' ', skipinitialspace=True)
                for line in dvars_reader:
                    dvarsData.append(float(line[0]))

            # calculate average and maximum motion per DVARS
            dvarsMean = numpy.average(dvarsData)
            dvarsMedian = numpy.median(dvarsData)
            dvarsMax = max(dvarsData)
            # calculate DVARS values above 3% threshold (Parkes et al., 2018)
            # or- 5% threshold (e.g., Afyouni & Nichols, 2018)
            dvarsArray = numpy.asarray(dvarsData)
            dvarsSpikes_Con = dvarsArray > 5
            dvarsSpikeCount_Con = dvarsSpikes_Con.sum()
            # calculate DVARS 'spikes' as individual outlier (used in FSL implementation)
            dvarsOutliers = detect_outlier(dvarsData)
            dvarsSpikeCount_Lib = len(dvarsOutliers)

        # otherwise, fill in NA for the following values
        else:
            dvarsMean = 'NA'
            dvarsMedian = 'NA'
            dvarsMax = 'NA'
            dvarsSpikeCount_Con = 'NA'
            dvarsSpikeCount_Lib = 'NA'

        # Third, if both FD and DVARS files exist,
        # get number of frames with either FD, DVARS 'spikes'
        if os.path.exists(fdFile) and os.path.exists(dvarsFile):
            # a) According to conservative definition (threshold)
            jointSpikes_Con = numpy.logical_or(fdSpikes_Con, dvarsSpikes_Con)
            jointSpikeCount_Con = jointSpikes_Con.sum()
            conSpikeList = str([i for i, x in enumerate(jointSpikes_Con) if x])
            print('Joint outlier volumes for subject ' + subjectID + ', with conservative approach: ' + conSpikeList)
            jointSpikeCount_Con_percent = jointSpikeCount_Con / len(fdArray)
            # b) According to liberal definition (outliers)

            # prior option: "and"
            jointSpikes_Lib = [element for element in fdOutliers if element in dvarsOutliers]
            # option two: "or"
            #jointSpikes_Lib = list(set(fdOutliers + dvarsOutliers))
            # continuing:
            jointSpikeCount_Lib = len(jointSpikes_Lib)
            libSpikeList = str(jointSpikes_Lib)
            print('Joint outlier volumes for subject ' + subjectID + ', with liberal approach: ' + libSpikeList)
            jointSpikeCount_Lib_percent = jointSpikeCount_Lib / len(fdArray)

        # Finally, write the current values to motion spreadsheet
        with open(motionSummary, 'a') as csvfile:
            motion_writer = csv.writer(csvfile, quotechar='|', quoting=csv.QUOTE_MINIMAL)
            motion_writer.writerow([subjectID, connprepID, fdMean, fdMedian, fdMax, fdSpikeCount_Con,
                            fdSpikeCount_Lib, dvarsMean, dvarsMedian, dvarsMax, dvarsSpikeCount_Con,
                            dvarsSpikeCount_Lib, jointSpikeCount_Con, jointSpikeCount_Lib,jointSpikeCount_Con_percent,jointSpikeCount_Lib_percent])
