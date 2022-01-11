#!/bin/bash

cd /home/alex/Bureau/findmyalex

npm run build
scp -r /home/alex/Bureau/findmyalex/public pi@192.168.2.2:/home/pi
