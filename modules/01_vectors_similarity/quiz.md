# Module 01 quiz

**1. What does shape (1000,384) mean?**

<details>
<summary>Answer</summary>

One thousand vectors, each with 384 coordinates.

</details>

**2. Can cosine distinguish [1,0] from [10,0]?**

<details>
<summary>Answer</summary>

No. Their directions are the same, so both have cosine 1 with [1,0].

</details>

**3. Why reject zero for cosine?**

<details>
<summary>Answer</summary>

Its length is zero and it has no direction; the cosine formula would divide by zero.

</details>

**4. When do dot and cosine rank alike?**

<details>
<summary>Answer</summary>

When both sides are appropriately normalized to unit length.

</details>

**5. Does shrinking relative distance spread prove semantic search fails?**

<details>
<summary>Answer</summary>

No. The experiment assumes independent random coordinates; learned data has structure.

</details>

**6. Why sort equal scores by ID?**

<details>
<summary>Answer</summary>

It gives reproducible order, although another library can have different legitimate tie behavior.

</details>
