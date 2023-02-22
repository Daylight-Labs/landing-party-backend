#!/usr/bin/env bash
set -eou pipefail

if [ "$ENVIRONMENT" == "dev" ] ; then
    python manage.py collectstatic --no-input
    python manage.py migrate
else
    echo "running migrations"
    python manage.py migrate
fi

# From gunicorn docs (https://docs.gunicorn.org/en/stable/design.html#how-many-workers):
#
#   Generally we recommend (2 x $num_cores) + 1 as the number of workers to start off with.
#   While not overly scientific, the formula is based on the assumption that for a given
#   core, one worker will be reading or writing from the socket while the other worker is
#   processing a request.
#
#   DO NOT scale the number of workers to the number of clients you expect to have.
#   Gunicorn should only need 4-12 worker processes to handle hundreds or thousands of
#   requests per second.
#
#   Always remember, there is such a thing as too many workers. After a point your
#   worker processes will start thrashing system resources decreasing the throughput of
#   the entire system.
CPU_COUNT=$(grep -c ^processor /proc/cpuinfo)
WORKER_COUNT=$(( 2*$CPU_COUNT + 1 ))
echo "Starting django with $WORKER_COUNT workers"

gunicorn api.wsgi:application \
    --bind :8000 \
    --workers $WORKER_COUNT \
    --log-level=info
