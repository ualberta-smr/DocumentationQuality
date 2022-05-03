def json_filter(extracted_tasks):
    black_list = ["support", "submit", "disable", "return", "indent", "sort",
                  "pass", "call", "apply", "configure", "compare", "read",
                  "input", "test", "run", "include", "introduce", "implement",
                  "read", "open", "provide", "add", "manipulate", "force",
                  "extend", "handle", "store", "import", "write", "change"
                  ]
    tasks = []
    for task in extracted_tasks.strip().split("\n"):
        if not task.split(" ")[0] in black_list:
            tasks.append(task)
    return "\n".join(tasks)
