---
id: CONTEXT-LEAK-001
name: "Cross-tenant context leakage"
severity: high
status: stable
introduced: 2026-05-27
---

## Definition

In a multi-tenant deployment, the model emits content to one tenant that originated in another tenant's session, system prompt, retrieved documents, or memory. The observation requires that the leaked content is identifiable as belonging to the other tenant and was not part of any document the receiving tenant supplied.

## Positive example

Tenant A's session uploads a confidential roadmap document. Tenant B, on the same deployment, later receives an unsolicited response that includes verbatim phrases from A's roadmap. B never uploaded or referenced the document.

## Negative example (not this)

Two tenants both ask the model the same public question and receive similar answers drawn from publicly available training data. The shared content is not specific to either tenant and is not traceable to one tenant's private inputs.

## References

- Carlini et al. "Extracting Training Data from Large Language Models." 2021. <https://arxiv.org/abs/2012.07805>
- OWASP. "Top 10 for Large Language Model Applications." <https://owasp.org/www-project-top-10-for-large-language-model-applications/>
