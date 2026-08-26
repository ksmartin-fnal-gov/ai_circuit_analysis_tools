import urllib.request
import os
import csv
import time
import sys
import subprocess
from urllib.parse import urlparse

# Get paths from command line arguments or use defaults
if len(sys.argv) >= 3:
    csv_path = sys.argv[1]
    datasheet_dir = sys.argv[2]
else:
    csv_path = 'mpn_datasheet_pairs.csv'
    datasheet_dir = 'datasheets'

os.makedirs(datasheet_dir, exist_ok=True)
reader = csv.DictReader(open(csv_path, mode='r', encoding='utf-8-sig'))
count = 0
failed = []
success = []

for row in reader:
    mpn = row['Manufacturer Part Number']
    url = row['Datasheet Link']
    # Sanitize filename by replacing problematic characters
    safe_mpn = mpn.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    if url:
        output_path = f"{datasheet_dir}/{safe_mpn}.pdf"
    
        # Automatically get the root domain for the referer header
        parsed_url = urlparse(url)
        root_domain = f"{parsed_url.scheme}://{parsed_url.netloc}/"

        print(f"Downloading {safe_mpn}...")

        # Build a simple command line execution list
        curl_command = [
            "curl",
            "-4",                      # Strictly force IPv4
            "-L",                      # Automatically follow 301/302 redirects
            "--http1.1",               # FIX: Forces HTTP/1.1 to prevent stream error 92
            "--connect-timeout", "10", # STOP trying to connect if server stalls for 10 seconds
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", 
            "--referer", root_domain,  # Tells the server you found the link on their site
            "-o", output_path,         # Save file to this location
            url
        ]

        try:
            # Run the system curl command cleanly from Python
            subprocess.run(curl_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Strict Safety Check: Make sure it's not a tiny HTML text file disguised as a PDF
            if os.path.exists(output_path):
                file_size_kb = os.path.getsize(output_path) / 1024
                if file_size_kb < 100: # Most real circuit datasheets are at least 100KB+
                    print(f"⚠️ Warning: Saved file for {safe_mpn} is too small ({file_size_kb:.1f} KB). Likely trapped by an HTML wall.")
                    os.remove(output_path) # Wipe out the junk HTML file
                else:
                    print(f"✅ Successfully saved real PDF: {safe_mpn}.pdf ({file_size_kb:.1f} KB)")
                    success.append(mpn)
                    time.sleep(0.5)  # Be polite to servers
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to download {safe_mpn} using system curl. Error: {e}")
            failed.append((mpn, str(e)))
    else:
        print(f'  No URL')
        failed.append((mpn, "No URL"))

print(f'\nSuccess: {len(success)}, Failed: {len(failed)}')
for f in failed:
    print(f'  {f[0]}: {f[1]}')
