parser.py: omega.ebnf 
	python3 rdgen/main.py create --input $< --output $@
test-short: tester.py parser.py short.json
	python3 tester.py --correct short.json
test: tester.py parser.py correct.json incorrect.json
	python3 tester.py --correct correct.json --incorrect incorrect.json
interactive: scanner.py
	python3 scanner.py

