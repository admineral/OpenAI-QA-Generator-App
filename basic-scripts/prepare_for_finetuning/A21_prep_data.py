import json
import os

# set input directory and output file
input_dir = "/Users/QA_files"
output_file = "/Users/output.jsonl"

# initialize list to store question and answer pairs
qa_pairs = []

# loop through each file in input directory
for filename in os.listdir(input_dir):
    # read in contents of file
    with open(os.path.join(input_dir, filename), "r") as file:
        content = file.readlines()

    # check that file has an even number of lines
    if len(content) % 2 != 0:
        print("""ERROR: Input file '{}' does not have an even number of 
lines.""".format(filename))
        continue

    # loop through each line in file and extract question-answer pairs
    for i in range(0, len(content), 2):
        if content[i].startswith("Q:") and content[i+1].startswith("A:"):
            question = content[i][3:].strip() + "\n"
            answer = content[i+1][3:].strip()
            data = {"prompt": question, "completion": answer}
            json_data = json.dumps(data, ensure_ascii=False)
            qa_pairs.append(json_data)
        else:
            print("ERROR: Incomplete Q&A pair found in file '{}', line {}: {}".format(filename, i+1, content[i]))

# write question and answer pairs to output file in JSONL format
with open(output_file, "w") as file:
    for pair in qa_pairs:
        file.write(pair + "\n")

# check that output file has expected format
with open(output_file, "r") as file:
    lines = file.readlines()
    for line in lines:
        try:
            json.loads(line)
        except json.JSONDecodeError:
            print("ERROR: Output file does not have expected format.")
            break
    else:
        print("Output file has expected format.")

# print number of Q&A pairs processed
print("Processed {} Q&A pairs.".format(len(qa_pairs)))

