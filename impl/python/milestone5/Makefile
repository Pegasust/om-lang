test: test_bindings.pickle parser.py scanner.py bindings.py
	python3 testerator.py run --input test_bindings.pickle

grader: test toy_pickle.pickle
	python3 testerator.py run --input toy_pickle.pickle

db_test: test_bindings.pickle parser.py scanner.py bindings.py
	python3 -m pdb testerator.py run --input test_bindings.pickle

