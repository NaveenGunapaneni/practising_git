#!/usr/bin/env python3
"""
PDF Generator for User Documentation
Converts User_Documentation.md to a professional PDF with styling
"""

import markdown
import weasyprint
from pathlib import Path
import re
from datetime import datetime

def create_pdf_from_markdown(md_file_path, output_pdf_path):
    """Convert markdown file to PDF with professional styling"""
    
    # Read the markdown file
    with open(md_file_path, 'r', encoding='utf-8') as file:
        md_content = file.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'codehilite'])
    
    # Create complete HTML document with CSS styling
    html_document = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GeoPulse User Documentation</title>
        <style>
            @page {{
                size: A4;
                margin: 2cm;
                @top-center {{
                    content: "GeoPulse User Documentation";
                    font-size: 10pt;
                    color: #666;
                }}
                @bottom-center {{
                    content: "Page " counter(page) " of " counter(pages);
                    font-size: 10pt;
                    color: #666;
                }}
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
            }}
            
            h1 {{
                color: #2c3e50;
                font-size: 28pt;
                font-weight: bold;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
                margin-top: 30px;
                margin-bottom: 20px;
                page-break-after: avoid;
            }}
            
            h2 {{
                color: #34495e;
                font-size: 20pt;
                font-weight: bold;
                margin-top: 25px;
                margin-bottom: 15px;
                page-break-after: avoid;
                border-left: 4px solid #3498db;
                padding-left: 15px;
            }}
            
            h3 {{
                color: #2c3e50;
                font-size: 16pt;
                font-weight: bold;
                margin-top: 20px;
                margin-bottom: 10px;
                page-break-after: avoid;
            }}
            
            h4 {{
                color: #34495e;
                font-size: 14pt;
                font-weight: bold;
                margin-top: 15px;
                margin-bottom: 8px;
                page-break-after: avoid;
            }}
            
            p {{
                margin-bottom: 12px;
                text-align: justify;
            }}
            
            ul, ol {{
                margin-bottom: 15px;
                padding-left: 25px;
            }}
            
            li {{
                margin-bottom: 5px;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                font-size: 11pt;
                page-break-inside: avoid;
            }}
            
            th {{
                background-color: #3498db;
                color: white;
                padding: 12px 8px;
                text-align: left;
                font-weight: bold;
                border: 1px solid #2980b9;
            }}
            
            td {{
                padding: 10px 8px;
                border: 1px solid #ddd;
                vertical-align: top;
            }}
            
            tr:nth-child(even) {{
                background-color: #f8f9fa;
            }}
            
            code {{
                background-color: #f4f4f4;
                padding: 2px 4px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
            }}
            
            pre {{
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 5px;
                padding: 15px;
                overflow-x: auto;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
                margin: 15px 0;
                page-break-inside: avoid;
            }}
            
            blockquote {{
                border-left: 4px solid #3498db;
                margin: 20px 0;
                padding: 10px 20px;
                background-color: #f8f9fa;
                font-style: italic;
            }}
            
            .toc {{
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 5px;
                padding: 20px;
                margin: 20px 0;
                page-break-inside: avoid;
            }}
            
            .toc h2 {{
                border: none;
                padding-left: 0;
                margin-top: 0;
            }}
            
            .toc ul {{
                list-style-type: none;
                padding-left: 0;
            }}
            
            .toc li {{
                margin-bottom: 8px;
            }}
            
            .toc a {{
                color: #3498db;
                text-decoration: none;
            }}
            
            .highlight {{
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 3px;
                padding: 10px;
                margin: 15px 0;
            }}
            
            .warning {{
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                border-radius: 3px;
                padding: 10px;
                margin: 15px 0;
            }}
            
            .success {{
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 3px;
                padding: 10px;
                margin: 15px 0;
            }}
            
            .info {{
                background-color: #d1ecf1;
                border: 1px solid #bee5eb;
                border-radius: 3px;
                padding: 10px;
                margin: 15px 0;
            }}
            
            .step {{
                background-color: #e8f4fd;
                border-left: 4px solid #3498db;
                padding: 15px;
                margin: 15px 0;
            }}
            
            .step-number {{
                font-weight: bold;
                color: #3498db;
            }}
            
            .file-format {{
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 15px;
                margin: 15px 0;
            }}
            
            .file-format h4 {{
                margin-top: 0;
                color: #495057;
            }}
            
            .demo-features {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }}
            
            .demo-features h3 {{
                color: white;
                margin-top: 0;
            }}
            
            .demo-features ul {{
                color: white;
            }}
            
            .footer {{
                text-align: center;
                font-size: 10pt;
                color: #666;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
            }}
            
            /* Page breaks */
            h1, h2, h3 {{
                page-break-after: avoid;
            }}
            
            table, pre, .toc {{
                page-break-inside: avoid;
            }}
            
            /* Links */
            a {{
                color: #3498db;
                text-decoration: none;
            }}
            
            /* Images */
            img {{
                max-width: 100%;
                height: auto;
                display: block;
                margin: 15px auto;
            }}
            
            /* Special formatting for specific sections */
            .getting-started {{
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
            }}
            
            .troubleshooting {{
                background-color: #fff3cd;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
            }}
            
            .faq {{
                background-color: #e8f4fd;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        {html_content}
        
        <div class="footer">
            <p><strong>GeoPulse User Documentation</strong></p>
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p>Version: 2.0 - Final Demo Version</p>
        </div>
    </body>
    </html>
    """
    
    # Convert HTML to PDF
    print(f"Converting {md_file_path} to PDF...")
    weasyprint.HTML(string=html_document).write_pdf(output_pdf_path)
    print(f"PDF created successfully: {output_pdf_path}")

def main():
    """Main function to create PDF from User Documentation"""
    
    # File paths
    md_file = "User_Documentation.md"
    output_pdf = "GeoPulse_User_Documentation.pdf"
    
    # Check if markdown file exists
    if not Path(md_file).exists():
        print(f"Error: {md_file} not found!")
        return
    
    try:
        # Create PDF
        create_pdf_from_markdown(md_file, output_pdf)
        print(f"\n✅ Successfully created PDF: {output_pdf}")
        print(f"📄 File size: {Path(output_pdf).stat().st_size / 1024:.1f} KB")
        print(f"📁 Location: {Path(output_pdf).absolute()}")
        
    except Exception as e:
        print(f"❌ Error creating PDF: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure you have weasyprint installed: pip install weasyprint")
        print("2. On macOS, you might need: brew install cairo pango gdk-pixbuf libffi")
        print("3. On Ubuntu/Debian: sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info")

if __name__ == "__main__":
    main()
