# social-data-experiments

[日本語](./README.md)

A place for small, reproducible checks in computational social science.
An experiment is added only when it goes by one of the routes that rule 15 of cpsbvbng26-dotcom names.
This repository is not part of the self-taught series.
There are 0 experiments now.
Neither experiments nor data are made up to fill it.
The place was set up on 2026-11-20.

The archive is on Zenodo. The DOI of the first version is [`10.5281/zenodo.24397158`](https://doi.org/10.5281/zenodo.24397158), and the DOI common to all versions is [`10.5281/zenodo.24397157`](https://doi.org/10.5281/zenodo.24397157).

## Rules

- Under rule 15 of cpsbvbng26-dotcom, the self-taught work is what was done up to the first undergraduate year.
- No new topic is added to the self-taught series.
- An experiment is added only when it goes by one of the routes that rule 15 names.
- The routes are joint research, JOSS, conference presentations and diamond open access venues.
- An experiment without a route is not added.
- Nothing goes to a venue that charges for publishing or for submitting, under rule 14 of cpsbvbng26-dotcom.
- The plan is fixed before the data are seen, with the date.
- A change to the plan adds the date and the reason; the earlier plan is not deleted.
- Results are written even when the question could not be answered.
- When the subject is social institutions or education policy, the disclosure comes first. This follows the section on dormant conflicts of interest in the [record of conflicts of interest](https://github.com/cpsbvbng26-dotcom/cpsbvbng26-dotcom/blob/main/docs/conflicts-of-interest.en.md) of cpsbvbng26-dotcom.

## The template of an experiment

Each experiment is kept in a directory of its own in `experiments/`.
Each directory holds the documents and the fields copied from the templates in `template/`.

| File | Content |
| --- | --- |
| [`template/experiment.md`](./template/experiment.md) | The document of the experiment, in Japanese |
| [`template/experiment.en.md`](./template/experiment.en.md) | The document of the experiment, in English |
| [`template/experiment.json`](./template/experiment.json) | The fields of the experiment |

The headings of the document come in this order.

| Heading | What it holds |
| --- | --- |
| Question | A question in a form that can be checked |
| Route | One of the routes that rule 15 names |
| Data source and licence | Where the data are, the licence, when and where it was checked, and that the data hold no personal data |
| Method | What is counted and how it is compared; the tools and their versions |
| Plan fixed in advance | The question, hypotheses, analysis and condition for stopping, fixed before the data are seen, with the date |
| Code | Where the code is and how the results are made again; the seed of random numbers |
| Results | The planned analysis first; analyses not in the plan set apart |
| Limits | What cannot be said |
| Disclosure | Conflicts of interest, and the use of language models |

| Field | Content |
| --- | --- |
| `name` | The name of the experiment, the same as its directory |
| `status` | One of `planned`, `running`, `done`, `withdrawn` |
| `route` | One of `collaboration`, `joss`, `conference`, `diamond-oa` |
| `question` | The question |
| `data_source` | Where the data are |
| `data_licence` | The licence of the data |
| `licence_checked` | The date the licence was checked |
| `personal_data` | Only `none` |
| `plan_fixed` | The date the plan was fixed |
| `results_written` | The date the results were written, after the plan was fixed |
| `code` | Where the code is |

## Data ethics

- No personal data are used.
- Nor are data that identify a person, or that can be turned back into a form that does.
- Only published data are used.
- No new survey or collection of data about people is made.
- The licence of the data is checked before use; the licence, and when and where it was checked, go into the record.
- Data whose licence does not allow redistribution are not kept here; only where they are and how to get them is written.
- No data are taken from a place whose terms forbid taking them by machine.
- Data are not combined so as to make a person identifiable.

## Checks

```
python3 verification/check.py            # the template's headings and fields, each experiment's fields, route and dates, data ethics, rules, copies, writing, numbers
python3 verification/check.py --break    # break each check once and see it fail
```

While there is no experiment, the check of an experiment's fields is run on sample experiments made inside the check, to see it pass and fail.
CI runs the checks on every push and pull request.

## Operator

The operator is Takuya Nemoto (根本卓哉).
ORCID iD: [0009-0000-1406-0547](https://orcid.org/0009-0000-1406-0547).
Errors are received through the [error report](https://github.com/cpsbvbng26-dotcom/social-data-experiments/issues/new?template=error-report.yml) form.
Security issues are received by the route in [SECURITY.md](./SECURITY.md).

## Use of language models

The use of language models is set out in the same table as in the other repositories.

| Tool | Used for | Checked by |
| --- | --- | --- |
| Claude Code (Anthropic) | The rules, the templates, the data ethics, README text, the checks in `verification/` | The checks of `verification/check.py`; there is no record of the operator reading and checking it |

Claude is not an author.

## Licence

The text and the templates are [CC BY 4.0](./LICENSE); the code is [MIT](./LICENSE-CODE).
