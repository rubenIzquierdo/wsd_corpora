#!/bin/bash

this_folder=$(pwd)

mkdir resources
cd resources

#For the mappings between wn versions
wget -O mappings.tgz http://nlp.lsi.upc.edu/tools/download-map.php
tar xzf mappings.tgz
mv mappings-upc-2007/ mappings-upc
rm mappings.tgz
cd ..

