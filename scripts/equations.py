"""
equations.py

Generates mathematical equations based on topics.
"""

import os

from openai import OpenAI

client = OpenAI()

topics_txt_path = os.environ["TOPICS_TXT_PATH"]
chapters_path = os.environ["CHAPTERS_PATH"]

skip_existing = True

print("loading topics...")
with open(topics_txt_path) as f:
    topics = [line.strip() for line in f.readlines()]

print("starting to write chapters...")
for idx, topic in enumerate(topics, 1):

    output_path = f"{chapters_path}/{idx:03d}_{topic}.tex"

    if skip_existing:
        if os.path.exists(output_path):
            print(f"[{idx}] {output_path} exists. skipping...")
            continue

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": r"""
                For the following topic, create an equation with 4 - 7 variables and use the full gamut of mathematical
                ideas to express it. It should be logically consistent. Only include the equation and what each variable
                represents. To quantify the theme, you have a choose a particular dimension of the topic. The equation 
                should be inspired by human literature, philosophy, and culture, but should remain grounded. 
                The topic should be approached from a humanistic point of view. Write everything in LaTeX. 
                Do not add anything else - only fill in the dots. Raw output (not code).
                
                \chapter{%s}
                
                \begin{equation}
                \text{%s} = ...
                \end{equation}
                
                \textbf{Where:}
                
                \begin{itemize}
                    \item $X$: ...
                \end{itemize}
                """ % (topic, topic),
            }
        ],
        model="gpt-4-turbo-preview",
    )

    equation = chat_completion.choices[0].message.content

    with open(output_path, "w+") as f:
        f.write(equation)
        print(f"[{idx}] Wrote {topic} to {output_path}")
