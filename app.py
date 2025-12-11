from flask import Flask, render_template, request, jsonify
import re
import pdfplumber
import io
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Your center's student IT numbers
CENTER_STUDENTS = {
    "IT23542556": "Sobiyan S",
    "IT23556652": "Joel Nithushan A.T",
    "IT23570962": "Lowmika.L",
    "IT23571020": "Jeyanash.J",
    "IT23581616": "Nirojan.G",
    "IT23581852": "Athithya M",
    "IT23607996": "Sureka A",
    "IT23611610": "Kenuja S",
    "IT23615816": "Vytheki.S",
    "IT23635784": "Kajana.P",
    "IT23635852": "Gowsikan.S",
    "IT23670716": "Vaishnavi S",
    "IT23670952": "Vaishnavi.R",
    "IT23671324": "Heasma.R",
    "IT23683204": "Diltan A",
    "IT23683372": "Kajaluxsan.K",
    "IT23683440": "Anoji.A",
    "IT23683518": "Sarmilan S",
    "IT23717268": "Sivamsan S",
    "IT23717336": "Vaishnavi.L",
    "IT23717572": "Kageepan K",
    "IT23717718": "Adshaya S",
    "IT23717886": "Kiripavan.N",
    "IT23733176": "Biranavy R",
    "IT23739048": "Croos R R A F",
    "IT23739802": "Arun.N",
    "IT23748644": "Kanistan T",
    "IT23752504": "Kajapirathap.J",
    "IT23752672": "Seyon.K",
    "IT23759152": "Saranjan.P",
    "IT23760592": "Gaayaththri M",
    "IT23760660": "Shiromy K B",
    "IT23764934": "Keerthanan N",
    "IT23767454": "Kavithushan B",
    "IT23777354": "Kobitharsan T",
    "IT23778344": "Rishikeshan S",
    "IT23794566": "Gowsika S",
    "IT23794634": "Sinthujan S",
    "IT23794702": "Croos K M C",
    "IT23794870": "Thushalini U",
    "IT23810778": "Subasthican M",
    "IT23811454": "Ahsan M S M",
    "IT23811690": "Pakeerathan B",
    "IT23848566": "Lavan K",
    "IT23849174": "Christhuraja R",
    "IT23855328": "Nivethika K",
    "IT23856240": "Sinthujan P",
    "IT23863484": "Jathushan V",
    "IT23863552": "Shambavi S",
    "IT23204416": "Braveenraj",
    "IT22545862": "Vinushan"
}

def extract_text_from_pdf(pdf_file):
    """Extract all text from a PDF file"""
    try:
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")

def parse_result_line(line):
    """Parse a single line of results"""
    line = line.strip()
    if not line:
        return None

    # Pattern 1: IT XX XXXX XX [marks] [grade] [status]
    match = re.match(r'IT\s*(\d{2})\s*(\d{4})\s*(\d{2})\s+(\d+\.?\d*)\s+([A-F][+-]?)\s+(Pass|Fail)', line, re.IGNORECASE)
    if match:
        return {
            'it_number': f"IT{match.group(1)}{match.group(2)}{match.group(3)}",
            'ca_marks': float(match.group(4)),
            'grade': match.group(5).upper(),
            'status': match.group(6).capitalize()
        }

    # Pattern 2: ITXXXXXXXX [marks] [grade] [status]
    match = re.match(r'IT(\d{8})\s+(\d+\.?\d*)\s+([A-F][+-]?)\s+(Pass|Fail)', line, re.IGNORECASE)
    if match:
        return {
            'it_number': f"IT{match.group(1)}",
            'ca_marks': float(match.group(2)),
            'grade': match.group(3).upper(),
            'status': match.group(4).capitalize()
        }

    return None

def extract_results_from_pdf_text(pdf_text):
    """Extract all results from PDF text using the working method"""
    all_results = []
    
    # Search for each center student in the PDF text
    for it_number in CENTER_STUDENTS.keys():
        # Convert IT number to PDF format (IT XX XXXX XX)
        # e.g., IT23556652 -> IT 23 5566 52
        formatted_it = f"IT {it_number[2:4]} {it_number[4:8]} {it_number[8:10]}"
        
        # Also try compact format (ITXXXXXXXX)
        compact_it = it_number
        
        found = False
        
        # Pattern 1: With CA Marks - IT XX XXXX XX [marks] [Grade] [Status]
        pattern_with_marks = rf"{re.escape(formatted_it)}\s+(\d+\.?\d*)\s+([A-F][+-]?)\s+(Pass|Fail)"
        matches = re.finditer(pattern_with_marks, pdf_text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            ca_marks = float(match.group(1))
            grade = match.group(2).upper()
            status = match.group(3).capitalize()
            
            all_results.append({
                'it_number': it_number,
                'ca_marks': ca_marks,
                'grade': grade,
                'status': status
            })
            found = True
            break  # Only take first match
        
        # Pattern 2: Without CA Marks - IT XX XXXX XX [Grade] [Status]
        if not found:
            pattern_without_marks = rf"{re.escape(formatted_it)}\s+([A-F][+-]?)\s+(Pass|Fail)"
            matches = re.finditer(pattern_without_marks, pdf_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                grade = match.group(1).upper()
                status = match.group(2).capitalize()
                
                all_results.append({
                    'it_number': it_number,
                    'ca_marks': None,  # No CA marks available
                    'grade': grade,
                    'status': status
                })
                found = True
                break  # Only take first match
        
        # Pattern 3: Compact format with CA Marks - ITXXXXXXXX [marks] [Grade] [Status]
        if not found:
            pattern_compact_with_marks = rf"{re.escape(compact_it)}\s+(\d+\.?\d*)\s+([A-F][+-]?)\s+(Pass|Fail)"
            matches = re.finditer(pattern_compact_with_marks, pdf_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                ca_marks = float(match.group(1))
                grade = match.group(2).upper()
                status = match.group(3).capitalize()
                
                all_results.append({
                    'it_number': it_number,
                    'ca_marks': ca_marks,
                    'grade': grade,
                    'status': status
                })
                found = True
                break  # Only take first match
        
        # Pattern 4: Compact format without CA Marks - ITXXXXXXXX [Grade] [Status]
        if not found:
            pattern_compact_without_marks = rf"{re.escape(compact_it)}\s+([A-F][+-]?)\s+(Pass|Fail)"
            matches = re.finditer(pattern_compact_without_marks, pdf_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                grade = match.group(1).upper()
                status = match.group(2).capitalize()
                
                all_results.append({
                    'it_number': it_number,
                    'ca_marks': None,  # No CA marks available
                    'grade': grade,
                    'status': status
                })
                found = True
                break  # Only take first match
    
    return all_results

def extract_results_from_text(text):
    """Extract all results from pasted text (line by line)"""
    all_results = []
    lines = text.split('\n')
    
    for line in lines:
        result = parse_result_line(line)
        if result:
            all_results.append(result)
    
    return all_results

def filter_center_students(all_results):
    """Filter results to show only center students"""
    center_results = []
    
    for result in all_results:
        it_number = result['it_number']
        if it_number in CENTER_STUDENTS:
            result['name'] = CENTER_STUDENTS[it_number]
            center_results.append(result)
    
    # Sort by IT number
    center_results.sort(key=lambda x: x['it_number'])
    
    return center_results

@app.route('/')
def index():
    return render_template('index.html', total_students=len(CENTER_STUDENTS))

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    """Handle PDF file upload"""
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No PDF file provided'}), 400
    
    file = request.files['pdf_file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Please upload a PDF file'}), 400
    
    try:
        # Extract text from PDF
        pdf_text = extract_text_from_pdf(file)
        
        if not pdf_text.strip():
            return jsonify({'error': 'Could not extract text from PDF. The PDF might be scanned or corrupted.'}), 400
        
        # Extract all results from PDF text using PDF-specific extraction
        all_results = extract_results_from_pdf_text(pdf_text)
        
        if not all_results:
            return jsonify({'error': 'No valid results found in PDF. Please check the PDF format.'}), 400
        
        # Results are already filtered to center students, just add names
        center_results = []
        for result in all_results:
            it_number = result['it_number']
            if it_number in CENTER_STUDENTS:
                result['name'] = CENTER_STUDENTS[it_number]
                center_results.append(result)
        
        # Sort by IT number
        center_results.sort(key=lambda x: x['it_number'])
        
        if not center_results:
            return jsonify({'error': 'No results found for your center students in this PDF.'}), 400
        
        # Calculate statistics
        passed = sum(1 for r in center_results if r['status'] == 'Pass')
        failed = len(center_results) - passed
        pass_rate = f"{((passed / len(center_results)) * 100):.1f}%" if center_results else "0.0%"
        
        return jsonify({
            'success': True,
            'results': center_results,
            'statistics': {
                'total_found': len(center_results),
                'total_students': len(CENTER_STUDENTS),
                'passed': passed,
                'failed': failed,
                'pass_rate': pass_rate
            }
        })
    
    except Exception as e:
        return jsonify({'error': f'Error processing PDF: {str(e)}'}), 500

@app.route('/process', methods=['POST'])
def process_results():
    """Handle pasted text results"""
    data = request.get_json()
    results_text = data.get('results', '')
    
    if not results_text.strip():
        return jsonify({'error': 'No results provided'}), 400
    
    try:
        # Extract all results from pasted text
        all_results = extract_results_from_text(results_text)
        
        if not all_results:
            return jsonify({'error': 'No valid results found. Please check the format.'}), 400
        
        # Filter to center students
        center_results = filter_center_students(all_results)
        
        if not center_results:
            return jsonify({'error': 'No results found for your center students.'}), 400
        
        # Calculate statistics
        passed = sum(1 for r in center_results if r['status'] == 'Pass')
        failed = len(center_results) - passed
        pass_rate = f"{((passed / len(center_results)) * 100):.1f}%" if center_results else "0.0%"
        
        return jsonify({
            'success': True,
            'results': center_results,
            'statistics': {
                'total_found': len(center_results),
                'total_students': len(CENTER_STUDENTS),
                'passed': passed,
                'failed': failed,
                'pass_rate': pass_rate
            }
        })
    
    except Exception as e:
        return jsonify({'error': f'Error processing results: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
