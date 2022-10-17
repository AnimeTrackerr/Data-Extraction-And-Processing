import jsondiff as jd

f1 = [
    {'a': 1, 'l': [1, 2, 3]},
    {'a': 2, 'l': [2, 3]},
    {'a': 3, 'l': [1, 3]},
    {'a': 4, 'l': [2, 3]},
    {'a': 5, 'l': [1, 2, 3]},
    {'a': 8, 'l': [1, 2, 3]}
]

f2 = [
    {'a': 2, 'l': [2, 3]},
    {'a': 3, 'l': [1, 3]},
    {'a': 4, 'l': [2, 3]},
    {'a': 5, 'l': [1, 2, 4]},
    {'a': 6, 'l': [5, 6]},
    {'a': 7, 'l': [5, 6]}
]

print(f1)

diff = jd.diff(f1, f2, syntax='explicit')

for key in diff:
    print(f'{key}: {diff[key]}\n')
