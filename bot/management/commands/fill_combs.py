from bot.models import Combinations
from pprint import pprint

strings = ['Bar', 'Grape', 'Lemon', 'Seven']
combinations = []
comb = None

for i in range(len(strings)):
    for j in range(len(strings)):
        for k in range(len(strings)):
            comb = f'{strings[k]}, {strings[j]}, {strings[i]}'
            combinations.append({'id': len(combinations) + 1, 'comb': comb, 'mult': 0.00})
            if comb == 'Seven, Seven, Seven':
                break
        if comb == 'Seven, Seven, Seven':
            break
    if comb == 'Seven, Seven, Seven':
        break

for combination in combinations:
    c = Combinations.objects.create(
        id=combination['id'],
        comb=combination['comb'],
        mult=combination['mult'],
    )
    pprint(f'Added: {c}')
