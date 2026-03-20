#!/bin/sh

if [ "$DB_HOST" != "" ]
then
    echo "Waiting for database ($DB_HOST)..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "Database started"
fi

# Run migrations
python manage.py collectstatic --no-input
python manage.py migrate

exec "$@"
