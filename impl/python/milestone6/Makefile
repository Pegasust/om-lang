ms5: ../milestone5/parser.py ../milestone5/scanner.py ../milestone5/bindings.py
	cp $? ./

test: pickle.pickle parser.py scanner.py bindings.py testerator.py symbols.py typecheck.py
	python3 testerator.py run --input pickle.pickle --verbose

