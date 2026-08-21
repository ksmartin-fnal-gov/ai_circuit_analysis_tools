import urllib.request
import os
import csv
import time
import sys

# Get paths from command line arguments or use defaults
if len(sys.argv) >= 3:
    csv_path = sys.argv[1]
    datasheet_dir = sys.argv[2]
else:
    csv_path = 'mpn_datasheet_pairs.csv'
    datasheet_dir = 'datasheets'

os.makedirs(datasheet_dir, exist_ok=True)
reader = csv.DictReader(open(csv_path))
count = 0
failed = []
success = []

for row in reader:
    mpn = row['Manufacturer Part Number']
    url = row['Datasheet Link']
    # Sanitize filename by replacing problematic characters
    safe_mpn = mpn.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    print(f'Downloading {mpn}...')
    if url:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                with open(f'{datasheet_dir}/{safe_mpn}.pdf', 'wb') as f:
                    f.write(response.read())
            print(f'  Success')
            success.append(mpn)
            time.sleep(0.5)  # Be polite to servers
        except Exception as e:
            print(f'  Failed: {e}')
            failed.append((mpn, str(e)))
    else:
        print(f'  No URL')
        failed.append((mpn, "No URL"))

print(f'\nSuccess: {len(success)}, Failed: {len(failed)}')
for f in failed:
    print(f'  {f[0]}: {f[1]}')
