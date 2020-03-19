# quarantineAtHome

### Note - this isn't ready yet

It literally won't run if you try. I will remove this notice when it does.

Want to help? I need people to look ahead to how to better package this for non-linux users. The best platform for this is BOINC, specifically with [boinc2docker](https://github.com/marius311/boinc-server-docker/blob/master/docs/cookbook.md) 

### About

quarantine@Home is a distributed computing project (like SETI@home) to fight the COVID19 viral pandemic.
 Other efforts like [Folding@home](https://foldingathome.org/2020/03/15/coronavirus-what-were-doing-and-how-you-can-help-in-simple-terms/) and [Rosetta@home](https://www.ipd.uw.edu/2020/02/rosettas-role-in-fighting-coronavirus/) are conducting important experiments as well.
 
 This project is conducting a different kind of experiment. Instead of folding large proteins, we are docking small molecule compounds to proteins that are important for the infection. The software we are using is [Autodock](http://autodock.scripps.edu/)
 
 Small molecules are taken from the UCSF [Zinc](https://zinc.docking.org/) database, which has conveniently divided these ligands into "tranches" based on their physical properties. To minimize load on the database, clients are programmed to download and compute single tranches at a time.

This project is being written in Dockerfiles, to allow the ease of distributing work.


![alt text](img/spike1.jpg "Spike protein")

### Building

##### GPU users :
You will need to have nvidia-docker installed 

    sudo docker build -t quarantinegpu -f Dockerfile.gpu .
    