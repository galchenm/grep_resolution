#!/usr/bin/env python3
# coding: utf8

"""
"""


import os
import sys
import h5py as h5
import subprocess
import re
import argparse
from collections import defaultdict
import pandas as pd


class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('-i', type=str, help="Input stream file")
    parser.add_argument('-o', type=str, help='Output stream file')
    parser.add_argument('-r', type=float, help='Resolution')
    parser.add_argument('-op', type=str, help='eq/gt/lt operations')
    return parser.parse_args()

def switch_func(value, i, resolution): 
    return { 'eq': lambda val: val == resolution, 'gt': lambda val: val > resolution, 'lt': lambda val: val < resolution, }.get(value)(i)

def parsing_stream(input_stream, output_stream, resolution, operation):
    out = open(output_stream, 'w')
    
    '''
    Image filename: /asap3/petra3/gpfs/p11/2020/data/11009046/raw/run87/87_data_000003.h5
    Event: //607
    Image serial number: 608
    hit = 1
    indexed_by = mosflm-latt-nocell
    n_indexing_tries = 6
    photon_energy_eV = 12000.000000
    beam_divergence = 0.00e+00 rad
    beam_bandwidth = 1.00e-08 (fraction)
    average_camera_length = 0.288000 m
    num_peaks = 31
    peak_resolution = 2.462998 nm^-1 or 4.060093 A
    '''
    total_filenames = 0
    total_hits = 0

    with open(input_stream, 'r') as stream:
        reading_chunk = False
        found_pattern = False

        for line in stream:
            
            if line.strip() == '----- Begin chunk -----':
                reading_chunk = True
                chunk = line

            elif line.startswith('Image filename:'):
                name_of_file = line.split()[-1]
                total_filenames += 1
                found_pattern = True
                chunk += line

            elif line.startswith('peak_resolution = '):
                chunk += line
                peak_resolution = re.findall(r'[\d]+[.]+[\d]* A', line.strip())[0]
                peak_resolution = float(re.findall(r'[\d]+[.]+[\d]*', peak_resolution)[0])
                print(name_of_file,peak_resolution)
                

            elif line.strip() == '----- End chunk -----':
                reading_chunk = False
                chunk += line
                result = switch_func(operation, peak_resolution, resolution)
                if found_pattern and result:
                   
                    out.write(chunk)

                found_pattern = False

            elif reading_chunk:
                chunk += line

            else:
                out.write(line)
    out.close()
    




if __name__ == "__main__":
    args = parse_cmdline_args()
    input_stream = args.i
    output_stream = args.o
    resolution = args.r
    operation = args.op

    parsing_stream(input_stream, output_stream, resolution, operation)
