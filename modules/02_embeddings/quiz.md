# Module 02 quiz

**1. Do learned coordinates have names like warmth and price?**

<details>
<summary>Answer</summary>

Usually not. They jointly encode patterns learned by the model.

</details>

**2. Why can equal-dimensional models be incompatible?**

<details>
<summary>Answer</summary>

Their coordinate systems and training objectives differ; coordinates need a shared recipe.

</details>

**3. Which costs should be separated when timing inference?**

<details>
<summary>Answer</summary>

Model startup, preprocessing/inference, cache access, and retrieval.

</details>

**4. Why include query/document role in a cache key?**

<details>
<summary>Answer</summary>

Some models use different prompts or encoders by role; accidental reuse changes semantics.

</details>

**5. What does PCA preserve?**

<details>
<summary>Answer</summary>

Directions with high variance under its linear projection, not all neighbors or relevance.

</details>

**6. Can a MiniLM query search SigLIP image vectors?**

<details>
<summary>Answer</summary>

No. Use a compatible joint image/text model for both sides.

</details>
