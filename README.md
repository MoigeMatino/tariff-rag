# tariff-rag

Status: in progress

A question-answering assistant over Co-op Bank Kenya's published tariff guide. It answers with
citations to the source, says so when the answer is not in the guide, applies guardrails on input
and output, and logs latency, token usage and cost for every query.

## Run it

```bash
make install
cp .env.example .env   # add your Anthropic API key
# download the tariff guide named in data/source.json into data/raw/
make verify-source
make check
make inspect
```

## Design notes

Every significant choice and the evidence behind it is recorded in [DECISIONS.md](DECISIONS.md).
