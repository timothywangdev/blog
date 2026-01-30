# Understanding Reasoning LLMs

**Subtitle:** Methods and Strategies for Building and Refining Reasoning Models

**Date:** JUL 19, 2025

**URL:** https://magazine.sebastianraschka.com/p/understanding-reasoning-llms

**Likes:** 1,239

**Image Count:** 18

---

## Images

1. ![Figure](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fd6ebc5c9-461f-4d3a-889b-b8ea4e14e5ba_1600x830.png)
   - Caption: Stages 1-3 are the common steps to developing LLMs. Stage 4 specializes LLMs for specific use cases.

2. ![Figure](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Ff2987079-25f4-45fb-a020-1ac936ed16cb_1424x820.png)
   - Caption: A regular LLM may only provide a short answer (as shown on the left), whereas reasoning models typically include intermediate steps.

3. ![Figure](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F35712d0e-0f40-4855-8d81-4dcea94055ce_1538x810.png)
   - Caption: "Reasoning" is used at two different levels: 1) processing the input and generating via multiple intermediate steps and 2) providing some sort of reasoning as part of the response to the user.

4. ![Figure](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F46dbe029-ab7d-4278-8dfe-7bc4af79a103_1352x524.png)
   - Caption: The key strengths and weaknesses of reasoning models.

5. ![Figure](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fdb19df56-c5bf-4a0c-aafb-4629a39b13f5_1542x1166.png)
   - Caption: Development process of DeepSeeks three different reasoning models.

6. ![Figure](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F523eee5e-afb6-4019-a11b-e0a291d2c286_1600x419.png)
   - Caption: An example of classic CoT prompting from the 2022 Large Language Models are Zero-Shot Reasoners paper.

7. ![Figure](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F5cb10e5a-738b-4c9e-ba65-5850d4793706_1600x919.png)
   - Caption: Different search-based methods rely on a process-reward-based model to select the best answer.

8. ![Figure](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa5bb6ecc-7e46-45fe-abff-1eb02e6b0e3a_1556x1162.png)
   - Caption: The development process of DeepSeek-R1-Zero model.

9. ![Figure](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F30f8e37b-ba60-49d2-a95e-9c06b2033ee4_1600x1019.png)
   - Caption: A figure from the DeepSeek R1 technical report showing the emergence of the "Aha" moment.

10. ![Figure](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fdf7f99f0-d154-49e5-b60a-4d148e0a61be_1548x1154.png)
    - Caption: The development process of DeepSeek-R1 model.

---

## Full Text Content

This article describes the four main approaches to building reasoning models, or how we can enhance LLMs with reasoning capabilities.

## Table of Contents

1. How do we define "reasoning model"?
2. When should we use reasoning models?
3. A brief look at the DeepSeek training pipeline
4. The 4 main ways to build and improve reasoning models
   - 4.1 Inference-time scaling
   - 4.2 Pure reinforcement learning (RL)
   - 4.3 Supervised finetuning and reinforcement learning (SFT + RL)
   - 4.4 Pure supervised finetuning (SFT) and distillation
5. Conclusion
6. Thoughts about DeepSeek R1
7. Developing reasoning models on a limited budget
   - Sky-T1 ($450)
   - TinyZero (<$30)
   - Journey Learning

## Key Concepts

### Definition of Reasoning Model
- Process of answering questions that require complex, multi-step generation with intermediate steps
- Two levels of "reasoning":
  1. Processing input and generating via multiple intermediate steps
  2. Providing reasoning as part of the response to the user

### When to Use Reasoning Models
**Strengths:**
- Complex multi-step problems
- Advanced math
- Challenging coding tasks
- Puzzles and riddles

**Weaknesses:**
- More expensive to run
- More verbose
- Prone to "overthinking" errors
- Not needed for simple tasks (summarization, translation, QA)

### The 4 Main Approaches

1. **Inference-Time Scaling**
   - No additional training required
   - Increases inference costs
   - Examples: Chain-of-thought prompting, majority voting, beam search
   - OpenAI o1 likely uses this (explains higher cost)

2. **Pure Reinforcement Learning**
   - DeepSeek-R1-Zero approach
   - No SFT stage ("cold start")
   - Two types of rewards:
     - Accuracy reward (LeetCode compiler for code, deterministic for math)
     - Format reward (LLM judge for <think> tags)
   - Key finding: "Aha moment" - reasoning emerged without explicit training

3. **SFT + RL (The Blueprint)**
   - DeepSeek-R1 approach
   - Steps:
     1. Start with R1-Zero → generate "cold-start" SFT data
     2. Instruction fine-tuning
     3. RL stage (accuracy + format + consistency rewards)
     4. Generate 600K CoT + 200K knowledge SFT examples
     5. Final instruction fine-tuning
     6. Final RL stage

4. **Pure SFT / Distillation**
   - DeepSeek-R1-Distill
   - Fine-tune smaller models (Llama 8B/70B, Qwen 0.5B-32B) on SFT data from larger models
   - Not traditional knowledge distillation (no logits)
   - Key finding: Distillation more effective than pure RL for smaller models

### Budget-Friendly Approaches

**Sky-T1 ($450)**
- 32B model trained on only 17K SFT samples
- Performs roughly on par with o1
- Pure SFT approach

**TinyZero (<$30)**
- 3B parameter model
- Replicates DeepSeek-R1-Zero approach
- Shows emergent self-verification abilities

**Journey Learning**
- Alternative to "shortcut learning"
- Includes incorrect solution paths in SFT data
- Model learns from mistakes
- May reinforce self-correction abilities
