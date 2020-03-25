# quarantineAtHome

### About

quarantine@Home is a distributed computing project (like SETI@home) to fight the COVID19 viral pandemic.
 Other efforts like [Folding@home](https://foldingathome.org/2020/03/15/coronavirus-what-were-doing-and-how-you-can-help-in-simple-terms/) and [Rosetta@home](https://www.ipd.uw.edu/2020/02/rosettas-role-in-fighting-coronavirus/) are conducting important experiments as well.
 
 This project is conducting a different kind of experiment. Instead of folding large proteins, we are docking small molecule compounds to proteins that are important for the infection. The software we are using is [Autodock](http://autodock.scripps.edu/)
 
 Small molecules are taken from the UCSF [Zinc](https://zinc.docking.org/) database, which has conveniently divided these ligands into "tranches" based on their physical properties. To minimize load on the database, clients are programmed to download and compute single tranches at a time.

This project is being written in Dockerfiles, to allow the ease of distributing work.


![alt text](img/spike1.jpg "Spike protein")



### Building and running

If you want your username to appear in the leaderboards, change "anonymous" below

##### CPU users :
This uses the standard version of AutoDock4.

    sudo docker build -t quarantine -f Dockerfile .
    sudo docker run -it -e ME=anonymous quarantine

##### GPU users (much faster!) :
You will need to have nvidia-docker installed. This will run a [GPU-optimized version of Autodock](https://github.com/ccsb-scripps/AutoDock-GPU) 

    sudo docker build -t quarantinegpu -f Dockerfile.gpu .
    sudo nvidia-docker run -it -e ME=anonymous quarantinegpu
    
Need nvidia-docker? [this is the best tutorial on how to install it](https://medium.com/@sh.tsang/docker-tutorial-5-nvidia-docker-2-0-installation-in-ubuntu-18-04-cb80f17cac65)


##### Why Docker ?

I'm no docker fanatic, but this needs to be portable to make it easier for participants to easily contribute. Installing the base packages is quite laborious.

Also, we're going to try using [boinc2docker](https://github.com/marius311/boinc-server-docker/blob/master/docs/cookbook.md) to deploy this on all systems

![alt text](img/dawg.jpg "Yo Dawg!")


#### Troubleshooting

##### General Docker stuff
General tips for troubleshooting docker quickly.
* If process does not respond to ctrl+c, try launching it from a .sh file.
* List processes: sudo docker ps
* Kill all docker running: sudo docker kill $(docker ps -q)
* Shell into docker instance (useful to move files or debug): sudo docker exec -it $DOCKERID /bin/bash

##### Error: clGetPlatformIDs(): -1001
This is an error due to libraries missing from the docker container, as may happen when mixing distros/repos.

First make sure your user is in the docker group (also helps with running without sudo): sudo usermod -a -G docker $USER

Some people report that running with sudo helps. In complicated setups it may still fail because "libnvidia-ml.so" and other libraries may be missing from "/usr/lib/x86_64-linux-gnu/" within the container (typically part of NVIDIA driver package on the host). In that case you must manually copy these libraries into the container once:

	sudo docker cp /usr/lib/x86_64-linux-gnu/ $DOCKERID:/nvidia
	sudo docker exec -it $DOCKERID /bin/bash
	cp -a /nvidia/* /usr/lib/x86_64-linux-gnu/*

Once that is done, if you copy "nvidia-smi" or "deviceQuery" (from https://github.com/NVIDIA/cuda-samples.git) into the container it should work correctly as on the host. Without this fix "deviceQuery" gives you this error;

	./deviceQuery Starting...
	
	CUDA Device Query (Runtime API) version (CUDART static linking)
	
	cudaGetDeviceCount returned 35
	-> CUDA driver version is insufficient for CUDA runtime version
	Result = FAIL

##### nvidia-docker networking
If experiencing issues, in debug mode particularly, maybe add "--net=host" to the nvidia-docker arguments.

### TODO
Potential improvements:
*  Prioritize subsets that are known safe (tracking them in scoreboard too), followed by those that are available (from http://zinc.docking.org/substances/subsets/)
	* world - drugs approved throughout the world, as often these have useful off-target effects
	* in-vivo - tested in man and animals, so we have some context about their toxicity
	* biogenic / in-stock / for-sale - broader search for available chemicals
* Have server analyze which tranche files have the most interesting ligands, try to assign multiple ligands from the same tranche file to the same client (avoids excessive downloading)
* Multithreading and pipelining, 
	* GPU version - CPU starts extracting next ligand and generates parameters while GPU is processing
	* CPU verison - run multiple docking concurrently on physical CPU cores (not hyperthreading) (current hacky approach is to launch many containers in parallel)
