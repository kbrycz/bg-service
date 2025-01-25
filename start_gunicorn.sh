#!/bin/bash
cd /home/ec2-user/bg-service
source venv/bin/activate

# Single worker, single thread, to reduce memory usage
exec gunicorn main:app -b 0.0.0.0:5000 --workers=1 --threads=1