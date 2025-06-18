import matplotlib.pyplot as plt
import numpy as np 
import scipy.signal as scsp
import scipy.io.wavfile as scio
import sys

def read_intac_txt(fname, ):
    """
    Convert INTAC .txt files to Python dictionary

    Parameters
    ----------
    fname : str
        Filename including directory of the txt file
    
    Returns
    -------
    data : dict
        Dictionary that contains all colums inside the txt file as individual
        dictionary entry.

    Example
    -------
    Read Power spectrum INTAC txt file that conatins columns "Freq (Hz)" and
    "u(V^2 )":
    >>> fname = "PowerSpectrum.txt"
    >>> intac_dict = audiolib.tools.read_intac_txt(fname=fname)
    >>> freq = intac_dict["Freq (Hz)"]
    >>> power_spec = intac_dict["u(V^2 )"]

    """
    with open(fname, 'r') as file:
        data = {}
        lines = file.readlines()

        # Extract column names from the first row
        column_names = lines[0].strip().split('\t')

        # Initialize empty lists for each column
        for column_name in column_names:
            data[column_name] = []
        # Iterate through the rest of the rows and add data to the corresponding column lists
        for line in lines[1:]:
            values = line.strip().split('\t')
            for i in range(len(column_names)):
                data[column_names[i]].append(float(values[i]))

        return data

def closest_idx_to_val(arr, val):
    return np.argmin(np.abs(np.array(arr) - val))

def calc_time_vec(sig_len, fs):
    """
    Create time vector from sig length and sampling freq

    Parameters
    ----------
    sig_len : int
        Length of the signal in samples, starting with 0
    fs : int
        Sampling frequency
    
    Returns
    -------
    t : numpy array
        Time Vector [s]
    """
    sig_dur = sig_len/fs
    t = np.arange(0, sig_dur, 1/fs)
    return t

def uint_to_float(arr_uint, int_bit_depth):
    """
    Turns array of unsigned intergers to array of float

    Parameters
    ----------
    arr_uint : array of unsigned integers
    int_bit_depth : bit depth of arr_uint
    
    Returns
    -------
    arr_float : array of float
    """
    num_neg_bits = 2**(int_bit_depth-1)
    num_pos_bits = num_neg_bits - 1
    arr_wo_offset = arr_uint.astype(float) - num_neg_bits
    arr_float = np.array([])

    for num in arr_wo_offset:
        if num >= 0:
            arr_float = np.append(arr_float, num/num_pos_bits)
        else:
            arr_float = np.append(arr_float, num/num_neg_bits)

    return arr_float

def sint_to_float(arr_sint, int_bit_depth):
    """
    Turns array of signed intergers to array of float

    Parameters
    ----------
    arr_sint : array of unsigned integers
    int_bit_depth : bit depth of arr_sint
    
    Returns
    -------
    arr_float : array of float
    """
    num_bits = 2**(int_bit_depth-1)
    return arr_sint/num_bits

def float_to_sint(arr_float, float_bit_depth):
    """
    Turns array of floats to array of signed int

    Parameters
    ----------
    arr_float : array of float
    float_bit_depth : bit depth of arr_float
    
    Returns
    -------
    arr_sint : array of signed integers
    """
    num_bits = 2**(float_bit_depth-1)
    return arr_float*num_bits

def float_to_uint(arr_float, uint_bit_depth):
    # TODO: Implement
    print('Float to UInt not yet implemented')

def wav_to_dict(fnames, ):
    """
    Read wav files, converts their content to float and
    move their contents to dict.

    Parameters
    ----------
    fnames : array of strings or string
        name of the .wav-file(s) including the directory

    Returns
    -------
    files_dict : dict (nested)
        contains all relevant information of the initial .wav(s), including the raw
        data as float arrays. Has the following form:

        {
            filename0 : {
                'fs': int, # sampling frequency
                'initial_bit_depth': int # bit depth of the initial raw data
                'ch0' : np.array # contents of channel 0 as float
                'ch1' : np.array # contents of channel 1 as float
                ...
            }
            filename1 : {
                'fs': int, # sampling frequency
                'initial_bit_depth': int # bit depth of the initial file
                'ch0' : np.array
                'ch1' : np.array
                ...
            }
        }
        The N numbers of channels in the wav file define the amount of 'chN' entries
        in the filename dict.
    
    """
    files_dict = {}
    if type(fnames) is str:
        fnames = [fnames]
    
    for fname in fnames:
        wav = scio.read(fname)
        dt = str(wav[1].dtype)
        if dt.startswith('int'):
            to_float = sint_to_float
        elif dt.startswith('uint'):
            to_float = uint_to_float
        bit_depth = int(''.join([s for s in str(wav[1].dtype) if s.isdigit()]))
        num_chs = np.size(wav[1][0])
        files_dict[fname] = wav
        file_dict = {
            'fs' : wav[0],
            'initial_bit_depth' : bit_depth,
        }
        for ch in np.arange(num_chs):
            if num_chs == 1:
                file_dict[f'ch{ch}'] = to_float(files_dict[fname][1], bit_depth)  
            else:
                file_dict[f'ch{ch}'] = to_float(files_dict[fname][1][:, ch], bit_depth)
        files_dict[fname] = file_dict
    return files_dict

def write_wav(fname, data, data_dtype, fs, wav_dtype,):
    """
    Write a data set to wav file. 

    Parameters
    ----------
    fname : str
        Target name of the wav-file
    data : array
        data set to be put into wav file
    fs : int
        Sampling frequency of the data
    data_dtype : numpy dtype
        number type of data
    wav_dtype : numpy dtype
        desired type of the format inside the wav file
    """
    # TODO: Make data type flexible
    if data_dtype.startswith('float') and wav_dtype.startswith('int'):
        bit_depth = int(wav_dtype[-2:])
        data = np.array(float_to_sint(data, bit_depth))
    # TODO finish here parsing the dtypes
    out = np.transpose(np.array(data)).astype(wav_dtype)
    scio.write(filename=fname, rate=fs, data=out.astype(np.int16))

def print_progress_bar(iteration, total, length=50, barname=''):
    """
    Displays a progress bar in the console.

    Parameters
    ----------
        iteration (int): Current iteration number.
        total (int): Total number of iterations.
        length (int, optional): Length of the progress bar. Default is 50.

    Raises:
        ValueError: If iteration is greater than total.

    Example:
        total_iterations = 100
        for i in range(total_iterations):
            time.sleep(0.1)  # Simulate work
            print_progress_bar(i + 1, total_iterations)
        print("\nDone!")
    """
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{barname} Progress: |{bar}| {percent}% Complete')
    sys.stdout.flush()
