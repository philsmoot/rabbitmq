#! /bin/bash
python3 /Users/phil.smoot/CZII/GitHub/rabbitmq/msg_jobstep_started.py "02_tomo_recon_mpi.sh"
python3 /Users/phil.smoot/CZII/GitHub/rabbitmq/msg_jobstep_done.py "02_tomo_recon_mpi.sh"