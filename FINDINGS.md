# Findings

Issues found while testing the Ribeira Markets support assistant.

## F-001: Synonym questions miss the right document

**Status:** Open
**Layer:** Retrieval

### Steps to reproduce
Search for "Can I trade Bitcoin?" with the retriever.

### Expected
The top result is the paragraph in `trading.md` that says
"Options, futures, cryptocurrencies and CFDs are not offered."

### Actual
That paragraph is not returned. The retriever returns unrelated paragraphs
that only share the word "trade", with a low score (about 1.7).
A good match, like "How much does a SWIFT withdrawal cost?", scores about 6.6.

### Root cause
The retriever matches exact words. The question says "Bitcoin",
the document says "cryptocurrencies", so no words match.

### Risk
A model receiving these unrelated paragraphs might answer
"Yes, you can trade Bitcoin", which is false.