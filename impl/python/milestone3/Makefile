parser.py: omega.gram rdgen/emit.py
	python3.11 rdgen/main.py create --input $< --output $@
test: tester.py parser.py correct.json incorrect.json
	python3.11 tester.py --correct correct.json --incorrect incorrect.json
interactive: scanner.py
	python3.11 scanner.py

