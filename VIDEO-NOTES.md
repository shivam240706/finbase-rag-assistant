# video + viva cheat sheet (my own words)

record <= 5 min. use the notebook on screen, click through the cells in this order.

## what to say per cell (10-20 sec each)

- **step 1 extract** - "pypdf gave me raw text, but when i opened it i saw 4 problems: ₹ became ■, bullets became a control character, a useless table of contents, and sentences cut across lines. so extraction alone was not enough, preprocessing mattered."
- **step 2 clean** - "i fixed each problem with a counted rule, so i could prove it worked: 138 toc lines removed, 3,888 broken characters fixed, 2,863 lines rejoined across the six documents."
- **step 3 chunking** - "the documents have structure, so i did not do blind fixed-size chunking. i split on section headings and on the 100 FAQ questions per document; long sections get cut at ~180 words with 30 words overlap so nothing is sliced mid-sentence. 771 chunks, 600 of them FAQs."
- **step 4 embeddings** - "all-MiniLM-L6-v2: 384 dimensions, runs on cpu in ~30 seconds, enough quality for short policy text. bigger models were not worth it for 771 chunks."
- **step 5 search** - "cosine similarity over a numpy matrix - i don't need a vector database at this scale, brute force is exact and fast. plus a small title bonus after i saw 'complaint' questions fetch the wrong document."
- **step 6 vocabulary** - "my favourite trick: if the question uses a word that appears NOWHERE in the corpus (home, nri, locker), the kb cannot know the answer. that is how i catch products the bank does not offer."
- **step 7 answer** - "i never let a model write freely. the answer is the two most relevant sentences per source, quoted exactly, tagged [S1] [S2]. refuse if 3+ unknown words or weak match; disclose if a product is missing."
- **steps 9-10 eval** - "i wrote my own golden set from the real text: X answerable + Y traps. metrics: hit@1/3/5 for retrieval, fact coverage for answers, trap handling for honesty."

## numbers to quote (from work/final_numbers.json - use YOURS)

chunks 771 (600 faq) · toc 138 · glyphs 3,888 · joins 2,863 · hit@1/hit@5 · coverage · traps handled.

## the six choices i must mention (they ask for all six)

1. chunking: structure-aware (headings + faq), 180w + 30 overlap
2. embedding model: all-MiniLM-L6-v2 (small, cpu, 384-dim)
3. vector store: numpy matrix, brute-force cosine (exact; a db like FAISS only matters at millions of chunks)
4. retrieval: dense cosine + citation-title bonus, top-5
5. llm: none for generation - extractive quoting (cheapest, zero hallucination); i'd plug gpt-4o-mini behind a function if free-form answers were needed
6. prompting: n/a for generation; my "prompt" is the grounding rule = quote-only + refuse rules

## honest limitations (say these! they score points)

- the escalate-a-complaint question retrieves loan FAQs, not the grievance section - dense search alone confuses it; hybrid BM25 would fix it (next step)
- one of my golden items (Metal card fee) is answered from the FAQ chunk, so section hit@3 misses while the answer is still correct
- extractive answers read stiff; an llm would smooth them but adds hallucination risk

## trap list (products NOT in the corpus)

home loan · car loan · education loan · gold loan · locker facility · NRI banking ·
Titanium card · salary account · cheque book · demat/trading · forex card · joint account
