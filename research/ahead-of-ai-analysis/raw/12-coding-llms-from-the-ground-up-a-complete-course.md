# Coding LLMs from the Ground Up: A Complete Course

**Date:** JUL 19, 2025

**URL:** https://magazine.sebastianraschka.com/p/coding-llms-from-the-ground-up

**Likes:** LIKE (2)

**Image Count:** 1

---

## Images

1. ![Figure](https://substackcdn.com/image/fetch/$s_!ye37!,w_140,h_140,c_fill,f_auto,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F367b547c-9d22-4a3d-b466-1d56ccc6b055_1844x1224.png)
   - Caption: Building LLMs from the Ground Up: A 3-hour Coding Workshop

---

## Full Text Content

I wrote a lot about reasoning models in recent months (4 articles in a row)! Next to everything "agentic," reasoning is one of the biggest LLM topics of 2025.

This month, however, I wanted to share more fundamental or "foundational" content with you on how to code LLMs, which is one of the best ways to understand how LLMs work.

Why? Many people really liked and benefited from the abbreviated LLM workshop I shared last year:

Building LLMs from the Ground Up: A 3-hour Coding Workshop
SEBASTIAN RASCHKA, PHD
·
AUGUST 31, 2024
Read full story

So, I thought this ~5× longer and more detailed content (~15 hours in total) would be even more useful.

Also, I'm sadly dealing with a bad neck injury and haven't really been able to work on a computer for the past 3 weeks. I am currently trying a conservative treatment before considering the suggested surgical route. This is the worst timing as I just started to get back on track before life threw another curveball.

So, during my recovery, I thought sharing these videos I recorded in the last couple of months would be a nice in-between content.

I hope you find this useful, and thanks for your support!

PS: The videos originally started as supplementary content for my Build a Large Language Model (From Scratch) book. But it turns out they also work pretty well as standalone content.

Why build from scratch?

It's probably the best and most efficient way to learn how LLMs really work. Plus, many readers have told me they had a lot of fun doing it.

To offer an analogy: if you are into cars and want to understand how they work, following a tutorial that walks you through building one from the ground up is a great way to learn. Of course, we probably wouldn't want to start by building a Formula 1 race car since it would be prohibitively expensive and overly complex for a first project. Instead, it makes more sense to start with something simpler, like a go-kart.

Building a go-kart still teaches you how the steering works, how the motor functions, and more. You can even take it to the track and practice (and have a lot of fun with it) before stepping into a professional race car (or joining a company or team that is focused on building one). After all, the best race drivers often got their start by building and tinkering with their own go-karts (think Michael Schumacher and Ayrton Senna). By doing that, they not only developed a great feel for the car but could also provide valuable feedback to their mechanics, which gave them an edge over the other drivers.

References

Build an LLM from Scratch book (Manning | Amazon)

Build an LLM from Scratch GitHub repository

1 - Set up your code environment (0:21:01)

This is a supplementary video explaining how to set up a Python environment using uv.

In particular, we are using “uv pip”, which is explained in this document.

Alternatively, the native “uv add” syntax (mentioned but not explicitly covered in this video) is described here.

Note / Tip: The installation may cause issues on certain versions of Windows. If you are on a Windows machine and have troubles with the installation (likely due to a TensorFlow dependency to load the original GPT-2 model weights from OpenAI in video 5), please don’t worry about it and feel free to skip the TensorFlow installation (you can do this by removing the TensorFlow line from the requirements file.)

To provide an alternative, I converted the GPT-2 model weights from a TensorFlow tensor format to PyTorch tensors and shared them on the Hugging Face model hub, which you can use as an alternative to the weight loading portion in video 5: https://huggingface.co/rasbt/gpt2-from-scratch-pytorch.

In any case, you don’t have to worry about this weight-loading code until the end of video 5.

2 - Working with text data (1:28:01)

This video goes over text data preparations steps (tokenization, byte pair encoding, data loaders, etc.) for LLM training.

3 - Coding attention mechanisms (2:15:40)

This is a supplementary video explaining how attention mechanisms (self-attention, causal attention, multi-head attention) work by coding them from scratch.
You can think of it as building the engine of a car (before adding the frame, seats, and wheels).

4 - Set up your code environment (0:21:01)

This video covers how to code an LLM architecture from scratch.

5 - Pretraining on Unlabeled Data (2:36:44)

This video explains how to pretrain a LLM from scratch.

6 - Finetuning for Classification (2:15:29)

This is a video explaining how to fine-tune an LLM as a classifier (here using a spam classification example) as a gentle introduction to finetuning, before instruction finetuning the LLM in the next video.

7 - Instruction Finetuning (1:46:04)

Finally, this video explains how to instruction finetune the LLM.

Happy viewing & tinkering!

Bonus: LLMs Then And Now (From 2018 to 2025)

As a big thank you to the paid subscribers, I want to share a 2.5h (non-coding) bonus video I recorded earlier in April, approximately 2 days after the Llama 4 release. In this talk, I discuss the current LLM landscape in 2025 with a focus on what and how things have changed since GPT-2 in 2018.

Thanks for your support, as an independent and self-employed researcher, this really means a lot to me!

Hopefully, things will improve in the next few weeks/months as I have lots of ideas for upcoming articles and can’t wait to work on them!

In addition, you can find a link to the slides here:

https://sebastianraschka.com/pdf/slides/2025-04-llms-whats-next.pdf

And below is a table of contents for the video:

00:00 LLM Specialization

17:24 LLM Architecture changes

22:42 Mixture of Experts (MoE)

32:35 Multi-Head Latent Attention (MLA)

36:47 Model sizes over the years

43:39 Pre-training

50:09 Hardware

58:04 Training complexity

1:09:01 Pre-training datasets

1:24:22 Instruction fine-tuning

1:34:08 Preference tuning

1:46:17 Reasoning specialization

1:58:18 Different ways to build reasoning models

2:06:14 DeepSeek case study

2:19:21 Affordable reasoning model experiments

I hope you found this video useful, and many thanks for your support!