pymad - a Python wrapper for the MPEG Audio Decoder library
===========================================================

![ci](https://github.com/jaqx0r/pymad/workflows/CI/badge.svg)
pymad is a Python module that allows Python programs to use the MPEG Audio Decoder library. pymad provides a high-level API, similar to the pyogg module, which makes reading PCM data from MPEG audio streams a piece of cake.

MAD is available at http://www.mars.org/home/rob/proj/mpeg/

Access this module via `import mad`.  To decode
an mp3 stream, you'll want to create a `mad.MadFile` object and read data from
that.  You can then write the data to a sound device.  See the example
program in `test/` for a simple mp3 player that uses the `python-pyao` wrapper around libao for the sound
device.

pymad wrapper isn't as low level as the C MAD API is, for example, you don't
have to concern yourself with fixed point conversion -- this was done to
make pymad easy to use.

```python
import sys

import ao
import mad

mf = mad.MadFile(sys.argv[1])
dev = ao.AudioDevice(0, rate=mf.samplerate())
while 1:
    buf = mf.read()
    if buf is None:  # eof
        break
    dev.play(buf, len(buf))
```


Building a binary package
-----------------------------------------

To build a binary package for your platform (*.whl), run:

    python -m pip wheel .


Troubleshooting a compilation of the library (C code)
------------------------------------------------------

The library is build with CMake, which is automatically called
when setuptools is building the package.

You can call CMake directly to see the error messages if any:

    cmake -S . -B build -DPYTHON_VERSION=3.8 -DPYMAD_VERSION=0.0.1
    cmake --build build