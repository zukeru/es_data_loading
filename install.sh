#!/bin/bash
sudo mkdir /opt/vdl
sudo cp ./init.d/vdl /etc/init.d/vdl
sudo cp ./logging.ini /opt/vdl/logging.ini
sudo chmod a+x /opt/vdl/logging.ini
sudo chmod a+x /etc/init.d/vdl
sudo cp ./vdl.py /opt/vdl/vdl.py
sudo chmod a+x /opt/vdl/vdl.py
sudo cp ./status.py /opt/vdl/status.py
sudo chmod a+x /opt/vdl/status.py
sudo cp ./init.d/vdl_status /etc/init.d/vdl_status
sudo chmod a+x /etc/init.d/vdl_status

sudo wget http://apache.arvixe.com//kafka/0.8.2.1/kafka_2.9.1-0.8.2.1.tgz
sudo tar -xvf kafka_2.9.1-0.8.2.1.tgz
sudo mkdir /opt/vdl/kafka
sudo cp -r kafka_2.9.1-0.8.2.1/* /opt/vdl/kafka/
sudo chmod a+x /opt/vdl/kafka/bin/kafka-topics.sh


echo "Starting VDL Server."
{
sudo update-rc.d vdl defaults
} ||{
sudo chkconfig --add vdl
sudo chkconfig vdl on
}
sudo service vdl start

echo "Starting VDL Status Server."
{
sudo update-rc.d vdl_status defaults
} ||{
sudo chkconfig --add vdl_status
sudo chkconfig vdl_stats on
}
sudo service vdl_status start

exit 0
