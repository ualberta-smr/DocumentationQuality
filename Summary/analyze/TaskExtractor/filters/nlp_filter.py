def nlp_filter(extracted_tasks):
    black_list = ["use", "learn", "run", "match", "download", "place", "search",
                  "omit", "process", "write", "include"
                  ]
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
