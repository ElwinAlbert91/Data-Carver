# Data-recovery-tool
This tool is used to recover deleted files by scanning disks for hidden data fragments and reassembling them into usable files before the raw data is overwritten by new information.

## Repository Structure

    |-- backend/
    |    |-- backend.py
    |    |-- requirements.txt
    |-- frontend/
    |    |-- (frontend files)
    |-- recovered/
    |    |-- (recovered files output)
    |-- README.md


## Overview


This project provides a robust solution to recover lost or deleted files directly from raw disk images. It is designed to handle cases where traditional metadata is missing or corrupted by employing a two-step recovery approach:

Signature Analysis: 
    
    The tool first scans the raw disk image to detect files using known format signatures.

Internal Structure Analysis: 
 
    If file signatures are not found or incomplete, the tool analyzes the internal structure and format-specific patterns to recover fragmented or damaged files.

The frontend accepts raw disk images and coordinates with backend modules responsible for extraction, entropy analysis, and intelligent file reassembly, ensuring reliable recovery even under challenging conditions.

Signature-based recovery for popular formats (JPG, PNG, PDF, WAV)

Entropy scanning to detect possible fragmented or hidden regions

Saves recovered files in a dedicated output directory
    

## How It Works

    The tool scans the raw disk image for known file signatures.

    Uses sliding entropy window to identify regions with high randomness typical of compressed formats.

    Extracts files matching headers and footers, checks for corruption, and avoids duplicates using hashes.

    Supports recovery for: JPG, PNG, PDF and WAV.

## Backend
    The backend folder contains the core recovery logic implemented in backend.py. It uses Python standard libraries (listed in requirements.txt) to scan raw disk images and recover files based on signature and entropy analysis.

Requirements

To install backend dependencies, run:

    pip install -r backend/requirements.txt

(This can be minimal or empty if only standard libraries are used but include it to keep structure clean.)

Running Backend (For Developers)

Developers can navigate to the backend folder and run:

    python3 main.py

to test the recovery logic independently.

## Backend Output 

![Alt text](https://github.com/user-attachments/assets/b0a0123e-bec0-46c3-93cd-b8415032275b)






