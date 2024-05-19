#!/bin/bash

#run test with coverage
pytest --cov-report xml --cov=./ -n 4

# if tests passed, run app


if [  $? -eq 0 ]; then
    python main.py
fi