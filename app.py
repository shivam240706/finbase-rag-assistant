# app.py - the chat interface
# run with:  python -m streamlit run app.py
# (i copied my functions over from the notebook so this file works on its own)

import re, json
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer

st.set_page_config(page_title="FinBase Help", page_icon="🏦")
st.title("FinBase Customer Support Assistant")
st.write("Answers only come from the FinBase knowledge base (6 policy documents). Sources are shown under every answer.")

# ---- load the index i built in the notebook ----
chunks = []
f = open("work/chunks.jsonl", encoding="utf-8")
for line in f:
    chunks.append(json.loads(line))
f.close()
vectors = np.load("work/vectors.npy")
model = SentenceTransformer("all-MiniLM-L6-v2")

# ---- same vocabulary trick as the notebook ----
vocab = set()
for c in chunks:
    for w in re.findall(r"[a-z]{3,}", c["text"].lower()):
        vocab.add(w)

STOP = """the a an of for to in on at my i how do does can could you me and or are
was were be been being this that these those with without about from into over under
after before during if then than so such between across per any all each other more
most some no not only own same too very just don should now there here when where why
which who whom whose will would shall may might must have has had having it its please
tell show give need want get got make made use used using also long take quickly keep
ready complaint close open work much many days day time times money account rate
charge fee fees one two three""".split()

def uncovered(query):
    words = set(re.findall(r"[a-z]{3,}", query.lower())) - set(STOP)
    missing = []
    for w in sorted(words):
        if w not in vocab:
            missing.append(w)
    return missing

def search(query, k=5):
    qv = model.encode([query], normalize_embeddings=True)[0]
    scores = list(vectors @ qv)
    qwords = list(set(re.findall(r"[a-z]{4,}", query.lower())))
    for i in range(len(chunks)):
        bonus = 0
        for w in qwords:
            if w in chunks[i]["citation"].lower():
                bonus = bonus + 0.06
        scores[i] = scores[i] + bonus
    order = np.argsort(-np.array(scores))
    hits = []
    for i in order[:k]:
        hits.append((float(scores[i]), chunks[i]))
    return hits

REFUSAL = "I could not find this information in the FinBase knowledge base."

def get_sentences(text):
    text = re.sub(r"\s*\((Operational|Payment|Service|KYC|Card|Loan|Wealth|Savings|UPI)[a-z ]*case \d+\)", "", text)
    text = text.replace("•", "").strip()
    out = []
    for s in re.split(r"(?<=[.?!]) ", text):
        s = s.strip()
        if len(s) > 25 and not re.match(r"(Section \d|Q\d+:) [^.]{0,60}$", s):
            out.append(s)
    return out

def answer(query):
    hits = search(query, 5)
    missing = uncovered(query)

    # refuse when off-topic or when nothing relevant was found
    if len(missing) >= 3 or hits[0][0] < 0.35:
        return {"answer": REFUSAL, "citations": []}

    lead = ""
    if len(missing) > 0:
        lead = 'I could not find information about "' + ", ".join(missing) + \
               '" in the FinBase knowledge base. The closest related information available is: '

    qwords = set(re.findall(r"[a-z0-9]+", query.lower()))
    pieces = []
    citations = []
    rank = 0
    for score, ch in hits:
        rank = rank + 1
        sents = get_sentences(ch["text"])
        if len(sents) == 0:
            continue
        overlap = []
        for i in range(len(sents)):
            sword = set(re.findall(r"[a-z0-9]+", sents[i].lower()))
            overlap.append((len(qwords.intersection(sword)), i))
        overlap.sort(key=lambda x: -x[0])
        if overlap[0][0] == 0:
            continue
        top = [overlap[0][1]]
        if len(overlap) > 1:
            top.append(overlap[1][1])
        top.sort()
        piece = ""
        for i in top:
            piece = piece + sents[i] + " "
        pieces.append(piece.strip() + " [S" + str(rank) + "]")
        citations.append({"label": ch["citation"], "snippet": ch["text"][:150]})

    if len(pieces) == 0:
        return {"answer": REFUSAL, "citations": []}
    body = "Based on the FinBase knowledge base:\n" + "\n".join(pieces)
    if lead != "":
        body = lead + body
    return {"answer": body, "citations": citations}

# ---- the chat ui ----
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["text"])
        for c in m.get("cites", []):
            st.caption("Source: " + c["label"])

q = st.chat_input("Ask about loans, cards, deposits, UPI, KYC...")
if q:
    # remember the last question so short follow-ups ("what about 24 months?")
    # get the context attached
    last_user = None
    for m in st.session_state.messages:
        if m["role"] == "user":
            last_user = m["text"]
    full_q = q
    if last_user is not None and len(q.split()) <= 4:
        full_q = last_user + " " + q

    st.session_state.messages.append({"role": "user", "text": q})
    with st.chat_message("user"):
        st.write(q)
    r = answer(full_q)
    with st.chat_message("assistant"):
        st.write(r["answer"])
        for c in r["citations"]:
            st.caption("Source: " + c["label"])
    st.session_state.messages.append({"role": "assistant", "text": r["answer"], "cites": r["citations"]})
