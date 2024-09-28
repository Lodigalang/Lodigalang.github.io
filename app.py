from flask import Flask, request, render_template
import docx
import csv
import os

app = Flask(__name__)

def read_docx(file_path):
    doc = docx.Document(file_path)
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip() != '']
    return paragraphs

def load_correction_dict(file_path):
    correction_dict = {}
    try:
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) == 2:
                    tidak_baku, baku = row
                    correction_dict[tidak_baku.strip().lower()] = baku.strip()
    except FileNotFoundError:
        return {}
    return correction_dict

def check_baku_in_kalimat(kalimat_data, baku_words, correction_dict):
    results = []
    for line in kalimat_data:
        words = line.strip().split()
        baku = []
        tidak_baku = []
        corrected_sentence = []

        for word in words:
            clean_word = word.strip('.,!?').lower()
            if clean_word in baku_words:
                baku.append(word)
                corrected_sentence.append(word)
            else:
                tidak_baku.append(word)
                corrected_word = correction_dict.get(clean_word, word)
                corrected_sentence.append(corrected_word)

        result = {
            'original': line.strip(),
            'baku': baku,
            'tidak_baku': tidak_baku,
            'corrected': ' '.join(corrected_sentence)
        }
        results.append(result)
    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        if file and file.filename.endswith('.docx'):
            baku_words = set()
            try:
                with open("teks.txt", "r", encoding='utf-8') as f1:
                    baku_words = set(f1.read().split())

                correction_dict = load_correction_dict("daftar_baku_tidak_baku.csv")
                
                # Save the uploaded file
                file_path = os.path.join("uploads", file.filename)
                file.save(file_path)
                
                kalimat_data = read_docx(file_path)
                results = check_baku_in_kalimat(kalimat_data, baku_words, correction_dict)

                return render_template('results.html', results=results)

            except Exception as e:
                return str(e)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
