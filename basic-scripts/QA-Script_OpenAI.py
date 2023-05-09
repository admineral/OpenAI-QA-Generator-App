import os
import glob
import openai
from datetime import datetime

openai.api_key = "YOUR-OPENAI-API-KEY-HERE"

def read_handouts(folder_path):
    handouts = []

    for file_path in glob.glob(os.path.join(folder_path, "*.txt")):
        with open(file_path, "r", encoding="utf-8") as f:
            handouts.append(f.read())

    return handouts

def create_qa_pairs(handouts):
    qa_pairs = []

    for handout in handouts:
        prompt = (
            "Generate a set of 20 unique and informative Q&A pairs that encompass various topics and concepts mentioned in the text. These pairs should aid in enhancing comprehension of the content when fine-tuning an AI language model. Be sure to craft high-quality questions that are directly related to the text and provide concise, accurate answers that further elucidate the topic at hand.\n\n"
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

def save_qa_pairs(qa_pairs):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"Q&A_Finetuning_{timestamp}.txt"
    
    output_dir = os.path.join(os.getcwd(), "Output", "Q&A_Finetuning")
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        for pair in qa_pairs:
            f.write(f"Q: {pair['question']}\n")
            f.write(f"A: {pair['answer']}\n\n")

def main():
    print("Reading handouts...")
    folder_path = os.path.join(os.getcwd(), "Handouts")
    handouts = read_handouts(folder_path)

    print("Creating question-answer pairs...")
    qa_pairs = create_qa_pairs(handouts)

    print("Saving question-answer pairs...")
    save_qa_pairs(qa_pairs)

    total_words = sum(len(pair["question"].split()) + len(pair["answer"].split()) for pair in qa_pairs)
    print(f"Done! {len(qa_pairs)} question-answer pairs generated and saved. Total words: {total_words}.")

if __name__ == "__main__":
    main()
