import sys

# read from transform.txt
with open('transform_adjust.txt', 'r') as f:
    text = f.read()

# split lines
lines = text.strip().splitlines()

# prepare result
result = []

# process each line
for line in lines:
    if line.startswith('<') and line.endswith('>'):
        # remove < and >
        content = line[1:-1]
        parts = content.split(',')
        if len(parts) >= 3:
            last = parts[-1].strip()
            result.append(last)

# join as comma separated row
output = ",".join(result)
print(output)

