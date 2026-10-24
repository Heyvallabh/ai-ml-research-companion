## Manual smoke test

| # | Type | Question | Expected | Result | Note |
|---|---|---|---|---|---|
| 1 | Answerable | What metric do the authors use to evaluate multi-document QA? | p.3 | ✅ |The answer matches the key, and the [n] citation points to a page that really contains it, and nothing is invented |
| 2 | Answerable | Why did the authors randomize the order of the distractor documents? | p.3, p.14 | ✅ | The answer matches the key, and the [n] citation points to a page that really contains it, and nothing is invented|
| 3 | Answerable | What happens to model performance when the distractors are hard negatives? | p.14 | ✅ | The answer matches the key, and the [n] citation points to a page that really contains it, and nothing is invented|
| 4 | Answerable | What instruction did the authors use to tell the model the search results were randomly ordered? | p.14 | ✅ |The answer matches the key, and the [n] citation points to a page that really contains it, and nothing is invented |
| 5 | Answerable | Which dataset is the multi-document QA task built from? | p.3 | ✅ |The answer matches the key, and the [n] citation points to a page that really contains it, and nothing is invented |
| 6 | Answerable | Where in the input context do models perform best, and where worst? | p.1 (abstract) | ✅ | The answer matches the key, and the [n] citation points to a page that really contains it, and nothing is invented|
| 7 | Answerable | Which two tasks do the authors use to study how models use long contexts? | p.1 (abstract) | ✅ |The answer matches the key, and the [n] citation points to a page that really contains it, and nothing is invented |
| 8 | Unanswerable | What is attention? | refusal | ✅ | refused correctly |
| 9 | Unanswerable | How do I bake bread? | refusal | ✅ | refused correctly |
| 10 | Unanswerable | What is gradient descent? | refusal | ✅ | refused correctly |