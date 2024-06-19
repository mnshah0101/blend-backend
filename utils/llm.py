from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

#make a function which takes a string and returns the completion of that string

def create_script(original_script, data):



    prompt = f"""

You are an AI that writes scripts for advertisements. You are given generics scripts and then the customers data, and you must change the script to match .You have been given the following script to work with:
{original_script}

The following is the customers data:
{data}

Please change the script to match the customers data. Do not add any new information. Only respond with the new script, do not comment on the script or adjust the formatting.


The following is the script for a video:

"""


    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4o",
    )

    return chat_completion.choices[0].message.content

