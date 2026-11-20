#!/usr/bin/env python3
"""The checks of social-data-experiments.

  python3 verification/check.py            the template, every experiment, the rules and data ethics, copies, writing, numbers
  python3 verification/check.py --break    every check fails when the thing it watches is broken

An experiment is a directory experiments/<name>/ with experiment.md, experiment.en.md and experiment.json copied from
template/. It needs a route that rule 15 of cpsbvbng26-dotcom names, data with no personal data and a checked licence,
and a plan fixed before the results. There are no experiments now; the check of an experiment is run on sample
experiments made here, which must pass and fail as expected, so that the check is neither empty nor too strict.
"""
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rules  # noqa: E402
from rules import add, jload, sub  # noqa: E402

PROSE = ["README.md", "README.en.md", "template/experiment.md", "template/experiment.en.md", "experiments/README.md", "experiments/README.en.md"]
HEADS_JA = ["問い", "経路", "データの出所とライセンス", "方法", "事前の計画", "コード", "結果", "限界", "開示"]
HEADS_EN = ["Question", "Route", "Data source and licence", "Method", "Plan fixed in advance", "Code", "Results", "Limits", "Disclosure"]
FIELDS = ["name", "status", "route", "question", "data_source", "data_licence", "licence_checked", "personal_data", "plan_fixed",
          "results_written", "code"]
STATUS = ["planned", "running", "done", "withdrawn"]
ROUTES = ["collaboration", "joss", "conference", "diamond-oa"]
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
DATA_EXT = (".csv", ".tsv", ".parquet", ".xlsx", ".xls", ".sav", ".dta", ".rds", ".feather", ".sqlite", ".db", ".zip", ".gz")


def today():
    return datetime.date.today().isoformat()


def heads(text):
    return re.findall(r"^## (.+)$", text, re.M)


def experiment_names(F):
    return sorted({f.split("/")[1] for f in F if re.match(r"^experiments/[^/]+/", f)})


def template(F):
    bad = []
    if heads(F.get("template/experiment.md", "")) != HEADS_JA:
        bad.append("template/experiment.md: the headings are not the nine in order")
    if heads(F.get("template/experiment.en.md", "")) != HEADS_EN:
        bad.append("template/experiment.en.md: the headings are not the nine in order")
    T = jload(F, "template/experiment.json")
    if T is None or [k for k in T if k != "_"] != FIELDS:
        bad.append("template/experiment.json: the fields")
    elif T["personal_data"] != "none" or T["status"] != "planned" or any(T[k] is not None for k in FIELDS if k not in ("personal_data", "status")):
        bad.append("template/experiment.json: a template holds no values but the defaults")
    for f, head, names in (("README.md", "| 見出し | 書くこと |", HEADS_JA), ("README.en.md", "| Heading | What it holds |", HEADS_EN)):
        rows = table_first_column(F.get(f, ""), head)
        if rows != names:
            bad.append(f + ": the table of headings is not the template's")
    for f, head in (("README.md", "| 欄 | 中身 |"), ("README.en.md", "| Field | Content |")):
        rows = [re.sub(r"`", "", r) for r in table_first_column(F.get(f, ""), head) or []]
        if rows != FIELDS:
            bad.append(f + ": the table of fields is not the template's")
    for f in ("README.md", "README.en.md"):
        t = F.get(f, "")
        for v in STATUS + ROUTES:
            if "`%s`" % v not in t:
                bad.append(f + ": the value %s is not listed" % v)
    return bad


def table_first_column(text, head):
    i = text.find("\n" + head + "\n")
    if i < 0:
        return None
    out = []
    for line in text[i + 1:].split("\n")[2:]:
        if not line.startswith("|"):
            break
        out.append(line.strip().strip("|").split(" | ")[0].strip())
    return out


def one_experiment(F, name):
    bad = []
    base = "experiments/%s/" % name
    md, en, js = F.get(base + "experiment.md"), F.get(base + "experiment.en.md"), jload(F, base + "experiment.json")
    if md is None or en is None or js is None:
        return [name + ": experiment.md, experiment.en.md and experiment.json are all needed"]
    if heads(md) != HEADS_JA or heads(en) != HEADS_EN:
        bad.append(name + ": the headings are not the template's")
    if [k for k in js if k != "_"] != FIELDS:
        bad.append(name + ": the fields are not the template's")
        return bad
    if js["name"] != name:
        bad.append(name + ": the name is not the directory's")
    if js["status"] not in STATUS:
        bad.append(name + ": a status outside the vocabulary")
    if js["route"] not in ROUTES:
        bad.append(name + ": no route that rule 15 names")
    if js["personal_data"] != "none":
        bad.append(name + ": personal data")
    for k in ("question", "data_source", "data_licence", "code"):
        if not isinstance(js[k], str) or not js[k].strip():
            bad.append(name + ": " + k + " is empty")
    for k in ("licence_checked", "plan_fixed"):
        if not isinstance(js[k], str) or not DATE.fullmatch(js[k]) or js[k] > today():
            bad.append(name + ": " + k + " is not a date up to today")
    r = js["results_written"]
    if r is not None:
        if not isinstance(r, str) or not DATE.fullmatch(r) or r > today():
            bad.append(name + ": results_written is not a date up to today")
        elif isinstance(js["plan_fixed"], str) and r < js["plan_fixed"]:
            bad.append(name + ": the results were written before the plan was fixed")
        if isinstance(js["licence_checked"], str) and js["licence_checked"] > r:
            bad.append(name + ": the licence was checked after the results")
    if js["status"] == "done" and r is None:
        bad.append(name + ": done without results")
    if js["status"] == "planned" and r is not None:
        bad.append(name + ": results while only planned")
    return bad


def experiments(F):
    """Every experiment follows the template and the rules. The same function is run on a valid sample, which must pass,
    and on broken samples, each of which must fail; otherwise the check would be empty or too strict."""
    bad = []
    for n in experiment_names(F):
        bad += one_experiment(F, n)
    sample = sample_experiment(F)
    if sample is None:
        return bad + ["the template cannot be copied into a sample experiment"]
    got = one_experiment(sample, "sample")
    if got:
        bad.append("a valid sample experiment fails: " + "; ".join(got))
    for k, v in (("route", "self-taught"), ("personal_data", "pseudonymised"), ("results_written", "2000-01-01"), ("data_licence", "")):
        s = dict(sample)
        j = json.loads(s["experiments/sample/experiment.json"])
        j[k] = v
        s["experiments/sample/experiment.json"] = json.dumps(j, ensure_ascii=False)
        if not one_experiment(s, "sample"):
            bad.append("a sample experiment with %s = %r passes" % (k, v))
    return bad


def sample_experiment(F):
    T = jload(F, "template/experiment.json")
    if T is None or "template/experiment.md" not in F or "template/experiment.en.md" not in F:
        return None
    j = {k: T.get(k) for k in FIELDS}
    j.update({"name": "sample", "status": "done", "route": "joss", "question": "q", "data_source": "s", "data_licence": "l",
              "licence_checked": "2026-01-01", "plan_fixed": "2026-01-02", "results_written": "2026-01-03", "code": "c"})
    return {"experiments/sample/experiment.md": F["template/experiment.md"], "experiments/sample/experiment.en.md": F["template/experiment.en.md"],
            "experiments/sample/experiment.json": json.dumps(j, ensure_ascii=False)}


def no_data(F, paths=None):
    """No data file anywhere but inside an experiment's directory; with no experiment, no data at all. No data are made up."""
    bad = []
    for p in (paths if paths is not None else all_paths()):
        if p.lower().endswith(DATA_EXT) and not re.match(r"^experiments/[^/]+/data/", p):
            bad.append(p + ": a data file outside an experiment")
    for f in F:
        if f.endswith(".json") and not (f.startswith((".github/", "verification/", "template/")) or f == ".zenodo.json"
                                        or re.match(r"^experiments/[^/]+/(experiment\.json|data/)", f)):
            bad.append(f + ": a data file outside an experiment")
    return bad


def all_paths():
    out = []
    for dp, dns, fns in os.walk(rules.ROOT):
        dns[:] = [d for d in dns if d not in rules.SKIP_DIRS]
        out += [os.path.relpath(os.path.join(dp, fn), rules.ROOT).replace(os.sep, "/") for fn in fns]
    return out


RULES = {
    "README.md": ["このリポジトリは、独学の系列に入りません。", "独学の系列に、新しい主題を足しません。",
                  "実験は、決めごと 15 が挙げる経路のどれかで進めるときだけ置きます。",
                  "経路は、共同研究・JOSS・学会発表・ダイヤモンド・オープンアクセスの場です。", "経路が決まっていない実験は、置きません。",
                  "掲載料や投稿料を取る場には出しません。", "実験もデータも、作り上げて置くことはしません。",
                  "事前の計画は、データを見る前に固め、その日を書きます。", "結果は、問いに答えられなかったときも書きます。",
                  "(https://github.com/cpsbvbng26-dotcom/cpsbvbng26-dotcom/blob/main/docs/conflicts-of-interest.md)"],
    "README.en.md": ["This repository is not part of the self-taught series.", "No new topic is added to the self-taught series.",
                     "An experiment is added only when it goes by one of the routes that rule 15 names.",
                     "The routes are joint research, JOSS, conference presentations and diamond open access venues.",
                     "An experiment without a route is not added.", "Neither experiments nor data are made up to fill it.",
                     "The plan is fixed before the data are seen, with the date.", "Results are written even when the question could not be answered.",
                     "(https://github.com/cpsbvbng26-dotcom/cpsbvbng26-dotcom/blob/main/docs/conflicts-of-interest.en.md)"],
}
ETHICS = {
    "README.md": ["個人のデータを使いません。", "公開されたデータだけを使います。", "人を対象にした調査や収集を、新しくすることはしません。",
                  "データのライセンスを確かめてから使います。", "再配布を許さないデータは、ここに置きません。",
                  "機械での取得を規約が禁じる場からは、データを取りません。", "複数のデータを組み合わせて、人を特定できるようにすることはしません。"],
    "README.en.md": ["No personal data are used.", "Only published data are used.", "No new survey or collection of data about people is made.",
                     "The licence of the data is checked before use", "Data whose licence does not allow redistribution are not kept here",
                     "No data are taken from a place whose terms forbid taking them by machine.", "Data are not combined so as to make a person identifiable."],
}


def rules_and_ethics(F):
    bad = []
    for D, sec in ((RULES, {"README.md": "## 決めごと", "README.en.md": "## Rules"}), (ETHICS, {"README.md": "## データの倫理", "README.en.md": "## Data ethics"})):
        for f, must in D.items():
            t = F.get(f, "")
            i = t.find("\n" + sec[f] + "\n")
            body = t[:t.find("\n## ")] + (t[i:t.find("\n## ", i + 3)] if i >= 0 else "")
            for s in must:
                if s not in body:
                    bad.append(f + ": lacks「" + s[:24] + "」")
    return bad


COUNTERS = {"experiments": lambda F: len(experiment_names(F))}

CHECKS = [
    ("The template: the nine headings in order in both languages, the fields, and the READMEs' tables of both", template),
    ("Every experiment follows the template, has a route of rule 15, no personal data, a checked licence and a plan before results (and the check passes and fails on samples)", experiments),
    ("No data file outside an experiment; with no experiment, no data", lambda F: no_data(F)),
    ("The rules (rule 15, the routes, nothing made up, the plan, rule 14) and the data ethics, in both READMEs", rules_and_ethics),
    ("Copies of the canonical files and the licences are byte-identical (sha256)", rules.copies),
    ("No name of the operator's own university in any spelling, other place of creative work, self-title, item of rule 10 or single relative", rules.words_not_written),
    ("No subject that these repositories do not write about", rules.topics_not_written),
    ("No list of work for the operator", rules.no_tasks),
    ("No e-mail address in any file", rules.no_email),
    ("Workflows: actions pinned to commits, permissions, timeouts; Dependabot", rules.workflows),
    ("labels.yml makes the labels of the canonical workflows", lambda F: rules.labels(F)),
    ("CLAUDE.md carries rules 16, 17 and 18 (10 times)", rules.claude_md),
    ("The writing rules: です/ます, no second person, no bold, one dash per paragraph, short sentences", lambda F: rules.prose(F, PROSE)),
    ("Every number in prose is in the ledger of numbers, and every count matches the experiments", lambda F: rules.numbers(F, PROSE, COUNTERS, ("README.md", "README.en.md"))),
    ("README.md and README.en.md link each other, disclose the language model and name the licences", rules.readme_pair),
    (".zenodo.json: one creator with the ORCID iD, the licence of LICENSE, the disclosure, the licence sentence, related identifiers found in the repository", rules.zenodo),
]


def _add_experiment(**over):
    def mut(G):
        s = sample_experiment(G)
        j = json.loads(s["experiments/sample/experiment.json"])
        j.update(over)
        s["experiments/sample/experiment.json"] = json.dumps(j, ensure_ascii=False)
        G.update(s)
    return mut


def _swap_template_heads(G):
    G["template/experiment.md"] = G["template/experiment.md"].replace("## 方法\n", "## 方法の前\n", 1).replace("## 事前の計画\n", "## 方法\n", 1).replace("## 方法の前\n", "## 事前の計画\n", 1)


C = [c[0] for c in CHECKS]
BREAKS = [
    (C[0], "the template drops the plan fixed in advance", sub("template/experiment.md", "## 事前の計画\n", "## 計画\n")),
    (C[0], "the template puts the plan after the method", _swap_template_heads),
    (C[0], "the English template drops the limits", sub("template/experiment.en.md", "## Limits\n", "## Notes\n")),
    (C[0], "the template allows personal data", sub("template/experiment.json", '"personal_data": "none"', '"personal_data": "some"')),
    (C[0], "README.md lists a field the template lacks", sub("README.md", "| `code` | コードの所在 |", "| `repo` | コードの所在 |")),
    (C[1], "an experiment with no route of rule 15", _add_experiment(route="self-taught")),
    (C[1], "an experiment with personal data", _add_experiment(personal_data="pseudonymised")),
    (C[1], "an experiment whose results come before its plan", _add_experiment(plan_fixed="2026-02-01", results_written="2026-01-15")),
    (C[1], "an experiment with no licence", _add_experiment(data_licence="")),
    (C[1], "an experiment done without results", _add_experiment(results_written=None)),
    (C[1], "an experiment with only the Japanese document", lambda G: (_add_experiment()(G), G.pop("experiments/sample/experiment.en.md"))),
    (C[2], "a data file with no experiment", add("data/survey.json", "{}")),
    (C[2], "a CSV outside an experiment", lambda G: G.__setitem__("__paths__", ["data/survey.csv"])),
    (C[3], "README.md drops rule 15", sub("README.md", "このリポジトリは、独学の系列に入りません。\n", "")),
    (C[3], "README.en.md adds a route", sub("README.en.md", "The routes are joint research, JOSS, conference presentations and diamond open access venues.", "The routes are joint research, JOSS, conference presentations, diamond open access venues and the self-taught series.")),
    (C[3], "README.md drops a rule of data ethics", sub("README.md", "- 機械での取得を規約が禁じる場からは、データを取りません。\n", "")),
    (C[3], "README.en.md drops the rule on personal data", sub("README.en.md", "- No personal data are used.\n", "")),
    (C[4], "one character of SECURITY.md", sub("SECURITY.md", "7 日以内", "8 日以内")),
    (C[5], "the university's name in hiragana", add("README.md", "\n" + rules.dec("44Gc44KT") + rules.dec("44Gg44GE44GM44GP") + "\n")),
    (C[5], "a self-title", add("README.en.md", "\n" + rules.dec("aW5kZXBlbmRlbnQ=") + " " + rules.dec("cmVzZWFyY2hlcg==") + "\n")),
    (C[6], "a political organisation", add("template/experiment.md", "\n" + rules.dec("5Zu95rCR5rCR5Li7") + "\n")),
    (C[6], "a degree these repositories do not write about", add("README.en.md", "\n" + rules.dec("TUJB") + "\n")),
    (C[7], "a list of work for the operator", add("README.en.md", "\nThe owner " + "must check the licence.\n")),
    (C[8], "an e-mail address", add("template/experiment.json", "\nwriter" + "@" + "example.com\n")),
    (C[9], "an action named by its version", sub(".github/workflows/check.yml", "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1", "actions/checkout@v7")),
    (C[10], "labels.yml drops a label", sub(".github/workflows/labels.yml", 'gh label create "needs a person"', 'gh label create "person"')),
    (C[11], "CLAUDE.md loses rule 16", sub("CLAUDE.md", "**Claude は利用者に命令しない。**", "**Claude は丁寧に書く。**")),
    (C[12], "a sentence not in です/ます", add("template/experiment.md", "\n問いは絞る。\n")),
    (C[12], "an instruction", add("README.md", "\n雛形を写してください。\n")),
    (C[13], "a count that differs from the experiments", sub("README.md", "いまは、実験は 0 件です。", "いまは、実験は 2 件です。")),
    (C[13], "a number not in the ledger of numbers", add("template/experiment.md", "\n問いは 3 行までにします。\n")),
    (C[14], "README.md drops the disclosure", sub("README.md", "Claude は著者ではありません。", "Claude が手伝いました。")),
    (C[15], ".zenodo.json names the MIT licence", sub(".zenodo.json", '"license": "cc-by-4.0"', '"license": "mit"')),
    (C[15], ".zenodo.json drops the name of the repository from the title", sub(".zenodo.json", '"title": "social-data-experiments: ', '"title": "')),
]

if __name__ == "__main__":
    F = rules.load()
    if "--break" in sys.argv:
        # The break of a data file outside an experiment hands its own list of paths to the check.
        CHECKS[2] = (C[2], lambda G: no_data(G, G.pop("__paths__", None)))
    sys.exit(rules.run(CHECKS, BREAKS, F, sys.argv))
