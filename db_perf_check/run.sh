#!/usr/bin/env bash

OP_TYPE=$1
DB_TYPE=$2
NUM_OF_PROCS=$3
if [ -z "$OP_TYPE" ]; then
    echo "Usage: $0 <op_type> <db_type> <num_of_procs>"
    exit 1
fi
if [ -z "$DB_TYPE" ]; then
    echo "Usage: $0 <op_type> <db_type> <num_of_procs>"
    exit 1
fi
if [ -z "$NUM_OF_PROCS" ]; then
    echo "Usage: $0 <op_type> <db_type> <num_of_procs>"
    exit 1
fi

run_proc () {
    python src/db_perf_check/${OP_TYPE}_data.py ${DB_TYPE} forever
}

pids=''

for i in `seq 1 ${NUM_OF_PROCS}`; do
   run_proc &
   pids="$pids $!"
done

wait $pids
