#!/bin/bash
##################################################################
#    functions
##################################################################

installPyRepo() {
	git clone https://github.com/SpiNNakerManchester/$1
	cd $1
	if [ -f setup.py ] ; then
		python setup.py develop --no-deps || exit $?
	fi
	cd ..
}

installCRepo() {
	git clone https://github.com/SpiNNakerManchester/$1
}

buildCCode() {
export NEURAL_MODELLING_DIRS=`pwd`/sPyNNaker/neural_modelling
export SPINN_DIRS=`pwd`/spinnaker_tools
export PATH=$PATH:`pwd`/spinnaker_tools/tools

cd spinnaker_tools
source $PWD/setup
make clean
make || exit $?
cd ..
cd spinn_common
make clean
make || exit $?
make install
cd ..
cd SpiNNFrontEndCommon/c_common/
cd front_end_common_lib/
make install-clean
cd ..
make clean
make || exit $?
make install
cd ../..
cd sPyNNaker/neural_modelling/
make clean
make || exit $?
echo "completed"
cd ../..
}


##################################################################
#    Script
##################################################################

# create a virtual environment
virtualenv $1
cd $1


source bin/activate

installCRepo spinnaker_tools
installCRepo spinn_common
installPyRepo SpiNNUtils
installPyRepo SpiNNMachine
installPyRepo SpiNNStorageHandlers
installPyRepo PACMAN
installPyRepo SpiNNMan
installPyRepo DataSpecification
installPyRepo SpiNNFrontEndCommon
installPyRepo SpiNNakerGraphFrontEnd
installPyRepo spalloc
installPyRepo sPyNNaker
installPyRepo sPyNNaker8
installPyRepo PyNN8Examples

# install python dependencies
pip install numpy
pip install six
pip install enum34
pip install scipy
pip install lxml
pip install matplotlib
pip install "pyNN>=0.9"
pip install requests
pip install appdirs
pip install spalloc
pip install rig
pip install testfixtures
pip install pytest
pip install jsonschema
pip install lazyarray
pip install "neo==0.6.1"
pip install futures
pip install pylru
pip install sortedcollections
pip install csa

# build the c code
buildCCode

echo export NEURAL_MODELLING_DIRS=`pwd`/sPyNNaker/neural_modelling >> bin/activate
echo export SPINN_DIRS=`pwd`/spinnaker_tools >> bin/activate
echo export PATH=$PATH:`pwd`/spinnaker_tools/tools >> bin/activate

cd PyNN8Examples/examples
python -u va_benchmark.py
