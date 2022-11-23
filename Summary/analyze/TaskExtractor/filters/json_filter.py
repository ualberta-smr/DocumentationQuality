def json_filter(extracted_tasks):
    black_list = ["apply", "change", "compare", "create", "disable", "handle",
                  "implement", "include", "indent", "open", "pass", "provide",
                  "raise", "remove", "return", "run", "store", "submit",
                  "support", "test", "use"]
    tasks = []
    for task in extracted_tasks.strip().split("\n"):
        if not task.split(" ")[0] in black_list:
            tasks.append(task)
    return "\n".join(tasks)


# Removed words from verb list from Orjson
# submit
# disable
# indent
# store
# apply
# compare
# handle
# return
# create
# test
#
# Removed words from verb list from Json-java
# implement
# change

# Block list
# support
# raise
# remove
# provide
# use
# pass
# include
# run
# open
