#!/bin/bash
sudo mkdir /opt/vdl
sudo cp ./init.d/VisionDataLoader /etc/init.d/vdl
sudo cp ./api_execute_data_load.py /opt/vdl/vdl.py
print "Starting VDL Server."
sudo update-rc.d vdl defaults
sudo service vdl start

exit 0