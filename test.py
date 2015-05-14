import datetime
import random
import re
import sys

from jinja2 import Environment, FileSystemLoader

NUM_QUESTIONS = 10
QUESTIONS_FILE = "questions.txt"
TEMPLATE_FILE = "sections.html"
OUT_TEST_FILE = "test_raw.html"
OUT_SOL_FILE = "test_sol.html"


def err(txt):
    sys.stderr.write("%s\n" % txt)
    sys.exit(1)


def parse(txt):
    ret = []

    for (lnum, line) in enumerate(txt.split("\n")):
        m = re.match("^(S:|Q:|\+|\-)(.*)$", line)

        if m is not None:
            (token, data) = m.groups()

            # TODO: detect encoding errors
            data.decode("ascii")

            if token == "S:":
                d = {"text": data, "questions": []}
                ret.append(d)

            elif token == "Q:":
                d = {"text": data, "options": []}

                if len(ret) > 0:
                    ret[-1]["questions"].append(d)
                else:
                    err("Error in line %d:\nExpecting 'S:' found '%s'" % (lnum+1, line))

            elif token in "+-":
                d = {"text": data, "correct": token == "+"}

                if len(ret) > 0:
                    if len(ret[-1]["questions"]) > 0:
                        ret[-1]["questions"][-1]["options"].append(d)
                    else:
                        err("Error in line %d:\nExpecting 'Q:' found '%s'" % (lnum+1, line))
                else:
                    err("Error in line %d:\nExpecting 'S:' found '%s'" % (lnum+1, line))

        elif len(ret) > 0:
            d["text"] += line

    return ret


def filter_and_shuffle(test):
    for section in test:
        random.shuffle(section["questions"])

        section["questions"] = section["questions"][:NUM_QUESTIONS]

        for question in section["questions"]:
            random.shuffle(question["options"])

    return test

#
#
#

test = filter_and_shuffle(parse(open(QUESTIONS_FILE).read()))

env = Environment(loader=FileSystemLoader('.'), autoescape=True)

template = env.get_template(TEMPLATE_FILE)

open(OUT_TEST_FILE, "w").write(template.render(test=test, solutions=False))
open(OUT_SOL_FILE, "w").write(template.render(test=test, solutions=True))
