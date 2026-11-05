# Module 08 quiz

1. What does an int8 scale encode?

<details><summary>Answer</summary>

The value of one integer step for a coordinate.

</details>

2. What does packed sign search discard?

<details><summary>Answer</summary>

Coordinate magnitude.

</details>

3. Why is PQ lookup asymmetric?

<details><summary>Answer</summary>

The query remains full precision and only catalog vectors use codes.

</details>

4. Which two stages can miss in IVF-PQ?

<details><summary>Answer</summary>

Coarse-list routing and compressed ranking.

</details>

5. What does oversampling buy?

<details><summary>Answer</summary>

More candidates for exact rescoring, at a higher cost.

</details>

6. How should a shortened cosine embedding be used?

<details><summary>Answer</summary>

Slice both sides to the same trained prefix, then renormalize.

</details>
