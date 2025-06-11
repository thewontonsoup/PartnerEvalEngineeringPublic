from dotenv import load_dotenv
import os
from openai import OpenAI
from openai.types.chat import ParsedChatCompletionMessage

PROMPT_FILE_PATH = os.path.join(os.path.dirname(__file__), "prompt_portfolio.txt")


def main(path: str, type: str):
    load_dotenv()
    API_KEY = os.getenv("API_KEY")

    # files = []
    # getAllFiles(os.getcwd(), files) #can replace with other directory
    # results = process("Multifamily OM", API_KEY, files)
    # outputFiles( "extracted",results)

    text = readFile(path)
    # res = request("Multifamily OM", API_KEY, text)
    res = request(type, API_KEY, text)
    # with open('result.txt','w') as file:
    #     file.write(res.content)
    print(res.content)
    return res.content
    # print(res)


def readFile(path: str) -> str:
    """
    Reads a file and returns a str with the contents of the file

    Args:
        path: a str representing the path to the file

    Returns:
        str: a str containing the contents of the file
    """
    with open(path, 'r') as file:
        text = file.read()
    return text


def request(type: str, api: str, text: str) -> ParsedChatCompletionMessage:
    """
    Uses OpenAI API to parse data from the given text based on document type.

    Args:
        type: a str representing the document type
        api: a str representing the OpenAI API Key
        text: a str representing the text to be parsed

    Returns:
        ParsedChatCompletionMessage: the result of the OpenAI API query, use the .content field to access the actual content as a str
    """
    client = OpenAI(api_key=api)

    prompt = readFile(PROMPT_FILE_PATH)

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user",
             "content": f"This lease is of type {type} and the following is the text that I need you to extract from. f{text}"},
        ],
        response_format={"type": "json_object"},
    )

    event = completion.choices[0].message
    return event


if __name__ == '__main__':
    main("output_unstructured.txt", "Multifamily OM")
