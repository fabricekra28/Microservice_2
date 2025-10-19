#!/bin/sh
echo "Waiting for PostgreSQL..."
while ! nc -z db.microservices-app2.svc.cluster.local 5432; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "PostgreSQL is up - starting User Service"
exec "$@" 
