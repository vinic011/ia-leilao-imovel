import json
import sys

with open('config.json', 'r') as f:
    vars = json.load(f)
print(vars, file=sys.stderr)  # Log para stderr para não poluir stdout