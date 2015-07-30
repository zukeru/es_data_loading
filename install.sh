#!/bin/bash
sudo mkdir /opt/vdl
sudo cp ./init.d/vdl /etc/init.d/vdl
sudo cp ./api_execute_data_load.py /opt/vdl/vdl.py
echo "Starting VDL Server."
{
sudo update-rc.d vdl defaults
} ||{
sudo chkconfig --add vdl
}
sudo service vdl start

exit 0
