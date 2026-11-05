# Module 20 quiz

<details>
<summary>1. Can MiniLM text directly search SigLIP images?</summary>

No. Use SigLIP's own text tower.

</details>

<details>
<summary>2. Why normalize both query and gallery?</summary>

Then their dot product represents cosine similarity.

</details>

<details>
<summary>3. What does a named vector add?</summary>

A distinct vector field and query target on one record.

</details>

<details>
<summary>4. Why exclude the source image ID?</summary>

An identical file is a trivial nearest neighbor.

</details>

<details>
<summary>5. Does exclusion remove every shortcut?</summary>

No. Repeated synthetic templates can remain highly similar.

</details>

<details>
<summary>6. What does weight zero mean?</summary>

The branch contributes no scores and introduces no candidate IDs.

</details>
