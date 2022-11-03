#!/usr/bin/env sh
ls ../../examples/omega | grep -o .*\.omega | while read input; do  
    echo "Input: ${input}"
    python3 main.py --file ../../examples/omega/${input}
done
