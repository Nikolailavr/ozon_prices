#!/usr/bin/env bash

set -e

echo "Запуск виртуального дисплея Xvfb..."
Xvfb :99 -screen 0 1920x1080x24 &

echo "Запуск оконного менеджера fluxbox..."
fluxbox &

echo "Запуск VNC-сервера..."
x11vnc -display :99 -forever -passwd 123456 -shared -nopw &

echo "Ожидание запуска Xvfb и VNC..."
sleep 5

echo "Запуск Celery worker..."
exec celery -A apps.celery.celery_app worker -Q parser --pool=threads --loglevel=info -c 1
