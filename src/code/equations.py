import asyncio
import glob
import json
import os
import re
import sys
from pathlib import Path

from openai import AsyncOpenAI
from pylatexenc.latexencode import unicode_to_latex
from tenacity import RetryError, stop_after_attempt, retry
from termcolor import colored

project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

import logging
from datetime import datetime

# set up logger
logging.basicConfig(
    filename=f'logs/poems-{datetime.now()}.log',
    filemode='w',
    level=logging.INFO
)

client = AsyncOpenAI()

chapters_path = os.environ["CHAPTERS_PATH"]

skip_existing = True
auto_rename = True

with open('scripts/examples.txt') as f:
    examples = f.read()

with open("book/layout.json", "r+") as f:
    layout = json.load(f)

with open("scripts/function.json") as f:
    equation_function = json.load(f)


@retry(stop=stop_after_attempt(5), after=lambda r: print(r.outcome.exception()))
async def write_chapter(idx, topic):
    output_path = f"{chapters_path}/{idx:03d}_{topic}.tex"

    if skip_existing:
        if os.path.exists(output_path):
            print(colored(f"[{idx}] {output_path} exists. skipping...", 'light_grey'))
            return

    existing_paths = glob.glob(f"{chapters_path}/*_{topic}.tex")
    if len(existing_paths) == 1:
        os.rename(existing_paths[0], output_path)
        print(colored(f"[{idx}] Renamed {existing_paths[0]} to {output_path}.", 'yellow'))
        return

    print(colored(f"[{idx}] Writing chapter for {topic}...", 'blue'))
    chat_completion = await client.chat.completions.create(
        messages=[
            {"role": "user",
             "content": f"""\
        For the topic ({topic}), create an equation with 4-6 variables and use the
        full gamut of mathematical ideas to express it. The equation should be simple, grounded and understandable. Have
        a pedagogical tone. Topics are in the context of human life. Write out a detailed explanation for
        the equation and how the variables relate. Write equation in Latex.
                
        Here are some examples:
        {examples}
        """}
        ],
        model="gpt-4-turbo-preview",
        tools=[{"type": "function", "function": equation_function}]
    )

    output = json.loads(chat_completion.choices[0].message.tool_calls[0].function.arguments)
    logging.info(output)

    # second pass
    print(colored(f"[{idx}] Proofreading chapter for {topic}...", 'yellow'))
    chat_completion = await client.chat.completions.create(
        messages=[
            {"role": "user",
             "content": f"""\
           The following json represents an equation for {topic}. Could you ensure the following:
           - Latex is formatted correctly
           - There are between four to six variables (edit equation as necessary)
           - Equation is not overly complex
           - Edits to language for clarity and conciseness (as required)
           - Ensure variable descriptions are understandable and simple
           - Variability in variable description lengths/structures (between 80 - 200 characters)
           - If possible without losing much meaning, make variables one word
           
           {output}
           """}
        ],
        model="gpt-4-turbo-preview",
        tools=[{"type": "function", "function": equation_function}]
    )

    output = json.loads(chat_completion.choices[0].message.tool_calls[0].function.arguments)
    logging.info(output)

    equation = output['equation']

    # left side should be topic expanded
    equation = re.sub(r".*=", f"{topic} =", equation)

    variables = output['variables']

    variables_str = ""

    # drop the first variable (on left side)
    for idx, variable in enumerate(variables[1:]):
        name = unicode_to_latex(variable['name']).title()
        symbol = variable['symbol']
        desc = unicode_to_latex(variable['description'])
        variables_str += r"\item $%s$: \index{%s}\textit{%s}. %s" % (symbol, name, name, desc) + "\n"

    poem = "\poem{%s}{%s}{%s}" % (topic, equation, variables_str)

    with open(output_path, "w+") as f:
        f.write(poem)
        print(colored(f"[{idx}] Wrote {topic} to {output_path}", 'green'))


async def retry_write_chapter(*args):
    try:
        await write_chapter(*args)
    except RetryError as e:
        print(e)


async def main():
    print("loading topics...")

    # flatten list
    poems = [item for item in layout.values() for item in item]

    print("starting to write chapters...")
    await asyncio.gather(*(retry_write_chapter(idx, topic) for idx, topic in enumerate(poems, 1)))


asyncio.run(main())
