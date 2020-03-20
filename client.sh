#!/bin/bash

while :
do
    # update client code periodically (sorry github, you're my bandwidth provider)
    git pull
	echo "Starting python script"
	python2.7 client.py
	sleep 5
done



