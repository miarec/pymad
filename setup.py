"""Setup script for the MAD module distribution."""

import os
import platform
import subprocess
import sys
from pprint import pprint
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


VERSION_MAJOR = 0
VERSION_MINOR = 10
PYMAD_VERSION = str(VERSION_MAJOR) + '.' + str(VERSION_MINOR)


DEFINES = [('VERSION_MAJOR', VERSION_MAJOR),
           ('VERSION_MINOR', VERSION_MINOR),
           ('VERSION', '"%s"' % PYMAD_VERSION)]

# Filename for the C extension module library
c_module_name = 'mad'

# Command line flags forwarded to CMake (for debug purpose)
cmake_cmd_args = []
for f in sys.argv:
    if f.startswith('-D'):
        cmake_cmd_args.append(f)

for f in cmake_cmd_args:
    sys.argv.remove(f)


def _get_env_variable(name, default='OFF'):
    if name not in os.environ.keys():
        return default
    return os.environ[name]


class CMakeExtension(Extension):
    def __init__(self, name, cmake_lists_dir='.', **kwargs):
        Extension.__init__(self, name, sources=[], **kwargs)
        self.cmake_lists_dir = os.path.abspath(cmake_lists_dir)

class CMakeBuild(build_ext):

    def build_extensions(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError('Cannot find CMake executable')

        python_version = '{}.{}.{}'.format(
            sys.version_info.major, 
            sys.version_info.minor, 
            sys.version_info.micro
        )

        for ext in self.extensions:

            extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
            cfg = 'Debug' if _get_env_variable('PYMAD_DEBUG') == 'ON' else 'Release'

            python_module_name, python_module_ext = os.path.splitext(os.path.basename(self.get_ext_fullpath(ext.name)))

            cmake_args = [
                '-DCMAKE_BUILD_TYPE=%s' % cfg,

                # Ask CMake to place the resulting library in the directory
                # containing the extension
                '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir),

                # Other intermediate static libraries are placed in a
                # temporary build directory instead
                '-DCMAKE_ARCHIVE_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), self.build_temp),

                # Hint CMake to use the same Python executable that
                # is launching the build, prevents possible mismatching if
                # multiple versions of Python are installed
                '-DPYTHON_VERSION={}'.format(python_version),

                '-DPYMAD_PYTHON_MODULE_NAME={}'.format(python_module_name),
                '-DPYMAD_PYTHON_MODULE_EXT={}'.format(python_module_ext),

                '-DPYMAD_VERSION={}'.format(PYMAD_VERSION),
            ]

            if platform.system() == 'Windows':
                plat = ('x64' if platform.architecture()[0] == '64bit' else 'Win32')
                cmake_args += [
                    '-DCMAKE_WINDOWS_EXPORT_ALL_SYMBOLS=TRUE',
                    '-DCMAKE_RUNTIME_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir),
                ]
                if self.compiler.compiler_type == 'msvc':
                    cmake_args += [
                        '-DCMAKE_GENERATOR_PLATFORM=%s' % plat,
                    ]
                else:
                    cmake_args += [
                        '-G', 'MinGW Makefiles',
                    ]

            cmake_args += cmake_cmd_args

            pprint(cmake_args)

            if not os.path.exists(self.build_temp):
                os.makedirs(self.build_temp)

            # Config and build the extension
            subprocess.check_call(['cmake', ext.cmake_lists_dir] + cmake_args,
                                  cwd=self.build_temp)

            subprocess.check_call(['cmake', '--build', '.', '--config', cfg],
                                  cwd=self.build_temp)


setup(
    name='pymad',
    version=PYMAD_VERSION,
    description='A wrapper for the MAD libraries.',
    author='Jamie Wilkinson',
    author_email='jaq@spacepants.org',
    url='http://spacepants.org/src/pymad/',
    license='GPL',
    ext_modules=[CMakeExtension(c_module_name)],
    cmdclass={'build_ext': CMakeBuild},
    zip_safe=False,
)
