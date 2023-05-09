import os
import PyPDF2

# Pfad zur PDF-Datei
pdf_path = '/Users//handout.pdf'

# Pfad zur Textdatei
text_path = '/Users/handout_txt.txt'

try:
    # Überprüfe, ob die PDF-Datei existiert
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f'Die PDF-Datei "{pdf_path}" wurde nicht gefunden!')

    # Öffne die PDF-Datei im binären Modus
    with open(pdf_path, 'rb') as file:
        # Erstelle ein PDF-Reader-Objekt
        reader = PyPDF2.PdfReader(file)

        # Erstelle ein leeres Textdokument
        with open(text_path, 'w') as text_file:
            # Schleife durch jede Seite des PDFs
            for page in range(len(reader.pages)):
                # Extrahiere den Text aus der aktuellen Seite
                text = reader.pages[page].extract_text()

                # Schreibe den Text in das Textdokument
                text_file.write(text)

        # Ausgabe zur Bestätigung
        print(f'Die PDF-Datei wurde erfolgreich in die Textdatei "{text_path}" konvertiert!')

except FileNotFoundError as e:
    print(f'Fehler: {e}')

except Exception as e:
    print(f'Ein Fehler ist aufgetreten: {e}')

