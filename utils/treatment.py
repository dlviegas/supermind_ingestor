import re
import pandas as pd


def number_treat(string):
    if not string or pd.isnull(string):
        return None
    print('String não é nula')
    number_match = re.search(r'\((\d+)\)\s+(\d+)', string)

    if number_match:
        print('Bateu no primeiro match')
        ddd = number_match.group(1)
        number = number_match.group(2)

        if len(number) == 8 and not number.startswith('3'):
            number = f'9{number.strip()}'

            return int(f'{ddd}{number}')
        elif len(number) == 7:
            number = f'3{number.strip()}'

            return int(f'{ddd}{number}')
        else:
            return int(f'{ddd}{number}')

    return None