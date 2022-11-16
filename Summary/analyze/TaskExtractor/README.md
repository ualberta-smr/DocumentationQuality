This component of the project deals with extracting tasks from documentation and linking code examples also found in documentation to paragraphs where we extracted tasks from.

The website_process.py takes 1 command line argument being the name of the library.
It finds the extracted tasks and code example links, and combines them into a csv that is used by the website. **Must** be run from the root directory in order to properly find the file and copy them correctly to the Website directory

https://www.cs.mcgill.ca/~swevo/tasknavigator/