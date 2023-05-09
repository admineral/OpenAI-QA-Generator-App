import os

INPUT_FOLDER = "Output/QA_Finetuning"
OUTPUT_FOLDER = "Output/prepared_for_training"

def sanitize_filename(filename):
    return filename.replace("&", "and").replace(" ", "_")

def main():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    for file_name in os.listdir(INPUT_FOLDER):
        if file_name.endswith(".txt"):
            sanitized_file_name = sanitize_filename(file_name)
            input_file_path = os.path.join(INPUT_FOLDER, file_name)
            output_file_path = os.path.join(OUTPUT_FOLDER, sanitized_file_name)
            os.rename(input_file_path, output_file_path)
            print(f"File {file_name} moved to {output_file_path}")

            absolute_output_file_path = os.path.abspath(output_file_path)
            os.system(f"openai tools fine_tunes.prepare_data -f {absolute_output_file_path}")

if __name__ == "__main__":
    main()
