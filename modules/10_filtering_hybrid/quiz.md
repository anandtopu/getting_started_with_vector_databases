# Module 10 quiz

1. What makes a sparse vector sparse?

<details><summary>Answer</summary>

Only the few present terms have stored nonzero weights.

</details>

2. Why can postfiltering lose recall?

<details><summary>Answer</summary>

Eligible rows may never enter the shortlist.

</details>

3. Why traverse ineligible graph nodes?

<details><summary>Answer</summary>

They may be the only bridge to eligible rows.

</details>

4. How does RRF combine scores?

<details><summary>Answer</summary>

It sums contributions based on rank positions.

</details>

5. How does MaxSim differ from one vector per product?

<details><summary>Answer</summary>

Each query token can match a different document token.

</details>

6. Why measure relevance separately from neighbor recall?

<details><summary>Answer</summary>

Fusion can improve useful results while changing their vector-neighbor order.

</details>
