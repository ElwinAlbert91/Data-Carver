# Data-recovery-tool
This tool is used to recover deleted files by scanning disks for hidden data fragments and reassembling them into usable files before the raw data is overwritten by new information.

## Overview


    This tool is used to recover deleted files by scanning a disk image for hidden data fragments and intelligently reassembling them into usable files before the raw data is overwritten. It supports recovery for JPG, PNG, PDF and WAV files from disk images using file signature carving compression and entropy-based analysis.

## Features

    Signature-based recovery for popular formats (JPG, PNG, PDF, WAV)

    Entropy scanning to detect possible fragmented or hidden regions

    Saves recovered files in a dedicated output directory
    

## How It Works

    The tool scans the raw disk image for known file signatures.

    Uses sliding entropy window to identify regions with high randomness typical of compressed formats.

    Extracts files matching headers and footers, checks for corruption, and avoids duplicates using hashes.

    Supports recovery for: JPG, PNG, PDF and WAV.



