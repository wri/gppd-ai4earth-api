""" This file is a script to concatenate files into a master set from the command line to avoid running this
on a notebook, although a notebook can be used to check for correctness.
"""
import sys
import gppd_ai4earth.gppd_co2 as gp

def main():
    """ 

    Usage (from command line)
    python "path/to/concat.py" <directory> <as_filename>

    Parameters
    directory: string, the path to the directory containing the datasets to be concatenated
    as_filename: string, the name of concatenated dataset to be saved as
    """

    master_df = gp.data_integration.make_master_df(sys.argv[1])
    gp.data_integration.save_data(master_df, sys.argv[2], sys.argv[1])

main()
