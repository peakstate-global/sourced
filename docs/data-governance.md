# The seven, in the language of the function that already owns six

Six of the seven checks are data-governance disciplines under different names. The disciplines are
decades old. What is new is pointing them at what a system **produces** rather than what it
**consumes**.

This page is the argument for recruiting the data governance function rather than standing up a new
one.

## The crosswalk

| | We call it | You call it | Today it is pointed at | Pointing it at output means |
|---|---|---|---|---|
| **S** | Sourced | Lineage and provenance | Where a field in a table came from, and through what transformations | Where a sentence in a deliverable came from, quoted and located, with a hash so you can tell when the source moves |
| **O** | Opposed | **No equivalent** | Nothing. Data governance has no discipline of adversarial challenge | Something has to try to break the answer, and it has to be a different model. This is the one check genuinely being added |
| **U** | Underwritten | Ownership and stewardship | A named owner for a data asset, appointed before anything goes wrong | A named person for a deliverable, who signs what they personally verified rather than that they reviewed it |
| **R** | Recorded | Audit trail | Who changed what, when, in the system of record | What was decided and rejected while the work happened, plus the model, version and tools. Written during, because a reason reconstructed afterwards is a story |
| **C** | Constrained | Policy enforcement | Access rules, masking, loss prevention. Deny by default on classes you have named | The same, on what the system is allowed to assert. Fail closed and fail visibly, because a silently weakened answer is worse than a refusal |
| **E** | Evaluated | Data quality monitoring | Rules and thresholds on an asset, re-run on a schedule, alerting on drift | Examples with known answers, re-run when the model, prompt, index or tools change, seeded from real failures rather than invented cases |
| **D** | Disclosed | Metadata and cataloguing | A dictionary and a catalogue, written for an engineer who needs to find and use the asset | A four-line block, written for a reader who needs to decide whether to rely on the output. Same instinct, different audience |

**O is the row that earns the page.** Marking it as having no equivalent is what stops the crosswalk
reading as a rebrand of work somebody else already does.

## Where the line falls

> **Data governance asks whether the data is fit, permitted and looked after.
> AI governance asks whether the behaviour is justified, bounded and answerable.**

| | Data governance | AI governance |
|---|---|---|
| Object | The asset: records, stores, flows | The behaviour: inference and its outputs |
| Question | Is this data accurate, permitted, classified, retained, access-controlled? | Should this system act, is it bounded, who answers for what it produced? |
| Failure looks like | A breach, a stale record, an unlawful transfer | A confident wrong answer, an unfair decision, nobody accountable |
| Determinism | Assumes the same input gives the same result | Exists **because** it does not |
| Settles when | The asset is correct and controlled | Never. The system changes underneath you, which is what E is for |

The overlap is narrow and specific: **training corpora, retrieval indexes, and prompt logs**. Those
are data assets *and* determinants of behaviour, so both disciplines claim them. Everything else
divides cleanly.

**Data governance can be fully satisfied by a system nobody can explain. AI governance cannot be
satisfied by data nobody can defend.** Necessary, not sufficient, in that direction only.

## What is actually being asked for

- **Not a new function.** Six of the seven are disciplines the organisation already staffs, funds and
  audits. The ask is a second target for them, not a second team.
- **Four of the seven have no manual version at volume.** Sourced, Recorded, Constrained and
  Evaluated cannot be done by a person reading outputs once volume passes what anybody reads. Those
  four are engineering work, and naming them as engineering work is how they get funded.
- **The output side has no owner today.** Ask who owns what comes out of a system and the answer is
  usually a team, a process, or a vendor. A team cannot be answerable.
- **Start with D, because it is the interface.** Without a disclosure block the other six are private
  practice a reader cannot act on. It is also the cheapest.

## The objection, and the answer

> **"We already have data governance, this is covered."**

Agree completely. The muscles are there and this is not a new discipline being sold to anybody. Every
one of them is pointed at what goes into a system, and nothing is pointed at what comes out. That is
the whole of the ask.

## Limitations

**This crosswalk is a reading, not a published mapping.** No data-management standard sets out a
correspondence between these disciplines and AI output assurance, and none was retrieved. The
discipline names are the ordinary industry ones; they are not quoted from a specification. Expect a
data governance professional to argue with at least one row, and treat that as the conversation
working.
