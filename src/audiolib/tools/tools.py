import matplotlib.pyplot as plt
import numpy as np 
import scipy.signal as scsp
import scipy.io.wavfile as scio

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
    scio.write(fname, fs, out.astype(np.int16))
