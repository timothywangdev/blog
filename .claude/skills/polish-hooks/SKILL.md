---
name: polish-hooks
description: Reader engagement, titles, and conversion
---

# Reader Hooks & Engagement

Optimize openings, titles, and structure for reader engagement and conversion.

**Use with:** `/polish` (core workflow)

## The 3-Second Rule

You have **3 seconds** to answer: "Why should I care?"

The opening must answer:
1. Who is this for?
2. What will they learn?

## Problem-First Opening (PAS Framework)

Lead with **relatable pain**, not the paper or solution.

```
1. PROBLEM: Specific pain point
   "Your model trains fine, then collapses at inference."

2. AGITATE: Make it vivid
   "You've wasted 3 days debugging. The demo is tomorrow."

3. SOLUTION: Hint at the fix
   "Turns out there's a simple reason — and a fix."
```

**Example:**

❌ Academic: "In March 2023, Chi et al. published..."

✅ Problem-first: "Train a robot to avoid an obstacle. Show it 100 demos going left, 100 going right. What does it learn? It drives straight into the wall."

## What Hooks Each Audience

| Audience | What hooks them |
|----------|-----------------|
| ML Engineers | "This is now the standard" / adoption signal |
| PhD Students | Elegant insight that solves hard problem |
| Software Engineers | Concrete failure → concrete fix |
| Founders/PMs | Market signal, who's using it |
| Hobbyists | "Here's what was broken and why" |

## Hook Types

| Type | Example |
|------|---------|
| Surprising data | "46.9% improvement over everything before" |
| Counterintuitive claim | "Position control beats velocity control" |
| Specific failure | "Your Docker containers are leaking memory" |
| Question they've wondered | "Why does Transformer attention work?" |
| Bold statement | "Behavioral cloning is fundamentally broken" |

## Title Patterns

**Works:**
- "Why X Keeps Failing (And How Y Fixed It)"
- "The Paper That Changed How We Do X"
- "X Explained: What the Tutorials Get Wrong"

**Avoid:**
- Generic: "Part 1: Introduction to X"
- No benefit: "Thoughts on Diffusion Models"

## Social Proof

Include early:
- Citation counts
- Awards, venue prestige
- Who's using it (companies, labs)

Example: "2,000+ citations in 2 years. Now the foundation of every major robot learning system."

## TL;DR Structure

```
[One sentence: What this is and why it matters]

- **The problem**: [Relatable pain]
- **The solution**: [Core insight]
- **The result**: [Concrete outcome with numbers]
```

3-4 bullets max. Readers should get it in 10 seconds.

## Conversion Flow

```
Free content delivers value
    ↓
Reader thinks "this person knows their stuff"
    ↓
Tease depth: "In Part 2, we go deeper on X"
    ↓
Gentle invitation, not pressure
```

**Paywall placement:** Value first, gate second.

**CTAs:** See `/substack-publish` for subscribe button placement during publishing.

## What NOT to Do

- Don't manufacture emotional drama
- Don't overstate claims
- Don't hide information for artificial scarcity
- Don't use fluffy language — be specific
- Don't tell them what to think — give facts

## The Read-Aloud Test

Read your opening aloud. If you stumble, rewrite it. If it sounds like marketing copy, rewrite it. Should sound like explaining to a smart colleague over coffee.

## Task

- [ ] Rewrite opening using PAS framework if needed
- [ ] Check title follows working patterns
- [ ] Add social proof early (citations, who's using it)
- [ ] Verify TL;DR is scannable (10 seconds)
- [ ] Read opening aloud — rewrite if you stumble
