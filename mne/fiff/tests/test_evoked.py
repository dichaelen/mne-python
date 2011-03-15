import os.path as op

from numpy.testing import assert_array_almost_equal, assert_equal

from .. import read_evoked, write_evoked

fname = op.join(op.dirname(__file__), 'data', 'test-ave.fif')

def test_io_evoked():
    """Test IO for noise covariance matrices
    """
    ave = read_evoked(fname)

    write_evoked('evoked.fif', ave)
    ave2 = read_evoked('evoked.fif')

    print assert_array_almost_equal(ave.data, ave2.data)
    print assert_array_almost_equal(ave.times, ave2.times)
    print assert_equal(ave.nave, ave2.nave)
    print assert_equal(ave.aspect_kind, ave2.aspect_kind)
    print assert_equal(ave.last, ave2.last)
    print assert_equal(ave.first, ave2.first)