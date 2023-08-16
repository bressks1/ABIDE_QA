# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 10:24:38 2023
@author: bressks1

#Created by JMQ, edited into loop by KSB 
#based on prior scripts by AZ 
"""
#This script works on the preprocessed ABIDE I resting state dataset
#For every subject, it grabs the cat12 output file, which is a pdf
#This pdf is a nontext object which means it is made of several images stitched together
#This script breaks the PDF up into its component images
#It then extracts text from these images use the tesseract engine
#To install tesseract for Windows follow these steps: https://stackoverflow.com/questions/46140485/tesseract-installation-in-windows
#In the command line, make sure you have run the following installations: 
    # pip install pytesseract
    # pip install opencv-python
    # pip install pdf2image
    #pip install pymupdf


#IMPORTS 
import os
import fitz  #do not use pip install fitz, use pip install pymupdf
import io
from PIL import Image
import os
import glob
import csv
import numpy
from datetime import datetime
import pytesseract

# Set up base directory (motion output folder)
baseDir = 'P:\JMQ_Cascio\MRI_analyses\ABIDE_RS'

#sample file path: 'P:\JMQ_Cascio\MRI_analyses\ABIDE_RS\cat12\ABIDE\Caltech_51456\Caltech_51456\ABIDE-x-Caltech_51456-x-Caltech_51456-x-cat12_ss2p0_v2-x-35ce638d-e78d-41ae-9c6f-11433a0ec457\PDF\catreport_t1.pdf'
#generic file path: 'P:\JMQ_Cascio\MRI_analyses\ABIDE_RS\cat12\ABIDE\*\*\*\PDF\catreport_t1.pdf'

# get list of all subject folders within cat12 folder --------------------------------------------------------------------------------------------------------------------
#subjectFiles = glob.glob(baseDir + '*')
subjectBase = sorted(glob.glob(baseDir +'\cat12\ABIDE\*'))
subjectFiles = sorted(glob.glob(baseDir + '\cat12\ABIDE\*\*\*\PDF\catreport_t1.pdf'))   #subjectFiles is a list of all the file paths for the cat12 pdf of every subject
print(len(subjectFiles))  #there are 989 individual subject folders

# configure tesseract ---------------------------------------------------------------------------------------------------------------------------------------------------
from pytesseract import pytesseract
#pytesseract.tesseract_cmd = "/opt/homebrew/Cellar/tesseract/5.3.1_1/bin/tesseract"
#pytesseract.tesseract_cmd = "D:\Bress\Tesseract-OCR\tesseract.exe"       #make sure this is set to the path of the tesseract.exe on your device (wherever you installed tesseract originally)
pytesseract.tesseract_cmd = r'C:\Users\bressks1\tesseract.exe'
# configurations
config = ("-l eng — oem 1 — psm 3")

# set up cat12 summary file, dated with current date and desired columns -----------------------------------------------------------------------------------------------
summaryDate = datetime.today().strftime('%m%d%y')
cat12summary = baseDir + "\cat12" "\cat12_summary_" + summaryDate + ".csv"
# create initial labels
with open(cat12summary, 'a') as csvfile:
    cat12_writer = csv.writer(csvfile, quotechar='|', quoting=csv.QUOTE_MINIMAL)
    cat12_writer.writerow(['MR.ID','IQR','IQR_Grade'])


# run loop to write the IQR value and grade to the cat12 summary file 
for path in subjectFiles:
    for subject in subjectBase: 
            if subjectFiles.index(path) == subjectBase.index(subject): 
                file = path 
                subjectID = os.path.basename(subject)
                pdf_file = fitz.open(file)
                cat12 = (subject + "/FD/FD.txt")
                output_dir = "P:/JMQ_Cascio/MRI_analyses/ABIDE_RS/cat12/cat12_screenshots" + '/'+ subjectID   # Output directory for the extracted images
                if os.path.exists(output_dir) == False: 
                    os.makedirs(output_dir)
                output_format = "png"
                min_width = 100      # Minimum width and height for extracted images
                min_height = 100
                
                for page_index in range(len(pdf_file)):
                    page = pdf_file[page_index]    # Get the page itself
                    image_list = page.get_images(full=True)  # Get image list
                    if image_list:
                        print(f"[+] Found a total of {len(image_list)} images in page {page_index}")  # Print the number of images found on this page
                    else:
                        print(f"[!] No images found on page {page_index}")
                    # Iterate over the images on the page
                    images = []
                    for image_index, img in enumerate(image_list, start=1):
                        # Get the XREF of the image
                        xref = img[0]
                        # Extract the image bytes
                        base_image = pdf_file.extract_image(xref)
                        image_bytes = base_image["image"]
                        # Get the image extension
                        image_ext = base_image["ext"]
                        # Load it to PIL
                        image = Image.open(io.BytesIO(image_bytes))
                        # Check if the image meets the minimum dimensions and save it
                        # if image.width >= min_width and image.height >= min_height:
                        #     image.save(
                        #         open(os.path.join(output_dir, f"image{page_index + 1}_{image_index}.{output_format}"), "wb"),
                        #         format=output_format.upper())
                        # else:
                        #     print(f"[-] Skipping image {image_index} on page {page_index} due to its small size.")
                        images.append(image)
                    text_org = pytesseract.image_to_string(images[25], config=config)
                    
                    #the text is split up into multiple lines, the first step is creating a string in one line
                    text = text_org.replace('\n', '').replace(')): ', ')').replace('-', '').replace('+', '')                      
                    #get the IQR value from the text string
                    IQR = text[40:46]     
                    
                    #the + and - characters need to be dealt with separately from the numerical characters
                    Grade_Value_org = ((text_org.replace('\n', ''))[41:58])  #this pulls the values at the end of the string 
                    if '-' in Grade_Value_org: 
                        Grade_Value = '-'
                    elif '+' in Grade_Value_org: 
                        Grade_Value = '+'
                    else: 
                        Grade_Value = ''  
                    IQR_Grade = ((text[47:50]).replace('(', '').replace(')', '') + Grade_Value)      #get the IQR grade, +/- value, and get ride of parentheses
                
                print(IQR + ' ' + IQR_Grade)
                                
                # Finally, write the IQR grade and value to the spreadsheet
                with open(cat12summary, 'a', newline='') as csvfile:
                    cat12_writer = csv.writer(csvfile, quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    cat12_writer.writerow([subjectID, IQR, IQR_Grade])
                              
                