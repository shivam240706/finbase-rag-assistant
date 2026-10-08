# FinBase RAG — Step-by-Step Checklist

One action per bullet. Tick them off in order. ✅ = a real checkpoint — at each one, paste your result to your tutor before moving on.

**You write the code; the tutor explains, debugs and reviews.** Where a bullet says *write file X*, the spec tells you **what** it must do — not the code.

**Command legend:** `python` = your Python 3.11+ command (`python3` on Mac/Linux). Activate-venv differs:
- Mac/Linux: `source .venv/bin/activate`
- Windows PowerShell: `.venv\Scripts\Activate.ps1`

---

## STAGE 0 — Setup + read the data (tonight, ~90 min)

- [ ] **0.1** Unzip `my-rag-starter.zip` somewhere you'll work. You now have `data/raw/` with the six PDFs.
- [ ] **0.2** Open a terminal in that folder. Create and activate a venv:
  - [ ] `python -m venv .venv`
  - [ ] activate it (see legend) → your prompt shows `(.venv)`
- [ ] **0.3** Install the first package: `pip install pypdf`
- [ ] **0.4** Start version control in the same folder:
  - [ ] `git init -b main`
  - [ ] create `.gitignore` (you write it) containing: `.venv/`, `__pycache__/`, `*.pyc`, `work/`
  - [ ] `git add -A && git commit -m "stage 0: starter setup"`
- [ ] **0.5** Create `work/` (your scratch output folder).
- [ ] **0.6** Write `extract.py` — spec:
  - loop over every `*.pdf` in `data/raw/`
  - for each: read it with pypdf, extract text page by page, join pages with a newline
  - save as `work/<pdf-name>.txt` (UTF-8)
  - print the filename and character count for each
  - *(hint: the class is `PdfReader`; each page has `.extract_text()` — that's all you need)* ~15 lines.
- [ ] **0.7** Run it: `python extract.py` → check you get 6 `.txt` files in `work/`.
  - [ ] If a file is empty or tiny, don't continue — paste the error/counts to your tutor.
- [ ] **0.8** `git add -A && git commit -m "stage 0: pdf extraction"`
- [ ] **0.9** Open one dump (pick `work/sample_5.txt`) and **read it end to end** — no skimming.
- [ ] **0.10** Write `JOURNAL.md` and start your defect list: for each defect write *what it looks like* + *one real example line copied from the dump*. Look carefully — there are at least 4 different kinds.
- [ ] **0.11** ✅ **CHECKPOINT 0** — paste your defect list to your tutor. Get it checked before Stage 1.

---

## STAGE 1 — Clean + chunk (~2 h)

- [ ] **1.1** Write `clean.py` with a function `clean(text) -> (clean_text, fix_counts)`:
  - [ ] write one small repair per defect from 0.10 (each as its own `re.sub`, adding to a counter dict)
  - [ ] print the total counts per fix at the end — these are real numbers you'll use in your video
  - [ ] test on one dump: `python -c "from clean import clean; t,c = clean(open('work/sample_5.txt').read()); print(c)"` (or a small `if __name__ == '__main__':` block)
- [ ] **1.2** Discover the document structure — run these and look:
  - [ ] `head -80 work/sample_5.txt` and `grep -n -i "^section\|^article\|^faq\|^Q" work/sample_5.txt | head -30`
  - [ ] write in your journal: exactly how are section headings formatted? how are FAQ questions/answers formatted? how do you know where a section begins and ends?
- [ ] **1.3** Write `chunk.py` — spec (adapt to what you found in 1.2):
  - [ ] split each document into sections using the heading pattern you found
  - [ ] if a section exceeds ~220 words/tokens, split it further with ~10–20% overlap (state your numbers in the journal)
  - [ ] FAQ blocks: make **one chunk per Q&A pair**
  - [ ] each chunk gets metadata: a unique `chunk_id`, the doc name, section number + title, and a pre-built **citation string** like `"Personal Loan Policy — Section 6.2 — Foreclosure Charges"` (you'll display this to users!)
- [ ] **1.4** Write the chunks to `chunks.jsonl` (one JSON object per line). Run it.
- [ ] **1.5** Print 5 random chunks and read them:
  - [ ] does each chunk make sense alone, without its neighbours?
  - [ ] would a citation to it point at the right thing?
- [ ] **1.6** Commit: `git commit -am "stage 1: cleaning + chunking"` (add new files first).
- [ ] **1.7** ✅ **CHECKPOINT 1** — paste: your fix counts, your chunk count, and one sample chunk with its citation.

---

## STAGE 2 — Embeddings + vector search (~1.5 h)

- [ ] **2.1** `pip install sentence-transformers` *(note: the first encode call downloads a ~90 MB model — one-time)*
- [ ] **2.2** Write `embed.py` — spec:
  - [ ] load the model `all-MiniLM-L6-v2`
  - [ ] read `chunks.jsonl`, encode every chunk's text with normalised embeddings
  - [ ] save the vectors to `vectors.npy` (NumPy) — the row order must match the `chunks.jsonl` line order (write that in a comment)
  - [ ] time the encoding and print it
- [ ] **2.3** Write `search.py` with `search(query, k=5)` — spec:
  - [ ] encode the query the same way
  - [ ] because vectors are normalised, cosine similarity = plain dot product
  - [ ] return the top-k chunk rows with their score and citation string
- [ ] **2.4** Hand-test with 5 questions you make up from the docs (use the text you read in Stage 0):
  - [ ] 4 phrased with the document's own words, **1 phrased completely differently** (e.g. "how much do I pay if I close my PPF early" → the doc says "premature liquidation penalty")
  - [ ] print top-3 per question and *judge with your eyes* — is the right chunk there?
- [ ] **2.5** Commit: `git commit -am "stage 2: embeddings + dense search"`
- [ ] **2.6** ✅ **CHECKPOINT 2** — paste the 5 questions and whether the right chunk made top-3.

---

## STAGE 3 — Better retrieval (~2.5 h)

- [ ] **3.1** `pip install rank-bm25`
- [ ] **3.2** Write `bm25.py` — spec:
  - [ ] tokenise all chunk texts **the same way you did nothing fancy** — lowercase, split on non-letters
  - [ ] build `BM25Okapi`, write `bm25_search(query, k)`
  - [ ] test with 3 queries that contain exact figures/short codes from the docs (e.g. a fee amount, a turnaround code like "T+1") — does BM25 beat dense on these?
- [ ] **3.3** Write `fuse.py` implementing **RRF** (read about it first!):
  - [ ] for each result list, score = `1 / (60 + rank)` per item; sum across lists; sort descending
  - [ ] `hybrid_search(query, k)` = RRF over dense top-30 + BM25 top-30 → top k
- [ ] **3.4** Print a comparison for 3 questions: dense top-5 vs BM25 top-5 vs fused top-5. Write in your journal where they differ and why you think so.
- [ ] **3.5** STRETCH (do only if on schedule) — reranker:
  - [ ] load `CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")`
  - [ ] score the fused top-30 as (query, passage) pairs, keep top 5
  - [ ] check on your 5 Stage-2 questions: how often does the best chunk move to #1?
- [ ] **3.6** Commit: `git commit -am "stage 3: hybrid retrieval"`
- [ ] **3.7** ✅ **CHECKPOINT 3** — paste the dense/BM25/fused comparison for one question and your explanation.

---

## STAGE 4 — Grounded answering + refusal (~2.5 h)

- [ ] **4.1** **DECIDE your LLM** (write the choice + why in the journal):
  - [ ] have an API key? → use it, `temperature=0`
  - [ ] no key? → build the **extractive answerer** (spec below) — fully legit and reproducible
- [ ] **4.2** Write `answer.py` — spec:
  - [ ] **if LLM:** a prompt with these rules — *answer only from the numbered excerpts*; *cite `[S#]` after every fact*; *be concise*; *if the excerpts don't contain the answer, reply exactly: "I could not find this information in the FinBase knowledge base."* Send the top-5 chunks as `[S1]…[S5]`.
  - [ ] **if extractive:** split each retrieved chunk into sentences; score each by word-overlap with the question (bonus: +1 if it contains digits/₹); take the best 1–3 sentences per source; stitch them in source order with `[S#]` markers after each; prefix a lead-in line.
  - [ ] **refusal rule (both paths):** if the best retrieval score is below a threshold *you choose by testing* (start with something and adjust on examples), return exactly the refusal sentence and an **empty** citation list.
- [ ] **4.3** Test a grid of 5 — record actual outputs in your journal:
  - [ ] 3 answerable questions → answer + correct `[S#]` citations?
  - [ ] 1 question about something that *sounds* plausible but isn't in the KB (e.g. "what are the charges for a bank locker?") → refused?
  - [ ] 1 obvious fake product (e.g. "home loan interest rate") → refused?
- [ ] **4.4** Commit: `git commit -am "stage 4: grounded answers + refusal"`
- [ ] **4.5** ✅ **CHECKPOINT 4** — paste the 5 Q&A outputs. This is the heart of the assignment; get it reviewed.

---

## STAGE 5 — Web interface (~1.5 h)

- [ ] **5.1** `pip install fastapi uvicorn`
- [ ] **5.2** Write `app.py` — spec:
  - [ ] `POST /ask` accepts `{"question": str, "session_id": str="default"}`, returns `{"answer": str, "citations": [{"label", "snippet"}]}`
  - [ ] serve a static `index.html` at `/`
- [ ] **5.3** Write `index.html` — spec (keep it ~100 lines, ugly is fine):
  - [ ] text input + Send button
  - [ ] `fetch("/ask", {method:"POST", ...})` on click
  - [ ] show the answer, then the sources as a bullet list under it ("Sources:" + citation labels)
  - [ ] show the raw answer even if something fails (wrap in try/catch and display the error)
- [ ] **5.4** Follow-ups: keep a fixed `session_id` per browser tab; on the server, keep the last 2–3 Q&A turns per session and include them in the prompt/answer step so "what about after 24 months?" resolves.
- [ ] **5.5** Run `uvicorn app:app --reload` and test in the browser: 2 questions + 1 follow-up.
- [ ] **5.6** Commit + ✅ **CHECKPOINT 5** — screenshot of an answer with sources; mention if the follow-up worked.

---

## STAGE 6 — Evaluation (Friday morning, ~3 h — scheduled first, it's 25% of the grade)

- [ ] **6.1** Build `golden_set.json` **by hand**. Format per item:
  `{"id", "q", "answerable": true/false, "gold_doc", "gold_section", "gold_facts": ["the exact figures the answer must contain"], "ref": "one line: where you verified it"}`
  - [ ] ~50–70 answerable questions spread across all 6 documents (use what you read in Stage 0)
  - [ ] 10–15 **traps**: products/entities that do NOT exist in the KB (from your Stage-0 reading). Write these as something a real customer would plausibly ask.
  - [ ] quality > quantity: every item must be verified against the text with your own eyes
- [ ] **6.2** Write `eval.py` — spec, one loop over the golden set:
  - [ ] for each question: run your full pipeline (hybrid search → answer)
  - [ ] retrieval metric: is the gold section in top-1 / top-3 / top-5? (print the averages; add MRR: 1/rank of the first gold hit)
  - [ ] answer metric: **fact coverage** — what fraction of `gold_facts` appear in the answer? **Normalise numbers first**: strip `₹` and commas, so `₹5,00,000` == `500000`
  - [ ] citation metric: does the answer cite a section (any), and does it cite the *gold* one?
  - [ ] refusal metric: how many traps got the refusal (or an explicit "I could not find…" disclosure)?
  - [ ] write the full results to `eval_report.md` (a readable table), and remember the run must be repeatable with one command
- [ ] **6.3** Run it. Then **write the failure list**: every question that scored badly, and your best guess why (retrieval miss? chunk too long? answerer picked adjacent text?). Don't fix everything — fix one cheap thing if obvious, otherwise document.
- [ ] **6.4** Commit + ✅ **CHECKPOINT 6** — paste the metrics table and your failure list. These numbers go in your video, README and interview.

---

## STAGE 7 — Ship it (Friday, ~2 h + video)

- [ ] **7.1** Write `README.md`: what it is (2 lines) · architecture diagram (ASCII boxes are fine: PDFs → clean → chunk → embed → retrieve → answer → citations) · **your six technical choices with your justifications** (they're in your journal) · how to run it (3 commands) · API endpoint description · your evaluation table · known limitations (from 6.3).
- [ ] **7.2** Push to GitHub (make it public, no starter README):
  - [ ] create the empty repo on github.com
  - [ ] `git remote add origin https://github.com/<you>/<repo>.git`
  - [ ] `git push -u origin main` (password = a Personal Access Token, not your account password)
  - [ ] check in an incognito tab that the README renders
- [ ] **7.3** Deploy a public URL: create a free **Hugging Face** account → New Space (SDK: **Docker**, free CPU) → for this mechanical step you may borrow `deploy/` + `Dockerfile` from the finished repo → push → wait for build → test the URL.
- [ ] **7.4** Record the **≤5 min video** (script from your journal — problem, architecture, preprocessing, chunking, embeddings, retrieval, answering, evaluation, trade-offs, demo, limitations):
  - [ ] warm the app with your 3 demo questions 5 minutes before recording
  - [ ] demo: 1 answerable (show sources) · 1 refusal · 1 follow-up
  - [ ] keep it under 5:00 — time it
- [ ] **7.5** ✅ **FINAL CHECK** in incognito on a second device: repo opens · URL loads and answers · video plays · all three links in one note.
- [ ] **7.6** Submit through the mail's **Submission Link** — Friday morning, not 5 PM — screenshot the confirmation. Done. 🎉

---

## How to work with your tutor (me) at each checkpoint

Paste in this shape — it makes debugging fast:
1. **The command** you ran
2. **The output** (or a small slice)
3. **What you expected** and how it differed
4. **Your guess** at the cause

That's it. Do **not** paste the whole project or say "it doesn't work" — smallest failing example wins.

**If a stage takes >1.5× its budget:** stop, ping me, we cut scope together (cut order: reranker → hybrid → Docker → interface polish). Never cut: citations, refusal, evaluation, README, deploy, video.
