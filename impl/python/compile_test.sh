#!/usr/bin/env sh
SUBDIR=${1:-"../../examples/omega"}
touch test_output/compile_test.out
touch test_output/compile_test.err

echo "=====================">> test_output/compile_test.out
echo "=====================">> test_output/compile_test.err

date >> test_output/compile_test.out
date >> test_output/compile_test.err

find "${SUBDIR}" | grep -o ".*\.omega" | while read input; do  
    echo "Input: ${input}, output: ${input}.vm" |\
        tee test_output/compile_test.out | tee test_output/compile_test.err
    python3 main.py --file ${input} --output ${input}.vm --run \
        >>test_output/compile_test.out 2>>test_output/compile_test.err
    echo "Exit: $?"
done
