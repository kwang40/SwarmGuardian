#!/bin/bash

if [ $1 == "aws1" ]; then
    ssh -i demo.pem ubuntu@52.91.61.147
elif [ $1 == "aws2" ]; then
    ssh -i demo.pem ubuntu@54.80.33.179
elif [ $1 == "aws3" ]; then
    ssh -i demo.pem ubuntu@184.73.149.187
elif [ $1 == "aws4" ]; then
    ssh -i demo.pem ubuntu@34.205.129.96
elif [ $1 == "aws5" ]; then
    ssh -i demo.pem ubuntu@54.166.208.38
elif [ $1 == "aws6" ]; then
    ssh -i demo.pem ubuntu@54.173.198.30
elif [ $1 == "aws7" ]; then
    ssh -i demo.pem ubuntu@174.129.141.218
else
    echo "invalid aws instance"
    exit 1
fi

exit 0
