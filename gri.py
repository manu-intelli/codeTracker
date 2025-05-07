# # Install these packages first if needed
# !pip install gerber python-docx pandas matplotlib reportlab


import os
import pandas as pd
from gerber import load, render
from gerber.render import RenderSettings, theme
from difflib import Differ, HtmlDiff
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def compare_gerber_designs(designer1_dir, designer2_dir, output_format='html'):
    """
    Compare two sets of Gerber files from different designers
    
    Args:
        designer1_dir: Directory containing Designer 1's Gerber files
        designer2_dir: Directory containing Designer 2's Gerber files
        output_format: 'html' or 'pdf' for the report format
    """
    
    # Step 1: Collect and match files from both directories
    designer1_files = {f: os.path.join(designer1_dir, f) for f in os.listdir(designer1_dir) 
                      if f.lower().endswith(('.gbr', '.ger', '.gbx', '.gbl', '.gbs', '.gtl', '.gto'))}
    
    designer2_files = {f: os.path.join(designer2_dir, f) for f in os.listdir(designer2_dir) 
                      if f.lower().endswith(('.gbr', '.ger', '.gbx', '.gbl', '.gbs', '.gtl', '.gto'))}
    
    all_files = set(designer1_files.keys()).union(set(designer2_files.keys()))
    
    # Step 2: Compare each matching file
    comparison_results = []
    
    for filename in sorted(all_files):
        file_results = {'Filename': filename}
        
        # Check file existence
        d1_exists = filename in designer1_files
        d2_exists = filename in designer2_files
        
        file_results['Designer1 Exists'] = 'Yes' if d1_exists else 'No'
        file_results['Designer2 Exists'] = 'Yes' if d2_exists else 'No'
        
        if d1_exists and d2_exists:
            # Compare file contents
            with open(designer1_files[filename], 'r') as f1, open(designer2_files[filename], 'r') as f2:
                lines1 = f1.readlines()
                lines2 = f2.readlines()
                
                # Simple line count comparison
                file_results['D1 Lines'] = len(lines1)
                file_results['D2 Lines'] = len(lines2)
                
                # Calculate differences
                d = Differ()
                diff = list(d.compare(lines1, lines2))
                changes = [line for line in diff if line.startswith('+ ') or line.startswith('- ')]
                file_results['Differences Count'] = len(changes)
                
                # Visual comparison
                if output_format == 'html':
                    html_diff = HtmlDiff().make_file(lines1, lines2, 
                                                   fromdesc='Designer1', 
                                                   todesc='Designer2')
                    file_results['Visual Diff'] = html_diff
                
        comparison_results.append(file_results)
    
    # Step 3: Generate report
    if output_format == 'html':
        generate_html_report(comparison_results)
    elif output_format == 'pdf':
        generate_pdf_report(comparison_results)
    else:
        print("Unsupported output format")

def generate_html_report(results):
    """Generate an HTML comparison report"""
    html = """
    <html>
    <head>
        <title>PCB Gerber File Comparison</title>
        <style>
            table {border-collapse: collapse; width: 100%;}
            th, td {border: 1px solid #ddd; padding: 8px; text-align: left;}
            th {background-color: #f2f2f2;}
            .diff {background-color: #ffe6e6;}
            .missing {background-color: #ffcccc;}
        </style>
    </head>
    <body>
        <h1>PCB Gerber File Comparison Report</h1>
        <table>
            <tr>
                <th>Filename</th>
                <th>In Designer1</th>
                <th>In Designer2</th>
                <th>D1 Lines</th>
                <th>D2 Lines</th>
                <th>Differences</th>
            </tr>
    """
    
    for result in results:
        row_class = ''
        if result['Designer1 Exists'] != result['Designer2 Exists']:
            row_class = 'class="missing"'
        elif result.get('Differences Count', 0) > 0:
            row_class = 'class="diff"'
            
        html += f"""
        <tr {row_class}>
            <td>{result['Filename']}</td>
            <td>{result['Designer1 Exists']}</td>
            <td>{result['Designer2 Exists']}</td>
            <td>{result.get('D1 Lines', '')}</td>
            <td>{result.get('D2 Lines', '')}</td>
            <td>{result.get('Differences Count', '')}</td>
        </tr>
        """
    
    html += """
        </table>
    </body>
    </html>
    """
    
    with open('gerber_comparison_report.html', 'w') as f:
        f.write(html)
    print("HTML report generated: gerber_comparison_report.html")

def generate_pdf_report(results):
    """Generate a PDF comparison report"""
    doc = SimpleDocTemplate("gerber_comparison_report.pdf", pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    elements.append(Paragraph("PCB Gerber File Comparison Report", styles['Title']))
    
    # Prepare table data
    table_data = [['Filename', 'In D1', 'In D2', 'D1 Lines', 'D2 Lines', 'Differences']]
    
    for result in results:
        table_data.append([
            result['Filename'],
            result['Designer1 Exists'],
            result['Designer2 Exists'],
            str(result.get('D1 Lines', '')),
            str(result.get('D2 Lines', '')),
            str(result.get('Differences Count', ''))
        ])
    
    # Create table
    t = Table(table_data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(t)
    doc.build(elements)
    print("PDF report generated: gerber_comparison_report.pdf")

# Example usage
compare_gerber_designs('path/to/designer1/files', 'path/to/designer2/files', 'html')