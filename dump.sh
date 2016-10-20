#!/bin/bash

rm -f dump.bin
gdb --pid $1 -batch -x dump.txt
