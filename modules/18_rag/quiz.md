# Module 18 quiz

<details>
<summary>1. Why overlap chunks?</summary>

It reduces boundary loss, at the cost of duplicate retrieval evidence.

</details>

<details>
<summary>2. Why keep passage IDs?</summary>

They let multiple chunks cite the same stable source passage.

</details>

<details>
<summary>3. What does passage recall measure?</summary>

The fraction of independently labeled source passages represented in retrieved chunks.

</details>

<details>
<summary>4. Is a cited claim necessarily faithful?</summary>

No. The stored refund draft contradicts a source despite a valid citation.

</details>

<details>
<summary>5. Why compare narrow LSH with exact retrieval?</summary>

To observe how missed candidates remove evidence and can cause abstention.

</details>

<details>
<summary>6. What does the fallback prove?</summary>

The delivered words occur in the retrieved source. It does not prove the source answers the question.

</details>
