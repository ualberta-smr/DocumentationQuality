# Overview
This repository contains the code of extracting tasks and also checking API coverage of code examples in library documentation. The first part is under the TaskExtractor directory, while the second part is in the APICoverage directory.

## Task Extractor

1. Given a HTML webpage:
   1. Extract tasks from the paragraphs of the page denoted with the HTML tag "\<p>"
   2. Find explicit code blocks on the webpage denoted with the HTML tag "\<code>" (Inline code with text is ignored)
2. Link paragraphs with extracted tasks with the extracted code blocks. Ideally, the paragraph/tasks give an idea of what the code example is about.
3. The paragraphs and extracted tasks are written to their own file (`TaskExtractor\results\tasks.txt`), and the linked paragraphs and code examples are written in their own file (`TaskExtractor\results\links.txt`).

### Process
1. Using an HTML parser, extract all HTML elements with the "\<p>" and "\<code>" tags.
2. Using the StringToTasks.jar file provided by Christoph Treude, run the extracted paragraphs through the jar file and keep track of which paragraphs had extracted tasks. 
3. Most code blocks are nested HTML, so traverse the parents until we reach a parent with siblings (usually this means we are at the top level of HTML elements). Then traverse the siblings looking for candidate paragraphs, stop when we reach our current code element. A candidate paragraph is:
   1. One that is before the code example, and does not cross a header ("\<h1-6>")
   2. One that has extracted tasks from the previous step

   Most explanations of code examples happen before the code example, that is why we stop searching after we reach our code example. A paragraph can be linked with multiple code examples, and a code example may not have an explanation.


Create "task_data" MySQL database manually

### Deficiencies
GitHub repo requires the source code to be in a directory named "src" or the library name for the scripts to work. e.g., https://github.com/nltk/nltk (code under library name), https://github.com/stanfordnlp/CoreNLP (code under src)

The `readability.classifier` needs to be in the analyze root directory and not the Readability directory because the rsm.jar looks for the classifier in the working directory from which it was called from, and we can not change directories in order to run all the metrics in multithreads.

Needs 
https://memcached.org/#/
# License
Described in the [LICENSE](http://github.com/ualberta-smr/tang-task-extractor/blob/main/LICENSE) file