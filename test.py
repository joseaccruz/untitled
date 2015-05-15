import datetime
import random
import re
import sys

from jinja2 import Environment, FileSystemLoader


time_code = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

DEBUG = True
ALL_QUESTIONS = True
NUM_QUESTIONS = 10
QUESTIONS_FILE = "questions.txt"
TEMPLATE_FILE = "sections.html"

if DEBUG:
    OUT_FILE_RAW = "debug_raw.html"
    OUT_FILE_SOL = "debug_sol.html"
else:
    OUT_FILE_RAW = "test_raw_%s.html" % time_code
    OUT_FILE_SOL = "test_sol_%s.html" % time_code


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
            d["text"] += "\n" + line

    return ret


def filter_and_shuffle(test):
    for section in test:
        random.shuffle(section["questions"])

        section["questions"] = section["questions"][:NUM_QUESTIONS]

        for question in section["questions"]:
            random.shuffle(question["options"])

    return test

#
# MAIN
#


test = parse(open(QUESTIONS_FILE).read())

print "\nTest database summary:"
print "------------------------\n"

for section in test:
    print "\t%s - %d questions" % (section["text"], len(section["questions"]))

if not ALL_QUESTIONS:
    test = filter_and_shuffle(test)

env = Environment(loader=FileSystemLoader('.'), autoescape=True)

template = env.get_template(TEMPLATE_FILE)

open(OUT_FILE_RAW, "w").write(template.render(test=test, solutions=False))
open(OUT_FILE_SOL, "w").write(template.render(test=test, solutions=True))

print "\nTest generated:"
print "-----------------\n"

print "Question database:        '%s'" % QUESTIONS_FILE
print "Test file for candidate:  '%s'" % OUT_FILE_RAW
print "Test file with solutions: '%s'" % OUT_FILE_SOL

print ""
