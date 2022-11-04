#!/usr/bin/env sh
SUBDIR=${1:-"../../examples/omega"}
touch test_output/compile_test.out
touch test_output/compile_test.err

echo "=====================">> test_output/compile_test.out
echo "=====================">> test_output/compile_test.err

date >> test_output/compile_test.out
date >> test_output/compile_test.err

find "${SUBDIR}" | grep -o ".*\.omega" | sort | while read input; do  
    NAVI="Input: ${input}, output: ${input}.vm" 
    echo $NAVI
    echo $NAVI >>test_output/compile_test.out 
    echo $NAVI >>test_output/compile_test.err
    python3 main.py --file ${input} --output ${input}.vm --run \
        >>test_output/compile_test.out 2>>test_output/compile_test.err
    echo "Exit: $?"
done
