import os, glob, openai, PyPDF2, sys, io, shutil
from datetime import datetime
import traceback
import tkinter as tk
from tkinter import (filedialog, messagebox, Text, Scrollbar, Tk, Label, Entry, Button,
                     font as tkFont, Listbox, MULTIPLE)
from ttkthemes import ThemedTk
from tkinter import ttk
from tkinter.ttk import Combobox, Style
from tkinter.font import Font


openai.api_key = "<YOUR OPENAI API KEY HERE>"

class ConsoleRedirect:
    def __init__(self, widget):
        self.widget = widget

    def write(self, message):
        self.widget.insert('end', message)
        self.widget.see('end')

    def flush(self):
        pass


def browse_files(files_entry, files_listbox):
    file_paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
    files_entry.delete(0, 'end')
    files_entry.insert(0, ", ".join(file_paths))
    
    # update the files listbox
    for file_path in file_paths:
        files_listbox.insert('end', file_path.split('/')[-1])


def browse_output_folder(output_folder_entry):
    output_folder_path = filedialog.askdirectory()
    output_folder_entry.delete(0, 'end')
    output_folder_entry.insert(0, output_folder_path)

def get_selected_file_paths(files_entry, files_listbox):
    file_paths = files_entry.get().split(", ")
    selected_file_paths = []

    for index in files_listbox.curselection():
        selected_file_name = files_listbox.get(index)
        for file_path in file_paths:
            if file_path.endswith(selected_file_name):
                selected_file_paths.append(file_path)
                break

    return selected_file_paths

def run_main(files_entry, output_folder_entry, run_button, num_questions_combobox, app, files_listbox):

    file_paths = files_entry.get().split(", ")

    if not file_paths or file_paths[0] == "No PDF file selected":
        messagebox.showerror("Error", "Please select PDF files.")
        return

    output_folder = output_folder_entry.get()
    
    if not output_folder or output_folder == "No Output Path selected":
        messagebox.showerror("Error", "Please select an output folder.")
        return
        
    # Get the selected file paths
    selected_file_paths = get_selected_file_paths(files_entry, files_listbox)
    if not selected_file_paths:
        messagebox.showerror("Error", "Please select a PDF file from the list.")
        return

    # Disable the Generate QA Pairs button while processing
    run_button.config(state='disabled')

    # Call main function with the selected PDF file paths
    num_questions = int(num_questions_combobox.get())
    for selected_file_path in selected_file_paths:
        main([selected_file_path], output_folder, num_questions, app)

    # Enable the Generate QA Pairs button after processing
    run_button.config(state='normal')

    # Update the app's event loop
    update_files_listbox(output_folder, files_listbox)
    app.update_idletasks()
    app.update()

    messagebox.showinfo("Success", "Question-answer pairs generated and saved.")

def prepare_selected_data(files_listbox):
    # Get the selected files
    selected_files = [files_listbox.get(idx) for idx in files_listbox.curselection()]

    if not selected_files:
        messagebox.showerror("Error", "Please select files to prepare.")
        return

    # Disable the Prepare Selected Data button while processing
    prepare_selected_data_button.config(state='disabled')

    # Call the data preparation function with the selected files
    num_questions = int(num_questions_combobox.get())
    prepare_data(selected_files, num_questions)

    # Enable the Prepare Selected Data button after processing
    prepare_selected_data_button.config(state='normal')

    # Update the app's event loop
    app.update_idletasks()
    app.update()

    messagebox.showinfo("Success", "Selected files prepared.")

def read_handouts(folder_path):
    handouts = []

    for file_path in glob.glob(os.path.join(folder_path, "*.txt")):
        with open(file_path, "r", encoding="utf-8") as f:
            handouts.append(f.read())

    return handouts

def create_qa_pairs(handouts, num_questions):
    qa_pairs = []

    for handout in handouts:
        prompt = (
            f"Generate a set of {num_questions} unique and informative Q&A pairs that encompass various topics and concepts mentioned in the text. These pairs should aid in enhancing comprehension of the content when fine-tuning an AI language model. Be sure to craft high-quality questions that are directly related to the text and provide concise, accurate answers that further elucidate the topic at hand.\n\n"
            f"{handout}"
        )
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=0.5,
            max_tokens=2000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        questions_answers = response["choices"][0]["text"].strip()
        pairs = questions_answers.split("\n\n")

        for pair in pairs:
            lines = pair.split("\n")
            if len(lines) != 2:
                print(f"Unexpected format: {pair}")
                continue

            question, answer = lines
            qa_pairs.append({"question": question[3:], "answer": answer[3:]})

        save_api_response(response)
        tokens_used = response["usage"]["total_tokens"]
        cost = calculate_cost(tokens_used)
        print(f"Tokens used: {tokens_used}, Cost: ${cost:.4f}")

    return qa_pairs

def save_api_response(response):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"API_Response_{timestamp}.txt"
    
    output_dir = os.path.join(os.getcwd(), "Output", "API_response")
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(response))

def calculate_cost(tokens_used):
    cost_per_1000_tokens = 0.02
    cost = tokens_used * cost_per_1000_tokens / 1000
    return cost

def save_qa_pairs(qa_pairs, output_folder):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"QA_Finetuning_{timestamp}.txt"

    # Save in the user-selected output folder
    user_output_dir = os.path.join(output_folder, "QA_Finetuning")
    os.makedirs(user_output_dir, exist_ok=True)
    user_file_path = os.path.join(user_output_dir, file_name)

    # Save in the fixed output folder
    fixed_output_dir = os.path.join("Output", "QA_Finetuning")
    os.makedirs(fixed_output_dir, exist_ok=True)
    fixed_file_path = os.path.join(fixed_output_dir, file_name)

    # Write the file to both locations
    with open(user_file_path, "w", encoding="utf-8") as user_f, open(fixed_file_path, "w", encoding="utf-8") as fixed_f:
        for pair in qa_pairs:
            user_f.write(f"Q: {pair['question']}\n")
            user_f.write(f"A: {pair['answer']}\n\n")
            fixed_f.write(f"Q: {pair['question']}\n")
            fixed_f.write(f"A: {pair['answer']}\n\n")

def read_handouts_from_pdfs(file_paths):
    handouts = []

    for file_path in file_paths:
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            content = ""

            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                content += page.extract_text()

            handouts.append(content)

    return handouts

def prepare_selected_data(listbox):
    selected_indices = listbox.curselection()
    selected_files = [listbox.get(index) for index in selected_indices]

    for file_name in selected_files:
        if file_name.endswith(".txt"):
            sanitized_file_name = sanitize_filename(file_name)
            input_file_path = os.path.join(INPUT_FOLDER, file_name)
            output_file_path = os.path.join(OUTPUT_FOLDER, sanitized_file_name)
            os.rename(input_file_path, output_file_path)
            print(f"File {file_name} moved to {output_file_path}")

            absolute_output_file_path = os.path.abspath(output_file_path)
            os.system(f"openai tools fine_tunes.prepare_data -f {absolute_output_file_path}")

def update_files_listbox(folder_path, files_listbox):
    
    files_listbox.delete(0, 'end')  # Löschen Sie alle Elemente in der Listbox

    # Fügen Sie Dateien aus dem ausgewählten Ordner zur Listbox hinzu
    if os.path.exists(folder_path):
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".txt"):
                files_listbox.insert('end', file_name)


def create_tkinter_app():

    print("create_tkinter_app() - start")

    # create the app
    app = Tk()

    app.title("Handout QA Generator")
    app.geometry("1000x700")
    app.resizable(False, False)

    style = Style()
    style.configure('TButton', font=('Helvetica', 12), padx=10, pady=10)
    style.configure('TLabel', font=('Helvetica', 12))
    style.configure('TEntry', font=('Helvetica', 12))
    style.configure('TCombobox', font=('Helvetica', 12))

    # set the font
    custom_font = Font(family="Helvetica", size=12, weight="normal")
# -->Create and style widgets

################################### -- INPUT BUTTON -- #########################################

    # ---Select Input File
    handout_pdf_path = ""

    Label(app, text="Handouts PDF Files:", font=custom_font).grid(row=0, column=0, padx=10, pady=10, sticky="e")

    #Show path of Input File
    files_entry = Entry(app, width=50, font=custom_font)
    files_entry.insert(0, "No PDF file selected")
    files_entry.grid(row=0, column=1, padx=10, pady=10)

    
    browse_button = ttk.Button(app, text="Browse", command=lambda: browse_files(files_entry, files_listbox))
    print("Pressed #Input-Button")

    browse_button.grid(row=0, column=2, padx=10, pady=10)


################################### -- OUTPUT BUTTON --  ########################################

    # ---Select Output Path
    output_folder_path = ""

    Label(app, text="Output Folder:", font=custom_font).grid(row=1, column=0, padx=10, pady=10, sticky="e")

    #Show path of Output File
    output_folder_entry = Entry(app, width=50, font=custom_font)
    output_folder_entry.insert(0, "No Output Path selected")
    output_folder_entry.grid(row=1, column=1, padx=10, pady=10)

    
    browse_output_button = ttk.Button(app, text="Browse", command=lambda: browse_output_folder(output_folder_entry))
    print("Pressed #Output-Button")

    browse_output_button.grid(row=1, column=2, padx=10, pady=10)


################################ -- NUMBER OF QUESTIONS -- #######################################

    # Create the Combobox for the number of questions

    Label(app, text="Number of Questions:", font=custom_font).grid(row=2, column=0, padx=10, pady=10, sticky="e")

    num_questions_combobox = Combobox(app, values=list(range(1, 21)), state="readonly", width=3)
    num_questions_combobox.grid(row=2, column=1, padx=10, pady=10)

    # Set the default value to 20
    num_questions_combobox.set("20")  


################################### --SELECT FILES-- #############################################

    # Create List & Select File

    files_listbox_label = Label(app, text="Select Files:", font=custom_font)
    files_listbox_label.grid(row=4, column=0, padx=10, pady=10, sticky="nw")

    files_listbox = Listbox(app, selectmode=MULTIPLE, height=10, width=70, font=custom_font)
    files_listbox.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    files_scrollbar = Scrollbar(app, command=files_listbox.yview)
    files_scrollbar.grid(row=5, column=2, padx=0, pady=10, sticky="ns")

    files_listbox.config(yscrollcommand=files_scrollbar.set)
    update_files_listbox(output_folder_entry.get(), files_listbox)


################################# --PREPARE SELECTED DATA-- ######################################

    
    # Create the new button for data preparation

    prepare_selected_data_button = ttk.Button(app, text="Prepare Selected Data", command=lambda: prepare_selected_data(files_listbox))
    prepare_selected_data_button.grid(row=6, column=0, padx=10, pady=10)

    console_label = Label(app, text="Console Output:", font=custom_font)
    console_label.grid(row=7, column=0, padx=10, pady=10, sticky="nw")

    console_text = Text(app, wrap="word", height=10, width=90, font=custom_font)
    console_text.grid(row=8, column=0, columnspan=3, padx=10, pady=10)

    console_scrollbar = Scrollbar(app, command=console_text.yview)
    console_scrollbar.grid(row=8, column=3, padx=0, pady=10,sticky="ns")

    console_text.config(yscrollcommand=console_scrollbar.set)

    
    update_files_listbox(output_folder_entry.get(), files_listbox)
    

################################# -- GENERATE QA PAIRS BUTTON-- ##################################


    ## Generate QA Pairs Button

    run_button = ttk.Button(app, text="Generate QA Pairs", command=lambda: run_main(files_entry, output_folder_entry, run_button, num_questions_combobox, app, files_listbox))


    run_button.grid(row=3, column=1, padx=10, pady=10)
    

    print("create_tkinter_app() - Bind Return key to run_main function")

    #Bind Return key to run_main function
    app.bind('<Return>', lambda event: run_main())

############################# --CONSOLE OUTPUT-- #################################################

    #Console output in APP GUI
    sys.stdout = ConsoleRedirect(console_text)
    sys.stderr = ConsoleRedirect(console_text)
    
 ################################ --START THE APP-- ##############################################

    # start the app
    app.mainloop()
    

def main(file_paths, output_folder, num_questions, app):
    
    print("Reading handouts...")
    app.update_idletasks()
    app.update()
    handouts = read_handouts_from_pdfs(file_paths)

    print("Creating question-answer pairs...")
    app.update_idletasks()
    app.update()
    qa_pairs = create_qa_pairs(handouts, num_questions)

    print("Saving question-answer pairs...")
    app.update_idletasks()
    app.update()
    save_qa_pairs(qa_pairs, output_folder)

    total_words = sum(len(pair["question"].split()) + len(pair["answer"].split()) for pair in qa_pairs)
    print(f"Done! {len(qa_pairs)} question-answer pairs generated and saved. Total words: {total_words}.")
    app.update_idletasks()
    app.update()

if __name__ == "__main__":
    try:
        print("Starting GUI...")
        app = create_tkinter_app()
        print("App created")
       
        app.mainloop()

        print("App ended")

    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()