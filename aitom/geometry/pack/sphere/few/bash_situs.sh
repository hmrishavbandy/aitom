#!/bin/bash

wget http://situs.biomachina.org/disseminate/Situs_3.1.tar.gz
gunzip Situs_3.1.tar.gz
tar xvf Situs_3.1.tar
cd Situs_3.1/src
make
make install
make clean
cd ..
ls bin
