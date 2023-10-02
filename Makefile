# Makefile for OoO_original.py
.PHONY: run 

# Define the `run` target to run the Python program with the specified input file using Python 3
run:
	python3 OoO_original.py $(arg)

clean:
	rm -f *.pyc
	rm -f out.txt


