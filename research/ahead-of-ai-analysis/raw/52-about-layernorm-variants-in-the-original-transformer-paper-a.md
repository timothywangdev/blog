# About LayerNorm Variants in the Original Transformer Paper, and Some Other Interesting Historical Tidbits About LLMs

**Date:** JUL 19, 2025

**URL:** https://magazine.sebastianraschka.com/p/why-the-original-transformer-figure

**Likes:** LIKE (2)

**Image Count:** 6

---

## Images

1. ![Figure](https://substackcdn.com/image/fetch/$s_!RaNK!,w_140,h_140,c_fill,f_auto,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fd9a0766d-2e52-4af0-96c5-3e07a30d6ecb_1868x1130.png)
   - Caption: Understanding Large Language Models

2. ![Figure](https://substackcdn.com/image/fetch/$s_!50Ij!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fcd9a088a-db49-470e-b243-979170219fe9_2040x956.png)
   - Caption: Sources: https://arxiv.org/abs/1706.03762 (left and center) and https://arxiv.org/abs/2002.04745 (right)

3. ![Figure](https://substackcdn.com/image/fetch/$s_!5HTQ!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F0216bdfb-a7d8-4805-861b-4dd8c0ff1dec_884x894.png)
   - Caption: Source: Annotated figure based on https://people.idsia.ch//~juergen/fast-weight-programmer-1991-transformer.html#sec2

4. ![Figure](https://substackcdn.com/image/fetch/$s_!HD3q!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fff930b7d-7aa2-459f-acfe-f9bab75d1b2e_1762x850.png)
   - Caption: Source: https://arxiv.org/abs/1801.06146

5. ![Figure](https://substackcdn.com/image/fetch/$s_!VLG9!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fb4fd3005-6548-4976-9459-d7768e26978d_1788x1408.png)
   - Caption: Source: Figure from https://arxiv.org/abs/2112.11446

6. ![Figure](https://substackcdn.com/image/fetch/$s_!CxIZ!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F27b6d27d-1052-4a4f-a419-a69cdd36704a_1118x454.png)
   - Caption: Machine Learning with PyTorch and Scikit-Learn, Machine Learning Q and AI, and Build a Large Language Model (from Scratch)

---

## Full Text Content

A few months ago, I shared the article, Understanding Large Language Models: A Cross-Section of the Most Relevant Literature To Get Up to Speed, and the positive feedback was very motivating! So, I also added a few papers here and there to keep the list fresh and relevant.

Understanding Large Language Models
SEBASTIAN RASCHKA
·
APRIL 16, 2023
Read full story

At the same time, keeping this list concise is useful and important so that someone can get up to speed in a reasonable time. However, there are also a few key papers that, in hindsight, are very informative and should be included.

This time, I want to share four useful papers to understand transformers from a more historical perspective. While I just added them to the Understanding Large Language Models article directly, I am also sharing them here in this separate article to make them easier to find for those who have already read through the Understanding Large Language Models before.

(1) On Layer Normalization in the Transformer Architecture (2020) by Xiong, Yang, He, K Zheng, S Zheng, Xing, Zhang, Lan, Wang, and Liu, https://arxiv.org/abs/2002.04745

While the original transformer figure above (from Attention Is All You Need, https://arxiv.org/abs/1706.03762) is a helpful summary of the original encoder-decoder architecture, the location of the LayerNorm in this figure remains a hotly debated subject.

For instance, the Attention Is All You Need transformer figure places the layer normalization between the residual blocks, which doesn't match the official (updated) code implementation accompanying the original transformer paper. The variant shown in the Attention Is All You Need figure is known as Post-LN Transformer, and the updated code implementation defaults to the Pre-LN variant.

The Layer Normalization in the Transformer Architecture paper suggests that Pre-LN works better, addressing gradient problems, as shown below. Many architectures adopted this in practice, but it can result in representation collapse.

So, while there's still an ongoing discussion regarding using Post-LN or Pre-LN, there's also a new paper that proposes taking advantage of both worlds: ResiDual: Transformer with Dual Residual Connections (https://arxiv.org/abs/2304.14802); whether it will turn out useful in practice remains to be seen.

Sources: https://arxiv.org/abs/1706.03762 (left and center) and https://arxiv.org/abs/2002.04745 (right)

(2) Learning to Control Fast-Weight Memories: An Alternative to Dynamic Recurrent Neural Networks (1991) by Schmidhuber, https://www.semanticscholar.org/paper/Learning-to-Control-Fast-Weight-Memories%3A-An-to-Schmidhuber/bc22e87a26d020215afe91c751e5bdaddd8e4922

This paper is recommended for those interested in historical tidbits and early approaches fundamentally similar to modern transformers.

For instance, in 1991, which is about two-and-a-half decades before the original transformer paper above ("Attention Is All You Need"), Juergen Schmidhuber proposed an alternative to recurrent neural networks called Fast Weight Programmers (FWP). The FWP approach involves a feedforward neural network that slowly learns by gradient descent to program the changes of the fast weights of another neural network.

The analogy to modern transformers is explained in this blog post as follows:

In today's Transformer terminology, FROM and TO are called key and value, respectively. The INPUT to which the fast net is applied is called the query. Essentially, the query is processed by the fast weight matrix, which is a sum of outer products of keys and values (ignoring normalizations and projections). Since all operations of both networks are differentiable, we obtain end-to-end differentiable active control of fast weight changes through additive outer products or second order tensor products.[FWP0-3a] Hence the slow net can learn by gradient descent to rapidly modify the fast net during sequence processing. This is mathematically equivalent (apart from normalization) to what was later called Transformers with linearized self-attention (or linear Transformers).

As mentioned in the blog post excerpt above, this approach is now called "linear Transformers" or "Transformers with linearized self-attention" via the more recent papers Transformers are RNNs: Fast Autoregressive Transformers with Linear Attention and Rethinking Attention with Performers that appeared on arXiv in 2020.

In 2021, the Linear Transformers Are Secretly Fast Weight Programmers paper then explicitly showed the equivalence between linearized self-attention and the fast weight programmers from the 1990s.

Source: Annotated figure based on https://people.idsia.ch//~juergen/fast-weight-programmer-1991-transformer.html#sec2

(3) Universal Language Model Fine-tuning for Text Classification (2018) by Howard and Ruder, https://arxiv.org/abs/1801.06146

This is another paper that's very interesting from a historical perspective. While it was written one year after the original Attention Is All You Need transformer was released, it doesn't involve transformers but instead focuses on recurrent neural networks. However, it's still noteworthy since it effectively proposed pretraining language models and transfer learning for downstream tasks.

While transfer learning was already established in computer vision, it wasn't yet prevalent in natural language processing (NLP). ULMFit was among the first papers to demonstrate that pretraining a language model and finetuning it on a specific task could yield state-of-the-art results in many NLP tasks.

The three-stage process for finetuning the language models suggested by ULMFit was as follows:

Train a language model on a large corpus of text.

Finetune this pretrained language model on task-specific data, allowing it to adapt to the specific style and vocabulary of the text.

Finetune a classifier on the task-specific data with gradual unfreezing of layers to avoid catastrophic forgetting.

This recipe -- training a language model on a large corpus and then finetuning it on a downstream task -- is the central approach used in transformer-based models and foundation models like BERT, GPT-2/3/4, RoBERTa, and others.

However, the gradual unfreezing, a key part of ULMFiT, is usually not routinely done in practice when working with transformer architectures, where all layers are typically finetuned at once.

Source: https://arxiv.org/abs/1801.06146

(4) Scaling Language Models: Methods, Analysis & Insights from Training Gopher (2022) by Rae and colleagues (78 co-authors!), https://arxiv.org/abs/2112.11446

Gopher is a particularly nice paper including tons of analysis to understand LLM training. Here, the researchers trained a 280 billion parameter model with 80 layers on 300 billions tokens. This includes interesting architecture modifications such as using RMSNorm (Root Mean Square Normalization) instead of LayerNorm (Layer Normalization). Both LayerNorm and RMSNorm are preferred over BatchNorm since they don't depend on the batch size and doesn't require synchronization, which is an advantage in distributed settings with smaller batch sizes. However, RMSNorm is generally said to stabilize the training in deeper architectures.

Besides interesting tidbits such the ones above, the main focus of this paper is the analysis of task performance for different scales. The evaluation on 152 diverse tasks reveal that increasing model sizes benefits tasks like comprehension, fact-checking, and the identification of toxic language the most. However, tasks related to logical and mathematical reasoning benefit less from architecture scaling.

Source: Figure from https://arxiv.org/abs/2112.11446

This magazine is a personal passion project that does not offer direct compensation. However, for those who wish to support me, please consider purchasing a copy of one of my books. If you find them insightful and beneficial, please feel free to recommend them to your friends and colleagues.

Machine Learning with PyTorch and Scikit-Learn, Machine Learning Q and AI, and Build a Large Language Model (from Scratch)

Your support means a great deal! Thank you!