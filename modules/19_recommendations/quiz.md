# Module 19 quiz

<details>
<summary>1. Why exclude future purchases from user vectors?</summary>

Otherwise the evaluation answer is already present in the query.

</details>

<details>
<summary>2. What happens when MMR lambda is 1?</summary>

Ranking uses only query relevance.

</details>

<details>
<summary>3. Why split duplicates by group?</summary>

Related copies must not leak across development and test.

</details>

<details>
<summary>4. Can a cosine threshold transfer automatically between models?</summary>

No. It must be calibrated on the new score distribution.

</details>

<details>
<summary>5. Are distant reviews necessarily negative?</summary>

No. Distance measures unusual embedding position, not sentiment or truth.

</details>

<details>
<summary>6. Why add a separate event fixture?</summary>

The original generator has no evaluable unseen-purchase cases at the audited cutoff, which must not be disguised as a successful metric.

</details>
