#!/bin/bash
sudo mkdir /opt/vdl
sudo mkdir /var/log/vdl
sudo chown -R ec2-user:ec2-user /var/log/vdl
sudo cp ./init.d/vdl /etc/init.d/vdl
sudo cp ./logging.ini /opt/vdl/logging.ini
sudo chmod a+x /opt/vdl/logging.ini
sudo chmod a+x /etc/init.d/vdl
sudo cp ./api_execute_data_load.py /opt/vdl/vdl.py
sudo chmod a+x /opt/vdl/vdl.py
echo "Starting VDL Server."
{
sudo update-rc.d vdl defaults
} ||{
sudo chkconfig --add vdl
}
sudo service vdl start

exit 0
