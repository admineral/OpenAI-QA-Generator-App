# OpenAI-QA-Generator-App

This QA Generator is an application that automatically generates question-answer pairs for PDF handouts using OpenAI's GPT-3.5. These Q&A pairs can be used to enhance comprehension and fine-tune AI language models.


## Features

- Select PDF files and extraxt the text
- Specify the output folder to save generated QA pairs
- Choose the number of questions to generate for each handout
- View generated files and prepare them for fine-tuning
- Console output within the application's GUI

## Installation

1. Make sure you have Python 3.6 or later installed.
2. Clone this repository or download it as a ZIP file and extract it.
3. Install required libraries by running the following command in the terminal:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:

```bash
python handout_qa_generator.py
```

2. Browse and select PDF files for handouts.
3. Choose an output folder where the generated QA pairs will be saved.
4. Specify the number of questions to generate for each handout.
5. Click on the "Generate QA Pairs" button to start the process.
6. The application will create the question-answer pairs and save them in the specified output folder.
7. To prepare the selected data for fine-tuning, select the generated files in the list, and click the "Prepare Selected Data" button.

## API Key

To use Handout QA Generator, you need to provide your OpenAI API key. Replace the placeholder text in the following line with your API key:

```python
openai.api_key = "<YOUR OPENAI API KEY HERE>"
```

## Dependencies

- openai
- PyPDF2
- tkinter
- ttkthemes
- glob

## License

This project is licensed under the MIT License.
