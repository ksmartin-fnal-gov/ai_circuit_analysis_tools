#!/usr/bin/env python3
"""
Parse .BomDoc file and extract Manufacturer Part Number and Datasheet Link pairs.
Outputs to mpn_datasheet_pairs.csv in the same directory as the input file.
"""

import sys
import os
import re

def clean_value(val):
    # Strip exactly one leading and one trailing double quote if they exist
    if val.startswith('"') and val.endswith('"'):
        val = val[1:-1]

    val = val.replace('(', '_').replace(')', '_').replace(',', '_')

    return val

def parse_bomdoc(bomdoc_path):
    """Parse .BomDoc file and extract MPN and Datasheet Link pairs."""
    pairs = []
    
    with open(bomdoc_path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            # Only process lines that start with |RECORD=CatalogItem|
            if not line.startswith('|RECORD=CatalogItem|'):
                continue
            
            # Find all quoted key-value pairs
            # Pattern matches "Key=Value" where Value can contain various characters
            pairs_in_line = re.findall(r'"([^"=]+)=([^"]*)"|([^"=,\s]+)=([^",\s]*)', line) 
            
            # Extract Manufacturer Part Number and Datasheet Link
            mpn = None
            datasheet_link = None
            
            for m in pairs_in_line:
                # Handle both "Manufacturer Part Number" and "Manufacturer Part Number 1" formats
                if m[0].startswith("Manufacturer Part Number"):
                    mpn = clean_value(m[1])
                    print(f"Found MPN1: {mpn}")
                elif m[2].startswith("Manufacturer Part Number"):
                    mpn = clean_value(m[3])
                    print(f"Found MPN2: {mpn}")
                elif m[0] == "Datasheet Link":
                    datasheet_link = clean_value(m[1])
                    print(f"Found Datasheet Link1: {datasheet_link}")
                elif m[2] == "Datasheet Link":
                    datasheet_link = clean_value(m[3])
                    print(f"Found Datasheet Link2: {datasheet_link}")
            
            # Only add if we have both values (or at least MPN)
            if mpn and datasheet_link:
                pairs.append((mpn, datasheet_link))
    
    return pairs


def write_csv(pairs, output_path):
    """Write MPN and Datasheet Link pairs to CSV file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        # Write header
        f.write("Manufacturer Part Number,Datasheet Link\n")
        
        # Write pairs
        for mpn, datasheet_link in pairs:
            # Escape commas and quotes in values for CSV
            mpn_escaped = mpn.replace('"', '""')
            datasheet_link_escaped = datasheet_link.replace('"', '""')
            
            # Quote fields if they contain commas, quotes, or newlines
            if ',' in mpn_escaped or '"' in mpn_escaped or '\n' in mpn_escaped:
                mpn_formatted = f'"{mpn_escaped}"'
            else:
                mpn_formatted = mpn_escaped
            
            if ',' in datasheet_link_escaped or '"' in datasheet_link_escaped or '\n' in datasheet_link_escaped:
                datasheet_formatted = f'"{datasheet_link_escaped}"'
            else:
                datasheet_formatted = datasheet_link_escaped
            
            f.write(f"{mpn_formatted},{datasheet_formatted}\n")


def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_mpn_datasheet.py <path_to_bomdoc>")
        sys.exit(1)
    
    bomdoc_path = sys.argv[1]
    
    if not os.path.exists(bomdoc_path):
        print(f"Error: File '{bomdoc_path}' not found.")
        sys.exit(1)
    
    if not bomdoc_path.lower().endswith('.bomdoc'):
        print(f"Warning: File '{bomdoc_path}' does not have .BomDoc extension.")
    
    # Parse the .BomDoc file
    pairs = parse_bomdoc(bomdoc_path)
    
    if not pairs:
        print("No CatalogItem records found or no MPN/Datasheet pairs extracted.")
        sys.exit(0)
    
    # Determine output path
    output_dir = os.path.dirname(bomdoc_path)
    output_path = os.path.join(output_dir, "mpn_datasheet_pairs.csv")
    
    # Write to CSV
    write_csv(pairs, output_path)
    
    print(f"Extracted {len(pairs)} MPN/Datasheet pairs to: {output_path}")


if __name__ == "__main__":
    main()
