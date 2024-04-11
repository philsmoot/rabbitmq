#! /bin/bash
python3 /Users/phil.smoot/CZII/GitHub/rabbitmq/msg_jobstep_started.py "01_motioncorr_mpi.sh"
python3 /Users/phil.smoot/CZII/GitHub/rabbitmq/msg_jobstep_done.py "01_motioncorr_mpi.sh"
