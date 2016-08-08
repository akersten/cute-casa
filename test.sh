#!/bin/sh

clear
rm secret/test*

echo "-------------------------"
echo "Running CuteCasa tests..."
echo "-------------------------"
echo -e "\n"

export CUTECASA_TEST=1

# Name your tests following the convention test_xyz.py and the test discovery module will find them.
python3 -m unittest discover

if [ $? -eq 0 ]
then
    echo "--------------------"
    echo "CuteCasa tests pass."
    echo "--------------------"
else
    echo -e "\n" >&2
    echo "----------------------" >&2
    echo "Cutecasa tests failed!" >&2
    echo "----------------------" >&2
fi
