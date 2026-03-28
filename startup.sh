#!/bin/bash
gunicorn --bind=0.0.0.0:8000 --workers=2 --threads=4 app:app
