import matplotlib.pyplot as plt
import numpy as np 
import scipy.signal as scsp
import scipy.io.wavfile as scio

from scipy.fftpack import fftshift

def uint_to_float(arr_uint, int_bit_depth):
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
    num_bits = 2**(int_bit_depth-1)
    return arr_sint/num_bits

def float_to_sint(arr_float, int_bit_depth):
    num_bits = 2**(int_bit_depth-1)
    return arr_float*num_bits

def float_to_uint(arr_float, uint_bit_depth):
    # TODO: Implement
    print('Float to UInt not yet implemented')

def wav_to_dict(fnames, ):
    files = {}
    float_sig = {}
    if type(fnames) is str:
        fnames = [fnames]
    for fname in fnames:
        wav = scio.read(fname)
        dt = str(wav[1].dtype)
        if dt.startswith('int'):
            to_float = sint_to_float
        elif dt.startswith('uint'):
            to_float = uint_to_float
        bit_depth = int(str(wav[1].dtype)[-2:])
        files[fname] = wav
        fs = wav[0]
        is_stereo = True if np.size(wav[1][0]) == 2 else False
        if is_stereo:
            left = to_float(left, bit_depth)
            right = to_float(right, bit_depth)
            float_sig[fname] = [fs, left, right,]
        else:
            left = np.array(files[fname][1])/((2**15)-1)
            float_sig[fname] = [fs, left,]
        files[fname] = float_sig[fname]
    return files

def write_wav(fname, fs, data_dtype, wav_dtype, data,):
    # TODO: Make data type flexible
    if data_dtype.startswith('float') and wav_dtype.startswith('int'):
        bit_depth = int(wav_dtype[-2:])
        data = np.array(float_to_sint(data, bit_depth))
    # TODO finish here parsing the dtypes
    out = np.transpose(np.array(data)).astype(wav_dtype)
    scio.write(fname, fs, out.astype(np.int16))
