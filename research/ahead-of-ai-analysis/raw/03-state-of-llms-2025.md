# The State Of LLMs 2025: Progress, Problems, and Predictions

**Date:** Dec 30, 2025

**URL:** https://magazine.sebastianraschka.com/p/state-of-llms-2025

**Likes:** 465

**Image Count:** 28

---

## Table of Contents

1. The Year of Reasoning, RLVR, and GRPO
   - 1.1 The DeepSeek Moment
   - 1.2 LLM Focus Points
2. GRPO, the Research Darling of the Year
3. LLM Architectures: A Fork in the Road?
4. It's Also The Year of Inference-Scaling and Tool Use
5. Word of the Year: Benchmaxxing
6. AI for Coding, Writing, and Research
   - 6.1 Coding
   - 6.2 Codebases and code libraries
   - 6.3 Technical writing and research
   - 6.4 LLMs and Burnout
7. The Edge: Private data
8. Building LLMs and Reasoning Models From Scratch
9. Surprises in 2025 and Predictions for 2026
   - 9.1 Noteworthy and Surprising Things in 2025
   - 9.2 Predictions for 2026
10. Bonus: A Curated LLM Research Papers List

---

## Key Takeaways

### 1. The DeepSeek Moment (January 2025)
- DeepSeek R1 released as open-weight model comparable to best proprietary models
- Training cost estimated ~$5M (much cheaper than previously assumed $50-500M)
- Introduced **RLVR (Reinforcement Learning with Verifiable Rewards)** with **GRPO algorithm**
- "Verifiable" = deterministic correctness labels (math, code)

### 2. LLM Development Focus by Year
- 2022: RLHF + PPO
- 2023: LoRA SFT
- 2024: Mid-Training
- 2025: RLVR + GRPO
- 2026 prediction: RLVR extensions + inference-time scaling
- 2027 prediction: Continual learning

### 3. GRPO Improvements (Research Darling)
**OLMo 3 adopted:**
- Zero gradient signal filtering (DAPO)
- Active sampling
- Token-level loss
- No KL loss
- Clip higher
- Truncated importance sampling
- No standard deviation normalization

**DeepSeek V3.2 adopted:**
- KL tuning with domain-specific strengths
- Reweighted KL
- Off-policy sequence masking
- Keep sampling mask for top-p/top-k

### 4. Architecture Trends
- MoE (Mixture-of-Experts) now standard for large models
- Efficiency tweaks: GQA, sliding-window attention, MLA
- Linear attention variants emerging: Gated DeltaNets (Qwen3-Next, Kimi Linear), Mamba-2 (Nemotron 3)
- Text diffusion models gaining traction (LLaDA 2.0 at 100B params)

### 5. Inference-Time Scaling & Tool Use
- GPT 4.5 showed pure scaling has diminishing returns
- Better training pipelines + inference scaling drove progress
- Tool use significantly reduces hallucinations
- gpt-oss models designed with tool use in mind

### 6. "Benchmaxxing" Problem
- Llama 4 scored well on benchmarks but disappointed in practice
- Benchmark numbers no longer trustworthy indicators
- Useful as minimum thresholds, not for comparing models above threshold

### 7. AI for Coding/Writing/Research
- LLMs as "superpowers" for productivity
- Author writes core code himself, uses LLM for boilerplate
- Expert-crafted codebases not replaced by pure LLM generation
- Warning: Overusing LLMs can lead to burnout (hollow work)
- Chess analogy: AI as partner, not replacement

### 8. Private Data as Edge
- Companies declining to sell proprietary data to LLM providers
- LLM development becoming commoditized
- Prediction: Companies will develop in-house LLMs using private data

### 9. 2025 Surprises
- Gold-level math performance earlier than expected
- Llama fell out of favor; Qwen overtook in popularity
- Mistral 3 uses DeepSeek V3 architecture
- New contenders: Kimi, GLM, MiniMax, Yi
- MCP became standard for tool access
- OpenAI released open-weight model (gpt-oss)

### 10. 2026 Predictions
- Consumer-facing diffusion model (Gemini Diffusion first)
- Open-weight community adopts local tool use
- RLVR expands beyond math/code (chemistry, biology)
- Classical RAG fades as long-context handling improves
- Progress from tooling/inference rather than training alone

---

## Article Structure Analysis

### Length: ~6,500 words

### Sections Pattern:
1. **Chronological narrative** (starts with January 2025)
2. **Technical deep dives** with figures
3. **Personal reflections** (coding, writing, burnout)
4. **Industry analysis** (private data, commoditization)
5. **Personal updates** (books, research)
6. **Predictions** (concrete, numbered)
7. **Bonus content** for paid subscribers

### Visual Elements:
- 22+ figures referenced
- Comparison tables
- Architecture diagrams
- Training loss curves
- Code snippets
- Book covers

### Cross-references:
- Links to previous Ahead of AI articles
- Links to author's books
- Links to GitHub repositories

### Tone:
- First person, conversational
- Honest about limitations ("no one knows what these might look like")
- Practical advice mixed with technical content
- Personal anecdotes (consulting, writing process)
