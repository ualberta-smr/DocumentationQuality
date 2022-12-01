from Summary.analyze.Readability.readability import \
    find_text_readability_metrics
from Summary.analyze.analyze import debug_metrics, analyze_library, clone_library

if __name__ == '__main__':
    # debug_metrics("python", "orjson",
    #                 "http://web.archive.org/web/20210831032333/https://github.com/ijl/orjson",
    #                 "https://github.com/ijl/orjson.git", "json")
    # debug_metrics("python", "nltk",
    #                 "https://web.archive.org/web/20210415060141/https://www.nltk.org/api/nltk.html",
    #                 "https://github.com/nltk/nltk.git", "nlp")
    # debug_metrics("javascript", "react",
    #                 "https://reactjs.org/docs/getting-started.html",
    #                 "https://github.com/facebook/react.git", "dom_manipulation")
    # debug_metrics("python", "Requests",
    #                 "https://requests.readthedocs.io/en/latest/",
    #                 "https://github.com/psf/requests.git", "http")
    # debug_metrics("javascript", "jQuery", "https://api.jquery.com/",
    #                 "https://github.com/jquery/jquery.git", "dom manipulation")
    # debug_metrics("java", "CoreNLP", "https://stanfordnlp.github.io/CoreNLP/cmdline.html",
    #                 "https://github.com/stanfordnlp/CoreNLP.git", "nlp")
    # debug_metrics("javascript", "React", "https://reactjs.org/docs/components-and-props.html",
    #                 "https://github.com/facebook/react.git", "dom_manipulation")
    # debug_metrics("javascript", "jquery", "https://api.jquery.com/jQuery.get",
    #                 "https://github.com/jquery/jquery.git", "dom_manipulation")
    debug_metrics("javascript", "jBinary", "https://github.com/jDataView/jBinary/wiki",
                    "https://github.com/jDataView/jBinary.git", None)
    # debug_metrics("javascript", "qunit",
    #               "https://api.qunitjs.com/",
    #               "https://github.com/qunitjs/qunit.git", "testing")
    # https://web.archive.org/web/20210417122335/https://www.nltk.org/api/nltk.parse.html
    # https://web.archive.org/web/20210725152853/https://www.nltk.org/api/nltk.tag.html
    # http://web.archive.org/web/20211017224709/https://github.com/stleary/JSON-java
    # debug_metrics("java", "JSON-java", "https://github.com/stleary/JSON-java",
    #                 "https://github.com/stleary/JSON-java.git", "json")
    # https://stanfordnlp.github.io/CoreNLP/ner.html
    # https://stanfordnlp.github.io/CoreNLP/cmdline.html
    # debug_metrics("java", "CoreNLP", "https://stanfordnlp.github.io/CoreNLP",
    #                 "https://github.com/stanfordnlp/CoreNLP.git", "nlp")
    # https://reactjs.org/docs/components-and-props.html
    # https://api.jquery.com/jQuery.get
    # debug_metrics("javascript", "jQuery", "https://api.jquery.com/",
    #                 "https://github.com/jquery/jquery.git", "dom manipulation")

    # repo_path = clone_library("orjson", "https://github.com/ijl/orjson.git")
    # analyze_library("python", "orjson",
    #                             "http://web.archive.org/web/20210831032333/https://github.com/ijl/orjson",
    #                             "https://github.com/ijl/orjson.git", "json", repo_path)
    # analyze_library("python", "nltk",
    #                 "https://web.archive.org/web/20210415060141/https://www.nltk.org/api/nltk.html",
    #                 "https://github.com/nltk/nltk.git", "nlp")
    # analyze_library("python", "requests",
    #                 "https://web.archive.org/web/20220505163814/https://docs.python-requests.org/en/latest/",
    #                 "https://github.com/psf/requests.git", "http")
    # analyze_library("java", "JSON-java", "https://github.com/stleary/JSON-java",
    #                 "https://github.com/stleary/JSON-java.git", "json")
    # analyze_library("java", "CoreNLP", "https://stanfordnlp.github.io/CoreNLP",
    #                 "https://github.com/stanfordnlp/CoreNLP.git", "nlp")
    # analyze_library("javascript", "React",
    #                 "https://reactjs.org/docs/getting-started.html",
    #                 "https://github.com/facebook/react.git", "dom manipulation")
    # analyze_library("javascript", "jQuery", "https://api.jquery.com/",
    #                 "https://github.com/jquery/jquery.git", "dom manipulation")
    # analyze_library("javascript", "qunit", "https://api.qunitjs.com/",
    #                 "https://github.com/qunitjs/qunit.git", "testing")
    # analyze_library("javascript", "jBinary",
    #                 "https://github.com/jDataView/jBinary/wiki",
    #                 "https://github.com/jDataView/jBinary.git",
    #                 "data structures")
