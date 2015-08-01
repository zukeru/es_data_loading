#!/bin/bash
sudo mkdir /opt/vdl
sudo cp ./init.d/vdl /etc/init.d/vdl
sudo cp ./logging.ini /opt/vdl/logging.ini
sudo chmod a+x /opt/vdl/logging.ini
sudo cp ./logging.ini /opt/vdl/status-logging.ini
sudo chmod a+x /opt/vdl/status-logging.ini
sudo chmod a+x /etc/init.d/vdl
sudo cp ./api_execute_data_load.py /opt/vdl/vdl.py
sudo chmod a+x /opt/vdl/vdl.py
sudo cp ./status.py /opt/vdl/status.py
sudo chmod a+x /opt/vdl/status.py
sudo cp ./init.d/vdl_status /etc/init.d/vdl_status

echo "Starting VDL Server."
{
sudo update-rc.d vdl defaults
} ||{
sudo chkconfig --add vdl
}
sudo service vdl start

echo "Starting VDL Status Server."
{
sudo update-rc.d vdl_status defaults
} ||{
sudo chkconfig --add vdl_status
}
sudo service vdl_status start

exit 0
