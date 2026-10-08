# FinBase Customer Support Assistant

A simple RAG system over the six provided FinBase policy PDFs (personal loans,
credit cards, savings, fixed deposits, payments/UPI, KYC & security).
The assistant answers using only sentences quoted from the documents, shows the
source under every answer, and refuses or discloses when the knowledge base
cannot answer.

## Run it

    pip install pypdf numpy sentence-transformers streamlit

1. open finbase_build.ipynb in Jupyter, Run All  -> builds the work/ folder
2. streamlit run app.py  -> the chat interface

## Pipeline and choices

1. extract  - pypdf (~506k chars over 6 docs)
2. clean    - removed 138 table-of-contents link lines, fixed 3,888 broken
              characters (the pdf turned rupees into black squares and bullets
              into a control char), rejoined 2,863 wrapped lines
3. chunk    - structure-aware: split on section headings and on the 100 FAQ
              questions per doc; long sections cut at 180 words with 30 words
              overlap so no sentence is sliced. -> 771 chunks (600 are FAQs)
4. embed    - all-MiniLM-L6-v2 (384 dims); chosen because it runs on a laptop
              cpu in ~30 seconds and is good enough for short policy text
5. search   - brute-force cosine over a numpy matrix (no vector db needed at
              this scale) + a small citation-title bonus, top-5
6. answer   - extractive: quote the 2 sentences per source that share the most
              words with the question, tagged [S1]..[S5]. no free-form writing,
              so the system cannot invent facts
7. honesty  - refuse when 3+ question words never appear in the corpus or the
              best match is weak; disclose when a product is missing (home
              loan, NRI, locker, ...)

## Evaluation (my own golden set, written by reading the real text)

5 answerable + 8 trap questions (golden_set.json):
- retrieval hit@1 / hit@3 / hit@5 = 1.0
- answer fact coverage = 1.0
- traps refused or disclosed = 8/8

known weaknesses (honest):
- "how do i escalate a complaint" retrieves loan FAQs, not the grievance
  section - dense search confuses generic words; hybrid BM25 is the next step
- the word "gold" appears in the corpus, so the vocabulary check cannot flag
  a "gold loan" question; an entity list would fix it
- extractive answers read stiff; an LLM would smooth them but adds risk

## Files

- finbase_build.ipynb  pipeline + evaluation
- app.py               streamlit chat ui
- golden_set.json / eval_report.md   my eval set and results
- work/                chunks.jsonl, vectors.npy, final_numbers.json
- data/raw/            the six provided pdfs
