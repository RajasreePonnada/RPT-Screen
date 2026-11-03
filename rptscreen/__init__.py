"""rptscreen: related-party screening from the statutory auditor's vantage point.

Design rule enforced throughout: probabilistic components (resolver, extractor,
indicators) may only write edges with confidence < 1 or emit signals. Only the
rule engine applies law, and only humans form conclusions.
"""
