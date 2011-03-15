# Authors: Alexandre Gramfort <gramfort@nmr.mgh.harvard.edu>
#          Matti Hamalainen <msh@nmr.mgh.harvard.edu>
#
# License: BSD (3-clause)

import time
import array
import numpy as np
from scipy import linalg

from .constants import FIFF


def _write(fid, data, kind, data_size, FIFFT_TYPE, dtype):
    FIFFV_NEXT_SEQ = 0
    if isinstance(data, np.ndarray):
        data_size *= data.size
    if isinstance(data, str):
        data_size *= len(data)
    fid.write(np.array(kind, dtype='>i4').tostring())
    fid.write(np.array(FIFFT_TYPE, dtype='>i4').tostring())
    fid.write(np.array(data_size, dtype='>i4').tostring())
    fid.write(np.array(FIFFV_NEXT_SEQ, dtype='>i4').tostring())
    fid.write(np.array(data, dtype=dtype).tostring())


def write_int(fid, kind, data):
    """
    %
    % fiff_write_int(fid,kind,data)
    %
    % Writes a 32-bit integer tag to a fif file
    %
    %     fid           An open fif file descriptor
    %     kind          Tag kind
    %     data          The integers to use as data
    %
    """
    FIFFT_INT = 3
    data_size = 4
    _write(fid, data, kind, data_size, FIFFT_INT, '>i4')


def write_double(fid, kind, data):
    """
    %
    % fiff_write_int(fid,kind,data)
    %
    % Writes a double-precision floating point tag to a fif file
    %
    %     fid           An open fif file descriptor
    %     kind          Tag kind
    %     data          The data
    %
    """
    FIFFT_DOUBLE = 5
    data_size = 8
    _write(fid, data, kind, data_size, FIFFT_DOUBLE, '>f8')


def write_float(fid, kind, data):
    """
    %
    % fiff_write_float(fid,kind,data)
    %
    % Writes a single-precision floating point tag to a fif file
    %
    %     fid           An open fif file descriptor
    %     kind          Tag kind
    %     data          The data
    %
    """
    FIFFT_FLOAT = 4
    data_size = 4
    _write(fid, data, kind, data_size, FIFFT_FLOAT, '>f4')


def write_string(fid, kind, data):
    """
    %
    % fiff_write_string(fid,kind,data)
    %
    % Writes a string tag
    %
    %     fid           An open fif file descriptor
    %     kind          The tag kind
    %     data          The string data to write
    %
    """
    FIFFT_STRING = 10
    data_size = 1
    _write(fid, data, kind, data_size, FIFFT_STRING, '>c')


def write_name_list(fid, kind, data):
    """
    %
    % fiff_write_name_list(fid,kind,mat)
    %
    % Writes a colon-separated list of names
    %
    %     fid           An open fif file descriptor
    %     kind          The tag kind
    %     data          An array of names to create the list from
    %
    """
    write_string(fid, kind, ':'.join(data))


def write_float_matrix(fid, kind, mat):
    """
    %
    % fiff_write_float_matrix(fid,kind,mat)
    % 
    % Writes a single-precision floating-point matrix tag
    %
    %     fid           An open fif file descriptor
    %     kind          The tag kind
    %     mat           The data matrix
    %
    """
    FIFFT_FLOAT = 4
    FIFFT_MATRIX = 1 << 30
    FIFFT_MATRIX_FLOAT = FIFFT_FLOAT | FIFFT_MATRIX
    FIFFV_NEXT_SEQ = 0

    data_size = 4 * mat.size + 4 * 3

    fid.write(np.array(kind, dtype='>i4').tostring())
    fid.write(np.array(FIFFT_MATRIX_FLOAT, dtype='>i4').tostring())
    fid.write(np.array(data_size, dtype='>i4').tostring())
    fid.write(np.array(FIFFV_NEXT_SEQ, dtype='>i4').tostring())
    fid.write(np.array(mat, dtype='>f4').tostring())

    dims = np.empty(3, dtype=np.int32)
    dims[0] = mat.shape[1]
    dims[1] = mat.shape[0]
    dims[2] = 2
    fid.write(np.array(dims, dtype='>i4').tostring())



def write_id(fid, kind, id_=None):
    """
    %
    % fiff_write_id(fid, kind, id)
    %
    % Writes fiff id
    %
    %     fid           An open fif file descriptor
    %     kind          The tag kind
    %     id            The id to write
    %
    % If the id argument is missing it will be generated here
    %
    """

    if id_ is None:
        id_ = dict()
        id_['version'] = (1 << 16) | 2
        id_['machid'] = 65536 * np.random.rand(2) # Machine id (andom for now)
        id_['secs'] = time.time()
        id_['usecs'] = 0            #   Do not know how we could get this XXX

    FIFFT_ID_STRUCT = 31
    FIFFV_NEXT_SEQ = 0

    data_size = 5*4                       #   The id comprises five integers
    fid.write(np.array(kind, dtype='>i4').tostring())
    fid.write(np.array(FIFFT_ID_STRUCT, dtype='>i4').tostring())
    fid.write(np.array(data_size, dtype='>i4').tostring())
    fid.write(np.array(FIFFV_NEXT_SEQ, dtype='>i4').tostring())

    # Collect the bits together for one write
    data = np.empty(5, dtype=np.int32)
    data[0] = id_['version']
    data[1] = id_['machid'][0]
    data[2] = id_['machid'][1]
    data[3] = id_['secs']
    data[4] = id_['usecs']
    fid.write(np.array(data, dtype='>i4').tostring())


def start_block(fid, kind):
    """
    %
    % fiff_start_block(fid,kind)
    %
    % Writes a FIFF_BLOCK_START tag
    %
    %     fid           An open fif file descriptor
    %     kind          The block kind to start
    %
    """

    FIFF_BLOCK_START = 104
    write_int(fid, FIFF_BLOCK_START, kind)


def end_block(fid, kind):
    """
    %
    % fiff_end_block(fid,kind)
    %
    % Writes a FIFF_BLOCK_END tag
    %
    %     fid           An open fif file descriptor
    %     kind          The block kind to end
    %
    """

    FIFF_BLOCK_END = 105
    write_int(fid, FIFF_BLOCK_END, kind)


def start_file(name):
    """
    %
    % [fid] = fiff_start_file(name)
    %
    % Opens a fif file for writing and writes the compulsory header tags
    %
    %     name           The name of the file to open. It is recommended
    %                    that the name ends with .fif
    %
    """
    fid = open(name, 'wb')

    #   Write the compulsory items
    FIFF_FILE_ID = 100
    FIFF_DIR_POINTER = 101
    FIFF_FREE_LIST = 106

    write_id(fid, FIFF_FILE_ID)
    write_int(fid, FIFF_DIR_POINTER, -1)
    write_int(fid, FIFF_FREE_LIST, -1)

    return fid


def end_file(fid):
    """
    %
    % fiff_end_file(fid)
    %
    % Writes the closing tags to a fif file and closes the file
    %
    %     fid           An open fif file descriptor
    %
    """
    data_size = 0
    fid.write(np.array(FIFF.FIFF_NOP, dtype='>i4').tostring())
    fid.write(np.array(FIFF.FIFFT_VOID, dtype='>i4').tostring())
    fid.write(np.array(data_size, dtype='>i4').tostring())
    fid.write(np.array(FIFF.FIFFV_NEXT_NONE, dtype='>i4').tostring())
    fid.close()


def write_coord_trans(fid, trans):
    """
    #
    # fiff_write_coord_trans(fid,trans)
    #
    # Writes a coordinate transformation structure
    #
    #     fid           An open fif file descriptor
    #     trans         The coordinate transfomation structure
    #
    """

    FIFF_COORD_TRANS = 222
    FIFFT_COORD_TRANS_STRUCT = 35
    FIFFV_NEXT_SEQ = 0

    #?typedef struct _fiffCoordTransRec {
    #  fiff_int_t   from;		           /*!< Source coordinate system. */
    #  fiff_int_t   to;		               /*!< Destination coordinate system. */
    #  fiff_float_t rot[3][3];	           /*!< The forward transform (rotation part) */
    #  fiff_float_t move[3];		       /*!< The forward transform (translation part) */
    #  fiff_float_t invrot[3][3];	       /*!< The inverse transform (rotation part) */
    #  fiff_float_t invmove[3];            /*!< The inverse transform (translation part) */
    #} *fiffCoordTrans, fiffCoordTransRec; /*!< Coordinate transformation descriptor */

    data_size = 4*2*12 + 4*2
    fid.write(np.array(FIFF_COORD_TRANS, dtype='>i4').tostring())
    fid.write(np.array(FIFFT_COORD_TRANS_STRUCT, dtype='>i4').tostring())
    fid.write(np.array(data_size, dtype='>i4').tostring())
    fid.write(np.array(FIFFV_NEXT_SEQ, dtype='>i4').tostring())
    fid.write(np.array(trans['from_'], dtype='>i4').tostring())
    fid.write(np.array(trans['to'], dtype='>i4').tostring())

    #   The transform...
    rot = trans['trans'][:3, :3]
    move = trans['trans'][:3, 3]
    fid.write(np.array(rot, dtype='>f4').tostring())
    fid.write(np.array(move, dtype='>f4').tostring())

    #   ...and its inverse
    trans_inv = linalg.inv(trans.trans)
    rot = trans_inv[:3, :3]
    move = trans_inv[:3, 3]
    fid.write(np.array(rot, dtype='>f4').tostring())
    fid.write(np.array(move, dtype='>f4').tostring())


def write_ch_info(fid, ch):
    """
    %
    % fiff_write_ch_info(fid,ch)
    %
    % Writes a channel information record to a fif file
    %
    %     fid           An open fif file descriptor
    %     ch            The channel information structure to write
    %
    %     The type, cal, unit, and pos members are explained in Table 9.5
    %     of the MNE manual
    %
    """

    FIFF_CH_INFO = 203
    FIFFT_CH_INFO_STRUCT = 30
    FIFFV_NEXT_SEQ = 0

    #typedef struct _fiffChPosRec {
    #  fiff_int_t   coil_type;      /*!< What kind of coil. */
    #  fiff_float_t r0[3];          /*!< Coil coordinate system origin */
    #  fiff_float_t ex[3];          /*!< Coil coordinate system x-axis unit vector */
    #  fiff_float_t ey[3];          /*!< Coil coordinate system y-axis unit vector */
    #  fiff_float_t ez[3];                   /*!< Coil coordinate system z-axis unit vector */
    #} fiffChPosRec,*fiffChPos;                /*!< Measurement channel position and coil type */


    #typedef struct _fiffChInfoRec {
    #  fiff_int_t    scanNo;    /*!< Scanning order # */
    #  fiff_int_t    logNo;     /*!< Logical channel # */
    #  fiff_int_t    kind;      /*!< Kind of channel */
    #  fiff_float_t  range;     /*!< Voltmeter range (only applies to raw data ) */
    #  fiff_float_t  cal;       /*!< Calibration from volts to... */
    #  fiff_ch_pos_t chpos;     /*!< Channel location */
    #  fiff_int_t    unit;      /*!< Unit of measurement */
    #  fiff_int_t    unit_mul;  /*!< Unit multiplier exponent */
    #  fiff_char_t   ch_name[16];   /*!< Descriptive name for the channel */
    #} fiffChInfoRec,*fiffChInfo;   /*!< Description of one channel */

    data_size = 4*13 + 4*7 + 16;

    fid.write(np.array(FIFF_CH_INFO, dtype='>i4').tostring())
    fid.write(np.array(FIFFT_CH_INFO_STRUCT, dtype='>i4').tostring())
    fid.write(np.array(data_size, dtype='>i4').tostring())
    fid.write(np.array(FIFFV_NEXT_SEQ, dtype='>i4').tostring())

    #   Start writing fiffChInfoRec
    fid.write(np.array(ch['scanno'], dtype='>i4').tostring())
    fid.write(np.array(ch['logno'], dtype='>i4').tostring())
    fid.write(np.array(ch['kind'], dtype='>i4').tostring())
    fid.write(np.array(ch['range'], dtype='>f4').tostring())
    fid.write(np.array(ch['cal'], dtype='>f4').tostring())
    fid.write(np.array(ch['coil_type'], dtype='>i4').tostring())
    fid.write(np.array(ch['loc'], dtype='>f4').tostring()) # writing 12 values

    #   unit and unit multiplier
    fid.write(np.array(ch['unit'], dtype='>i4').tostring())
    fid.write(np.array(ch['unit_mul'], dtype='>i4').tostring())

    #   Finally channel name
    if len(ch['ch_name']):
        ch_name = ch['ch_name'][:15]
    else:
        ch_name = ch['ch_name']

    fid.write(np.array(ch_name, dtype='>c').tostring())
    if len(ch_name) < 16:
        dum = array.array('c', '\0' * (16 - len(ch_name)))
        dum.tofile(fid)


def write_dig_point(fid, dig):
    """
    %
    % fiff_write_dig_point(fid,dig)
    %
    % Writes a digitizer data point into a fif file
    %
    %     fid           An open fif file descriptor
    %     dig           The point to write
    %
    """

    FIFF_DIG_POINT = 213
    FIFFT_DIG_POINT_STRUCT = 33
    FIFFV_NEXT_SEQ = 0

    #?typedef struct _fiffDigPointRec {
    #  fiff_int_t kind;               /*!< FIFF_POINT_CARDINAL,
    #                                  *   FIFF_POINT_HPI, or
    #                                  *   FIFF_POINT_EEG */
    #  fiff_int_t ident;              /*!< Number identifying this point */
    #  fiff_float_t r[3];             /*!< Point location */
    #} *fiffDigPoint,fiffDigPointRec; /*!< Digitization point description */

    data_size = 5 * 4

    fid.write(np.array(FIFF_DIG_POINT, dtype='>i4').tostring())
    fid.write(np.array(FIFFT_DIG_POINT_STRUCT, dtype='>i4').tostring())
    fid.write(np.array(data_size, dtype='>i4').tostring())
    fid.write(np.array(FIFFV_NEXT_SEQ, dtype='>i4').tostring())

    #   Start writing fiffDigPointRec
    fid.write(np.array(dig['kind'], dtype='>i4').tostring())
    fid.write(np.array(dig['ident'], dtype='>i4').tostring())
    fid.write(np.array(dig['r'][:3], dtype='>f4').tostring())


def write_named_matrix(fid, kind, mat):
    """
    %
    % fiff_write_named_matrix(fid,kind,mat)
    %
    % Writes a named single-precision floating-point matrix
    %
    %     fid           An open fif file descriptor
    %     kind          The tag kind to use for the data
    %     mat           The data matrix
    %
    """
    raise NotImplementedError, "CTF data processing is not supported yet"

    # start_block(fid, FIFF.FIFFB_MNE_NAMED_MATRIX)
    # write_int(fid, FIFF.FIFF_MNE_NROW, mat['nrow'])
    # write_int(fid, FIFF.FIFF_MNE_NCOL, mat['ncol'])
    # 
    # if len(mat['row_names']) > 0:
    #     write_name_list(fid, FIFF.FIFF_MNE_ROW_NAMES, mat['row_names'])
    # 
    # if len(mat['col_names']) > 0:
    #     write_name_list(fid, FIFF.FIFF_MNE_COL_NAMES, mat['col_names'])
    # 
    # write_float_matrix(fid,kind, mat.data)
    # end_block(fid, FIFF.FIFFB_MNE_NAMED_MATRIX)
    # 
    # return;
