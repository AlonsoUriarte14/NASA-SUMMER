#!/bin/bash


# enable i2c on le potato on pin 3 and 5
ls -al /dev/i2c-*
sudo ldto enable i2c-ao
ls -al /dev/i2c-*

sudo chmod +x enablei2c.sh

pip3 install matplotlib

git pull

