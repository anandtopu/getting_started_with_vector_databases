# Module 09 quiz

1. Why stream generation?

<details><summary>Answer</summary>

To bound temporary float allocations.

</details>

2. Why compute truth before rounding?

<details><summary>Answer</summary>

To measure what the compressed representation loses.

</details>

3. What is read amplification?

<details><summary>Answer</summary>

Bytes fetched divided by bytes actually useful to the query.

</details>

4. Why keep k winners per block?

<details><summary>Answer</summary>

A discarded row already has k better rows in that block.

</details>

5. What is a shard?

<details><summary>Answer</summary>

An independently searched partition of the collection.

</details>

6. Which figures can be extrapolated directly?

<details><summary>Answer</summary>

Fixed-width payload with a known row count and dimension.

</details>
