import subprocess
import os
from fuzzywuzzy import fuzz
import re
from pyquery import PyQuery as pq


# P_REGEX = re.compile("(?<=<p>).+?(?=</p>)")
# CODE_REGEX = re.compile("(?<=<code>)[\s\S]*?(?=</code>)")

def get_paragraphs_and_tasks(paragraphs):
    paragraphs_w_tasks = []
    with open("tasks.txt", "w", encoding="utf-8") as task_file:
        os.chdir("TaskExtractor")
        for paragraph in paragraphs.items():
            if len(paragraph[0].classes) == 0:
                extract = call_extractor(paragraph.text())
                if extract:
                    paragraphs_w_tasks.append(paragraph.text())
                    task_file.write(paragraph.text())
                    task_file.write("\n")
                    task_file.write(extract.replace("\r\n", "\n"))
                    task_file.write("\n")

        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    return paragraphs_w_tasks


def link_code_examples_and_paragraphs(code_examples, paragraphs):
    with open("links.txt", "w", encoding="utf-8") as links_file:
        for example in code_examples.items():
            code = example
            # Look for the closest parent with siblings
            while example.siblings().length == 0:
                example = example.parent()

            # Find the paragraph that is right above the code example
            paragraph = None
            for child in example.parent().children():
                if re.match(re.compile("h[0-6]"), child.tag):
                    paragraph = None
                # TODO: There is an issue where the paragraphs list contains paragraphs with inline code
                # But child.text does not contain inline code. So there are false links
                # That is okay because we do not care about inline
                elif child.text in paragraphs:
                    paragraph = child
                if example[0] == child:
                    break
            if paragraph is not None:
                links_file.write(paragraph.text + "\n")
                links_file.write(code.text() + "\n\n")


def call_extractor(inp):
    inp = inp.replace("’", "'")
    result = subprocess.run(["java", "-jar", "StringToTasks.jar", inp.encode("utf-8").decode("utf-8")], stdout=subprocess.PIPE)
    return result.stdout.decode("utf-8")


def main():
    raw_html = pq(url="https://stanfordnlp.github.io/CoreNLP/ner.html")
    paragraphs = get_paragraphs_and_tasks(raw_html("p"))

    code_examples = raw_html("code")

    link_code_examples_and_paragraphs(code_examples, paragraphs)


if __name__ == '__main__':
    main()
