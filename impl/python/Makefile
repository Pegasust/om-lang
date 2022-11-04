test: pickle.pickle parser.py scanner.py bindings.py testerator.py symbols.py typecheck.py offsets.py
	rm -rf test_output/*
	python3 testerator.py run pickle.pickle --verbose
	./test_diff.sh

to_vm_test:

.PHONY: to_vm_test test

