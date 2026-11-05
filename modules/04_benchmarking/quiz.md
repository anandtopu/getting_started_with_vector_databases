# Module 04 quiz

**1. Can exact search have recall 1 and relevance 0?**

<details>
<summary>Answer</summary>

Yes. It can faithfully retrieve nearest vectors that do not satisfy the customer’s intent.

</details>

**2. How does precision differ from recall in this course?**

<details>
<summary>Answer</summary>

Precision uses independent useful-item judgments; ANN recall uses exact vector neighbors.

</details>

**3. What is MRR for a first relevant result at rank four?**

<details>
<summary>Answer</summary>

0.25 for that query; average reciprocal rank across queries for MRR.

</details>

**4. Does standard deviation across repetitions prove a speed difference is significant?**

<details>
<summary>Answer</summary>

No. It describes observed variation, not a complete statistical comparison or confidence interval.

</details>

**5. Why compute quality outside the timed loop?**

<details>
<summary>Answer</summary>

The retrieval latency should not include the evaluator’s work unless that is the explicitly chosen workload.

</details>

**6. Why retain strict ID recall beside tie-aware recall?**

<details>
<summary>Answer</summary>

It exposes ordering differences while the primary metric fairly handles equivalent cutoff neighbors.

</details>
