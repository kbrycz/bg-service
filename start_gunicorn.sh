#!/bin/bash
# "start_gunicorn.sh"
cd /home/ec2-user/bg-service
source venv/bin/activate
exec gunicorn main:app -b 0.0.0.0:5000