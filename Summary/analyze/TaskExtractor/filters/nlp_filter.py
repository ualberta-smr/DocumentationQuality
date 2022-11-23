def nlp_filter(extracted_tasks):
    black_list = ["adjust", "apply", "combine", "count", "customize",
                  "describe", "download", "extend", "find", "generate",
                  "implement", "include", "learn", "list", "locate", "match",
                  "omit", "place", "process", "purchase", "read", "redirect",
                  "run", "search", "separate", "seperate", "store", "use",
                  "write"]
    tasks = []
    for task in extracted_tasks.strip().split("\n"):
        if not task.split(" ")[0] in black_list:
            tasks.append(task)
    return "\n".join(tasks)

# REMOVE
# store
# describe
# combine
# apply
# find
# customize
# purchase
#
# adjust
# separate
# list
# redirect
# read
# count
# generate
# locate
# extend
# implement
#
# FILTER
# use
# learn
# run
# match
# download
# place
# search
# omit
# process
# write
# include
