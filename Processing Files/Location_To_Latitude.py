import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import re

address = pd.read_csv('club_addresses_and_ids.csv')

# Initialize geolocator
geolocator = Nominatim(user_agent="your_app_name")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

def clean_address(addr):
    addr = str(addr).strip()
    addr = addr.replace('\n', ', ')
    addr = addr.replace('  ', ' ')
    addr = addr.replace(', ,', ',')  # clean double commas
    return addr

address['Full_Address'] = address['Full_Address'].str.strip()
address['Full_Address'] = address['Full_Address'].apply(clean_address)

# Apply geocoding
address['location'] = address['Full_Address'].apply(geocode)
address['latitude'] = address['location'].apply(lambda loc: loc.latitude if loc else None)
address['longitude'] = address['location'].apply(lambda loc: loc.longitude if loc else None)

patterns_to_remove = [
    r'\bSuite\s*\d+[A-Za-z]*',         # Suite 101 or Suite 200A
    r'\bSte\.?\s*\d+[A-Za-z]*',        # Ste. 101 or Ste 300B
    r'\bFloor\s*\d+',                  # Floor 4
    r'\bFl\.?\s*\d+',                  # Fl. 4
    r'\b4th Floor\b',                  # 4th Floor, etc.
    r'\b[1-9][0-9]{0,1}(st|nd|rd|th)\s+Floor',  # "1st Floor", "2nd Floor", etc.
]

# Combine all patterns into a single regex
combined_pattern = '|'.join(patterns_to_remove)

# Remove the matches
address['Full_Address'] = address['Full_Address'].str.replace(combined_pattern, '', flags=re.IGNORECASE, regex=True)


def clean_address(addr):
    addr = str(addr).strip()
    addr = addr.replace('\n', ', ')
    addr = addr.replace('  ', ' ')
    addr = addr.replace(', ,', ',')  # clean double commas
    return addr

address['Full_Address'] = address['Full_Address'].str.strip()
address['Full_Address'] = address['Full_Address'].apply(clean_address)

actual_address = address.loc[~address['latitude'].isna()]

del actual_address['Full_Address'], actual_address['location']

actual_address.to_csv('partial_addresses_lat_lon.csv', index=False)

other_address = address.loc[address['latitude'].isna()]

# Assuming your DataFrame is named df and has a column "Full_Address"
def clean_full_address(addr):
    if pd.isna(addr):
        return addr

    # Handle Canadian case (e.g., V6B 5C6 Vancouver, British Columbia, Canada)
    if "Canada" in addr:
        return addr.strip()

    # General cleanup
    addr = re.sub(r'\s{2,}', ' ', addr)  # remove double spaces
    addr = addr.strip()

    # Find patterns like "X 12345ityname"
    match = re.search(r'([A-Z]) (\d{5})([a-zA-Z]+)', addr)
    if match:
        state_initial = match.group(1)
        zipcode = match.group(2)
        city_tail = match.group(3)

        # Replace broken segment with proper ", City, ST ZIP"
        broken = f"{state_initial} {zipcode}{city_tail}"
        city_name = city_tail.capitalize()
        new_segment = f"{city_name}, {state_initial}{zipcode}"
        addr = addr.replace(broken, new_segment)

    # Fix missing commas between city/state/ZIP
    addr = re.sub(r'([a-zA-Z]), ([A-Z]{2})(\d{5})', r'\1, \2 \3', addr)

    return addr

other_address["Full_Address"] = other_address["Full_Address"].apply(clean_full_address)

other_address['location'] = other_address['Full_Address'].apply(geocode)
other_address['latitude'] = other_address['location'].apply(lambda loc: loc.latitude if loc else None)
other_address['longitude'] = other_address['location'].apply(lambda loc: loc.longitude if loc else None)

# I got these addresses manually in a google sheet with some help from the function above
other_address = pd.read_csv('partial_addresses_lat_lon_2.csv')
del other_address['Full_Address'], other_address['location']

final_address = pd.concat([other_address, actual_address], ignore_index=True)

final_address.to_csv('address_lat_lon.csv', index=False)