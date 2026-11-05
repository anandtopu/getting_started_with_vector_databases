# Module 03 quiz

**1. How is upsert different from append?**

<details>
<summary>Answer</summary>

It replaces the record with an existing ID, or inserts it if absent.

</details>

**2. Why validate the whole batch before mutation?**

<details>
<summary>Answer</summary>

A later invalid record should not leave earlier records partially updated.

</details>

**3. Why can postfiltering return fewer than k valid results?**

<details>
<summary>Answer</summary>

The initial candidate set can be occupied by ineligible records; valid ones outside it were never considered.

</details>

**4. Does exact filtered ground truth use all products?**

<details>
<summary>Answer</summary>

It searches only the same eligible filter set.

</details>

**5. Why publish the manifest after the vector file?**

<details>
<summary>Answer</summary>

Readers should not observe a new manifest pointing at incomplete vector bytes.

</details>

**6. Is TinyVec safe as an uncoordinated multiwriter service?**

<details>
<summary>Answer</summary>

No. It has no transaction or writer-lock protocol; use it as an educational single-owner store.

</details>
