import os
import fitz

def extract_text_with_positions(pdf_path):
    doc = fitz.open(pdf_path)
    text_data = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if block["type"] == 0:  # Text block
                for line in block["lines"]:
                    for span in line["spans"]:
                        text_data.append({
                            "text": span["text"],
                            "page_num": page_num,
                            "rect": span["bbox"]
                        })

    return text_data

def save_extracted_text_with_position(text_data, output_path):
    with open(output_path, 'w') as output_file:
        for item in text_data:
            output_file.write(f"Page: {item['page_num']}\n")
            output_file.write(f"Text: {item['text']}\n")
            output_file.write(f"Position: {item['rect']}\n")
            output_file.write('\n')

def highlight_text(input_pdf_path, output_pdf_path, text_to_highlight):
    doc = fitz.open(input_pdf_path)

    for page_num in range(len(doc)):
        page = doc[page_num]
        found = page.search_for(text_to_highlight)
        for found_rect in found:
            highlight = page.add_highlight_annot(found_rect)
    
    doc.save(output_pdf_path)

if __name__ == "__main__":
    pdf_path = "/Users/handout.pdf"
    output_dir = os.path.dirname(pdf_path)
    extracted_text_with_position_path = os.path.join(output_dir, "extracted_text_with_position.txt")
    highlighted_pdf_path = os.path.join(output_dir, "highlighted.pdf")

    text_data = extract_text_with_positions(pdf_path)
    save_extracted_text_with_position(text_data, extracted_text_with_position_path)

    for item in text_data:
        if "Internal Process" in item["text"]:
            print(f"Found text: '{item['text']}'")
            print(f"Position: {item['rect']}")
            highlight_text(pdf_path, highlighted_pdf_path, item["text"])
            break

    print("Done")
