from Summary.analyze.Readability.readability import \
    find_text_readability_metrics
from Summary.analyze.analyze import debug_metrics, analyze_library, clone_library

if __name__ == '__main__':
    # debug_metrics("python", "orjson",
    #                 "https://github.com/ijl/orjson",
    #                 "https://github.com/ijl/orjson.git", "json")
    # debug_metrics("python", "nltk-new",
    #                 "https://www.nltk.org/api/nltk.html",
    #                 "https://github.com/nltk/nltk.git", "nlp")
    #
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
    # debug_metrics("javascript", "React", "https://reactjs.org/docs/getting-started.html",
    #                 "https://github.com/facebook/react.git", "dom_manipulation")
    # debug_metrics("javascript", "jquery", "https://api.jquery.com/jQuery.get",
    #                 "https://github.com/jquery/jquery.git", "dom_manipulation")
    # debug_metrics("javascript", "jBinary", "https://github.com/jDataView/jBinary/wiki",
    #                 "https://github.com/jDataView/jBinary.git", None)
    # debug_metrics("javascript", "qunit",
    #               "https://api.qunitjs.com/",
    #               "https://github.com/qunitjs/qunit.git", "testing")
    # debug_metrics("python", "nltk",
    #                 "https://web.archive.org/web/20210725152853/https://www.nltk.org/api/nltk.tag.html",
    #                 "https://github.com/nltk/nltk.git", "nlp")
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
    # debug_metrics("python", "pytest",
    #               "https://docs.pytest.org/en/7.2.x/",
    #               "https://github.com/pytest-dev/pytest", "")
    debug_metrics("python", "pandas",
                  "https://pandas.pydata.org/docs/",
                  "https://github.com/pandas-dev/pandas", "")