#!/bin/bash
# filepath: ./stop.sh
# Stops Flask and Huey services started by start.sh (Linux version)
kill "$(< app-pid)"
kill "$(< huey-pid)"
rm app-pid
rm huey-pid

