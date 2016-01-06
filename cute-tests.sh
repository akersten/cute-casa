#!/bin/sh

echo "-------------------------"
echo "Running CuteCasa tests..."
echo "-------------------------"
echo -e "\n"

export CUTECASA_TEST=1

python3 cute-tests.py

if [ $? -eq 0 ]
then
    echo "CuteCasa tests pass."
else
    echo -e "\n" >&2
    echo "----------------------" >&2
    echo "Cutecasa tests failed!" >&2
    echo "----------------------" >&2
fi
