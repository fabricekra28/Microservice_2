#!/bin/sh

echo "Waiting for backend services..."

# On attend que users_service soit joignable
while ! nc -z user 8008; do
  echo "Waiting for users_service..."
  sleep 2
done

# On attend que products_service soit joignable
while ! nc -z maison 8005; do
  echo "Waiting for maison..."
  sleep 2
done

# On attend que orders_service soit joignable
while ! nc -z location 8006; do
  echo "Waiting for location_service..."
  sleep 2
done

echo "All backend services are up - starting gateway"

exec "$@"
