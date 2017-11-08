#!/bin/bash

if [ $1 == "aws1" ]; then
    ssh -i demo.pem ubuntu@52.91.61.147
elif [ $1 == "aws2" ]; then
    ssh -i demo.pem ubuntu@54.80.33.179
elif [ $1 == "aws3" ]; then
    ssh -i demo.pem ubuntu@184.73.149.187
else
    echo "invalid aws instance"
    exit 1
fi

exit 0
