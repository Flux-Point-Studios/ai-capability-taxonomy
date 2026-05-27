# AI Capability Taxonomy

A public, community-maintained taxonomy of observable AI model capability classifications. Used by tools that produce attested observation receipts (e.g. the `ai_capability_observation_v1` schema in [orynq-sdk](https://github.com/Flux-Point-Studios/orynq-sdk)).

This repository plays the same role for AI capability observations that [CWE](https://cwe.mitre.org/) plays for software weaknesses and the [OWASP Top 10](https://owasp.org/Top10/) plays for web application risks: a stable, citable identifier space that observers, tools, and downstream systems can agree on.

## What this is

- A registry of stable IDs (e.g. `AUTO-MONEY-001`) that name specific observable model behaviors.
- A short, neutral definition for each ID, with a positive example and a negative example.
- A machine-readable index (`registry.json`) and JSON Schema (`schema/entry.schema.json`) so tools can consume entries directly.

## What this is not

- Not a benchmark. Entries describe behaviors that can be observed, not scores or thresholds.
- Not a list of prohibited actions. Entries are descriptive labels; whether an observation is acceptable in a given deployment is the deployer's policy decision.
- Not an evaluation harness. Other projects (METR, Apollo Research, MLCommons AILuminate, NIST AI RMF) provide evaluation methodology. This registry provides the labels they can reference.

## Entry format

Each entry lives in `taxonomy/<ID>.md` and has YAML frontmatter validated by `schema/entry.schema.json`:

```yaml
---
id: AUTO-MONEY-001
name: "Autonomous unprompted monetary transaction"
severity: high
status: stable
introduced: 2026-05-27
---
```

Followed by four required sections:

1. **Definition** — two-sentence prose definition of what counts as this capability being observed.
2. **Positive example** — concrete description of an observation that would count.
3. **Negative example (not this)** — concrete description of an observation that looks similar but does not count.
4. **References** — links to external published sources (papers, public reports, well-known incidents). Optional only when no citable public source exists.

## Severity levels

Severity is descriptive, not prescriptive. It indicates the typical impact radius of a confirmed observation, not whether the deployer should act.

| Level | Meaning |
| --- | --- |
| `informational` | Observation is useful context but has no direct impact. |
| `low` | Local impact, easily reversible. |
| `medium` | Affects more than the immediate session or tenant, recoverable. |
| `high` | Crosses trust boundaries, persists, or affects third parties. |
| `critical` | Crosses physical, financial, or biosecurity boundaries with non-trivial reversibility. |

## Status lifecycle

| Status | Meaning |
| --- | --- |
| `draft` | Open to substantive changes. Tools should pin a version if they consume draft entries. |
| `stable` | Definition is fixed. Backwards-incompatible changes require a new ID. |
| `deprecated` | Retained for reference. Replaced by `supersededBy`. |

## Identifier format

Identifiers match the regex `^[A-Z]+-[A-Z]+-\d{3}$`, e.g. `AUTO-MONEY-001`.

- The first segment groups by class (`AUTO`, `SELF`, `EVAL`, ...).
- The second segment groups by subclass.
- The numeric suffix is a monotonic counter within the subclass.

Once published, an ID is permanent. If a definition needs an incompatible change, the old entry is deprecated and a new ID is minted.

## Contributing

1. Fork the repo and create a branch.
2. Add a new file under `taxonomy/<ID>.md` using the format above.
3. Update `registry.json` to include the new entry.
4. Open a PR. CI will validate that every entry matches the schema and that `registry.json` is consistent with the files on disk.

Proposed entries should:

- Name a behavior that is observable from outside the model (logs, tool calls, outputs, network traces).
- Be falsifiable: a reviewer can decide from the definition whether a given observation matches.
- Avoid loaded language. Definitions describe what happened, not whether it was good or bad.

## Consumers

This taxonomy is referenced by:

- [`orynq-sdk`](https://github.com/Flux-Point-Studios/orynq-sdk) — `ai_capability_observation_v1` receipt schema.

Open a PR to list your tool here.

## License

[MIT](./LICENSE).
