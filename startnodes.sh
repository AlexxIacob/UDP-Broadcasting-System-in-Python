#!/bin/bash
# Exemple:   ./startnodes.sh config.txt 0 4


if [ "$#" -ne 3 ]; then
    echo "Utilizare: ./startnodes.sh config.txt primul_index ultimul_index"
    echo "Exemplu:   ./startnodes.sh config.txt 0 4"
    exit 1
fi

CONFIG=$1
FIRST=$2
LAST=$3

echo "Pornesc nodurile $FIRST pana la $LAST cu config: $CONFIG"


for ((i=FIRST; i<=LAST; i++)); do
    echo "Pornesc nodul $i..."
    python3 bcastnode.py $CONFIG $i &
done

echo "Toate nodurile au fost pornite!"
echo "Nodurile vor astepta 30 secunde inainte de a incepe broadcasting-ul."

wait
echo "Toate nodurile au terminat."