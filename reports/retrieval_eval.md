# Retrieval eval

Answer key status: **draft**. Scores are provisional until the owner has checked the expected answers.
Corpus: 11 chunks from 6 sections (poster column 1 only). A hit is any chunk from the question's expected section.

## Answerable questions (10)

| Retriever | Hit@1 | Hit@3 | MRR |
|---|---|---|---|
| bm25 | 1.00 | 1.00 | 1.00 |
| vector: BAAI/bge-small-en-v1.5 | 0.90 | 1.00 | 0.95 |
| vector: BAAI/bge-small-en-v1.5 (no query prefix) | 0.90 | 1.00 | 0.95 |
| random ranking (expected) | 0.19 | 0.50 | n/a |

Rank of the first chunk from the expected section (1 is best):

| Question | Expected section | bm25 | vector: BAAI/bge-small-en-v1.5 | vector: BAAI/bge-small-en-v1.5 (no query prefix) |
|---|---|---|---|---|
| q01 What is the annual fee for a Co-op Bank Gold credit card? | card-fees | 1 | 1 | 1 |
| q02 How much does it cost to withdraw Ksh 15,000 at a Co-op Bank agent? | agency-banking | 1 | 1 | 1 |
| q03 What is the charge for sending Ksh 5,000 by Pesalink through an agent? | agency-banking | 1 | 1 | 1 |
| q04 How much is a balance inquiry at an agent? | agency-banking | 1 | 2 | 2 |
| q05 What is the monthly maintenance fee on a USD current account? | foreign-currency-accounts | 1 | 1 | 1 |
| q06 Is there a charge for depositing USD 50,000 cash into my foreign currency account? | foreign-currency-accounts | 1 | 1 | 1 |
| q07 What does the bank charge to buy Treasury bills on my behalf? | treasury-and-transfers | 1 | 1 | 1 |
| q08 How much is an outgoing RTGS transfer? | treasury-and-transfers | 1 | 1 | 1 |
| q09 What happens if I pay my credit card late? | card-fees | 1 | 1 | 1 |
| q10 What is the minimum opening balance for a YEA account? | yea-account | 1 | 1 | 1 |

## Can a score threshold detect fallback questions? (5 questions)

Top-1 score per question. A threshold can only separate the two groups if every fallback question scores below every answerable one.

| Retriever | Answerable: lowest top score | Fallback: highest top score | Separable |
|---|---|---|---|
| bm25 | 2.416 | 8.156 | no |
| vector: BAAI/bge-small-en-v1.5 | 0.578 | 0.707 | no |
| vector: BAAI/bge-small-en-v1.5 (no query prefix) | 0.593 | 0.743 | no |

| Question | bm25 | vector: BAAI/bge-small-en-v1.5 | vector: BAAI/bge-small-en-v1.5 (no query prefix) |
|---|---|---|---|
| q11 What is the arrangement fee for an overdraft? | 0.214 | 0.679 | 0.701 |
| q12 How much is the application fee for a Co-op Bank mortgage? | 2.135 | 0.614 | 0.628 |
| q13 What is today's US dollar to Kenya shilling exchange rate? | 3.315 | 0.619 | 0.639 |
| q14 How much does Equity Bank charge for an agent cash withdrawal of Ksh 10,000? | 3.371 | 0.707 | 0.743 |
| q15 Should I get a Gold or a Platinum credit card? | 8.156 | 0.605 | 0.638 |
