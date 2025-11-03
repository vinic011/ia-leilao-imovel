import json

with open('config.json', 'r') as f:
    vars = json.load(f)
print(vars)