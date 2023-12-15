import os
from apikey import api_key
import numpy as np
from langchain.llms import OpenAI

os.environ['OPENAI_API_KEY'] = api_key
def ats(transcript):

    # Chunking the transcript into smaller chunks
    chunk_size = 5000
    chunks = [transcript[i:i + chunk_size] for i in range(0, len(transcript), chunk_size)]

    # Combine the results from each chunk
    combined_output = []

    for chunk in chunks:
        prompt = f'analyze this raw video transcript. Return only the most usable and attractive dialogues spoken by only the interviewee like their introduction and job experience to use for final video editing but do not mold words.Additionally, do not include any output-related statements or unnecessary phrases in the response.here is the transcript:\n"{chunk}"'
        llm = OpenAI(temperature=np.random.random())
        output = llm(prompt).strip()
        phrases_to_remove = ["The usable dialogues you can use for the final video editing would be:",
                             "Interviewee Dialogues:","Interviewee dialogues:" , "Answer:","Interviewee Dialogue:"]

        # Remove specific phrases
        for phrase in phrases_to_remove:
            output = output.replace(phrase, '')

        # Remove both single and double quotes
            output = output.replace("'", '').replace('"', '')

        # Split text into lines based on "."
            lines = output.split('.')

        # Remove empty lines
            lines = [line.strip() for line in lines if line.strip() and ":" not in line]

        # Print the processed lines
        #for line in lines:
            #print(line)
        combined_output += lines

    #print(combined_output)
    #print(type(combined_output))

    return combined_output
