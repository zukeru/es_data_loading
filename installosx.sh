#!/bin/bash

sudo mkdir /opt/vdl
sudo cp ./logging.ini /opt/vdl/logging.ini
sudo chmod a+x /opt/vdl/logging.ini
sudo cp ./logging.ini /opt/vdl/status-logging.ini
sudo chmod a+x /opt/vdl/status-logging.ini
sudo cp ./vdl.py /opt/vdl/vdl.py
sudo chmod a+x /opt/vdl/vdl.py
sudo cp ./status.py /opt/vdl/status.py
sudo chmod a+x /opt/vdl/status.py
sudo cp ./LaunchDaemons/vdl.plist /Library/LaunchDaemons/vdl.plist
sudo chmod a+x /Library/LaunchDaemons/vdl.plist
sudo cp ./LaunchDaemons/vdl_status.plist /Library/LaunchDaemons/vdl_status.plist
sudo chmod a+x /Library/LaunchDaemons/vdl_status.plist

echo "Starting VDL Server."
sudo launchctl load -w /Library/LaunchDaemons/vdl.plist

echo "Starting VDL Status Server."
sudo launchctl load -w /Library/LaunchDaemons/vdl_status.plist

exit 0
