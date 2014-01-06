GWFrames
========
Manipulate gravitational waveforms—changing frames, and so on.

The code in this project extends code written for the paper "[Angular
velocity of gravitational radiation from precessing binaries and the
corotating frame](http://arxiv.org/abs/1302.2919)", giving an explicit
implementation of the methods discussed in it.  The first commit of
this project is the last commit of the paper's project.

The license for using this software is basically open (see the LICENSE
file in this directory), though citations to the original paper are
appreciated, where relevant.

Note that this code is not optimized.  In many cases, obvious
optimizations were rejected in favor of clearer or simpler code, or
code that simply reflected the discussion in the paper more directly.
The code is generally more than fast enough for interactive use on
individual waveforms, but there is plenty of room for improvement.  In
particular, rotations may be painfully slow for large data sets.


Build requirements
==================
To build just the C++ code:
* C++ compiler
* [GNU Scientific Library](http://www.gnu.org/software/gsl/), built as a shared library

To use the optional—but highly recommended—Python interface:
* [SWIG](http://www.swig.org/) v2.0 or greater
* [Python](http://www.python.org/getit/) v2.7.4 or greater (but not v3.*), with development headers (python-dev or similar)
* [HDF5](http://www.hdfgroup.org/HDF5/) v1.8.10 or greater, built as a shared library with development headers (libhdf5-dev or similar)

And the following, for which python's automatic installation utility
[`pip`](http://www.pip-installer.org) can do all the work:
* [NumPy](http://www.numpy.org/) v1.7 or greater (`pip install --user numpy`)
* [Matplotlib](http://matplotlib.org/) v1.2 or greater (`pip install --user matplotlib`)
* [h5py](http://code.google.com/p/h5py/) v2.1 or greater (`pip install --user h5py`)
* [IPython](http://ipython.org/) v1.0 or greater, with notebook (`pip install --user ipython \[notebook\]`)

N.B.: These must all be compiled with the same compiler.  In
particular, if you are using this on a cluster, check to ensure that
the requirements are all compiled with the same compiler.

All of the above are reasonably standard, and can be installed easily
through package managers such as apt and homebrew.  The notebook
interface for IPython provides an environment much like the
Mathematica notebook interface.  The examples are provided in a
notebook (*.ipynb) file.


Getting started
===============
The code is mostly in the form of C++, for speed.  All functions are
provided in the `GWFrames` namespace.  The interface is reasonably
straightforward, and can easily be included into and compiled with
other code.  Look for examples of how to do this in the `C++Example`
directory.  (See below for a few more details.)


However, it is mostly intended to be used through the interface to
python.  With the above-listed requirements, build the code and
install to the user directory.  To do this, run `make` or

    python setup.py install --user

After this, you should be able to start a new python session (in any
directory) and `import GWFrames`, which is the basic module provided
by this code.  The primary objects are `Quaternion` and `Waveform`
objects, with various methods defined for each.  The IPython notebook
`Docs/Documentation.ipynb` contains extensive examples, following the outline
of the paper.  To use it, run

    ipython notebook Documentation.ipynb --pylab

Alternatively, this code may be used directly through its C++
interface.  A simple example is provided in the `C++Example`
directory, along with the Makefiles needed to build all the necessary
code.  If it does not compile easily, make sure the various paths in
_both_ Makefiles are set properly.

Detailed documentation of most functions may be found through python's
`help` function, or by running `make` in the `Docs` subdirectory, and
reading `Docs/html/index.html`.
