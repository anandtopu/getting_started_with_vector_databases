# Module 11 quiz

1. Where does an embedded engine execute?

<details><summary>Answer</summary>

Inside the calling process.

</details>

2. What fixes Lance vector dimensions?

<details><summary>Answer</summary>

Its Arrow field declares a fixed-size list.

</details>

3. What must survive a logical export?

<details><summary>Answer</summary>

IDs, vectors, metadata, text and the collection’s embedding-space contract.

</details>

4. Why bind SQL values?

<details><summary>Answer</summary>

Binding preserves value types and separates values from SQL syntax.

</details>

5. What does a Lance version preserve?

<details><summary>Answer</summary>

A readable historical table state until retention or cleanup removes its files.

</details>

6. Why publish DuckDB exact and VSS separately?

<details><summary>Answer</summary>

A scalar array scan and an approximate graph have different execution plans.

</details>
