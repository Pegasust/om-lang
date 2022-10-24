parser.py: omega.gram 
	python3 rdgen/main.py create --input $< --output $@
test-short: tester.py parser.py short.json
	python3 tester.py --correct short.json
test: tester.py parser.py correct.json incorrect.json
	python3 tester.py --correct correct.json --incorrect incorrect.json
test-ast: ast_tests.py parser.py
	python3 ast_tests.py
interactive: scanner.py
	python3 scanner.py

