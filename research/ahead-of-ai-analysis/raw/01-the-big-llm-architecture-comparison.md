# The Big LLM Architecture Comparison

**Subtitle:** From DeepSeek V3 to Mistral 3 Large: A Look At Modern LLM Architecture Design

**Date:** FEB 5, 2025 (Last updated: Dec 18, 2025)

**URL:** https://magazine.sebastianraschka.com/p/the-big-llm-architecture-comparison

**Likes:** 1,723

**Image Count:** 60

---

## Images

1. ![Figure 1](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F4ae4aa85-3e22-486c-9bd9-27edc4acbf8b_3000x2093.png)
   - Caption: Figure 1: A subset of the architectures covered in this article.

2. ![Figure 2](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F647caf83-cd3d-46f8-8bd0-0946bd896ea1_1023x474.png)
   - Caption: Figure 2: A comparison between MHA and GQA. Here, the group size is 2, where a key and value pair is shared among 2 queries.

3. ![Figure 3](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Feb9a75be-2848-4b99-af3d-4c48bdd0181a_1550x858.png)
   - Caption: Figure 3: Comparison between MLA (used in DeepSeek V3 and R1) and regular MHA.

4. ![Figure 4](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F2b7e646a-16c1-4245-9a3f-55a41f3070c2_903x856.png)
   - Caption: Figure 4: Annotated tables from the DeepSeek-V2 paper, https://arxiv.org/abs/2405.04434

5. ![Figure 5](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F632d3212-432a-4d43-b271-f2269be1d8ec_1304x822.png)
   - Caption: Figure 5: An illustration of the Mixture-of-Experts (MoE) module in DeepSeek V3/R1 (right) compared to an LLM with a standard FeedForward block (left).

6. ![Figure 6](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F3d93c441-a6d2-4257-bd80-2d3590c4001c_1039x569.png)
   - Caption: Figure 6: An annotated figure from "DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models"

7. ![Figure 7](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fbb5c7281-eded-4319-9ae2-7b07478a86b2_1027x823.png)
   - Caption: Figure 7: Modeling benchmark performance (higher is better) vs pre-training cost (FLOPs; lower is better) for different LLMs.

8. ![Figure 8](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F61a4560f-d97f-4c78-a7a3-765babb45bec_1444x789.png)
   - Caption: Figure 8: A comparison of Post-Norm, Pre-Norm, and OLMo 2's flavor of Post-Norm.

9. ![Figure 9](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F186190ec-2ae5-430d-b0d4-a63486e0f3fb_1289x407.png)
   - Caption: Figure 9: A plot showing the training stability for Pre-Norm versus OLMo 2's flavor of Post-Norm.

10. ![Figure 10](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F7fa42974-cfae-45cc-9cd9-fc1d9607d386_1329x737.png)
    - Caption: Figure 10: An architecture comparison between Llama 3 and OLMo 2.

---

## Full Text Content

Last updated: Dec 18, 2025

It has been seven years since the original GPT architecture was developed. At first glance, looking back at GPT-2 (2019) and forward to DeepSeek V3 and Llama 4 (2024-2025), one might be surprised at how structurally similar these models still are.

Sure, positional embeddings have evolved from absolute to rotational (RoPE), Multi-Head Attention has largely given way to Grouped-Query Attention, and the more efficient SwiGLU has replaced activation functions like GELU. But beneath these minor refinements, have we truly seen groundbreaking changes, or are we simply polishing the same architectural foundations?

Comparing LLMs to determine the key ingredients that contribute to their good (or not-so-good) performance is notoriously challenging: datasets, training techniques, and hyperparameters vary widely and are often not well documented.

However, I think that there is still a lot of value in examining the structural changes of the architectures themselves to see what LLM developers are up to in 2025.

## Table of Contents

1. DeepSeek V3/R1
   - 1.1 Multi-Head Latent Attention (MLA)
   - 1.2 Mixture-of-Experts (MoE)
   - 1.3 DeepSeek Summary
2. OLMo 2
   - 2.1 Normalization Layer Placement
   - 2.2 QK-Norm
   - 2.3 OLMo 2 Summary
3. Gemma 3
   - 3.1 Sliding Window Attention
   - 3.2 Normalization Layer Placement in Gemma 3
   - 3.3 Gemma 3 Summary
   - 3.4 Bonus: Gemma 3n
4. Mistral Small 3.1
5. Llama 4
6. Qwen3
   - 6.1 Qwen3 (Dense)
   - 6.2 Qwen3 (MoE)
7. SmolLM3
   - 7.1 No Positional Embeddings (NoPE)
8. Kimi K2 and Kimi K2 Thinking
9. GPT-OSS
   - 9.1 Width Versus Depth
   - 9.2 Few Large Versus Many Small Experts
   - 9.3 Attention Bias and Attention Sinks
10. Grok 2.5
11. GLM-4.5
12. Qwen3-Next
    - 12.1 Expert Size and Number
    - 12.2 Gated DeltaNet + Gated Attention Hybrid
    - 12.3 Multi-Token Prediction
13. MiniMax-M2
14. Kimi Linear
15. Olmo 3 Thinking
16. DeepSeek V3.2
17. Mistral 3
18. Nemotron 3
19. Xiaomi MiMo-V2-Flash

[Full article text continues with detailed technical content about each architecture...]
