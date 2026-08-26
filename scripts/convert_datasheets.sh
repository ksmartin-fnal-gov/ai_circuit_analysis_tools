#!/bin/bash

# Convert downloaded PDF datasheets to HTML using pdftohtml
# Usage: ./convert_datasheets.sh

DATASHEETS_DIR="$PWD/datasheets"

if [ ! -d "$DATASHEETS_DIR" ]; then
    echo "Error: datasheets directory not found at $DATASHEETS_DIR"
    exit 1
fi

# Check if pdftohtml is installed
if ! command -v pdftohtml &> /dev/null; then
    echo "Error: pdftohtml is not installed"
    exit 1
fi

echo "Converting PDF datasheets to HTML..."
echo "Processing directory: $DATASHEETS_DIR"
echo ""

# Process each PDF file
for pdf_file in "$DATASHEETS_DIR"/*.pdf; do
    if [ -f "$pdf_file" ]; then
        # Get the filename without path and extension
        filename=$(basename "$pdf_file")
        basename_no_ext="${filename%.pdf}"
        
        # Create subdirectory with the same name as the PDF (without extension)
        output_dir="$DATASHEETS_DIR/$basename_no_ext"
        mkdir -p "$output_dir"
        
        # Output HTML file path
        html_file="$output_dir/${basename_no_ext}.html"
        
        echo "Converting: $filename -> $html_file"
        
        # Run pdftohtml with specified parameters
        # -i: convert images
        # -q: quiet mode
        # -noframes: no frames
        if pdftohtml -i -q -noframes "$pdf_file" "$html_file"; then
#        if pdftohtml -i -noframes "$pdf_file" "$html_file"; then
            echo "  Success"
        else
            echo "  Failed"
        fi
    else
        echo "No PDF files found in $DATASHEETS_DIR"
        break
    fi
done

echo ""
echo "Conversion complete!"
