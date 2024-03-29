def dom_manipulation_filter(extracted_tasks):
    black_list = ["add", "apply", "assign", "call", "change", "compare",
                  "create", "describe", "disable", "find", "handle",
                  "implement", "indent", "insert", "introduce", "learn",
                  "receive", "remove", "render", "return", "reuse", "specify",
                  "store", "submit", "test", "fetch", "use", "write"]
    tasks = []
    for task in extracted_tasks.strip().split("\n"):
        if not task.split(" ")[0] in black_list:
            tasks.append(task)
    return "\n".join(tasks)


# ADD
# manipulate
# select
# map
# check
# generate
# get
# set
# toggle
# iterate
# extend
# modify
# serialize
# return
#
# REMOVE
# specify
# fetch
# insert
# call
# receive
# assign
# add
# find
# learn
# describe
# reuse
# introduce
# remove
#
# FILTER
# return
# render
# use
# write
