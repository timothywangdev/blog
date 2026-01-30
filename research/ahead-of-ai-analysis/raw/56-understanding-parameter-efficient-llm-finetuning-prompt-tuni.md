# Understanding Parameter-Efficient LLM Finetuning: Prompt Tuning And Prefix Tuning

**Date:** JUL 19, 2025

**URL:** https://magazine.sebastianraschka.com/p/understanding-parameter-efficient

**Likes:** LIKE (1)

**Image Count:** 8

---

## Images

1. ![Figure](https://substackcdn.com/image/fetch/$s_!lJ3t!,w_140,h_140,c_fill,f_auto,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa534808e-9284-47eb-9b4d-3e3aedc0b5da_1180x842.png)
   - Caption: Finetuning Large Language Models

2. ![Figure](https://substackcdn.com/image/fetch/$s_!mNEc!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Ff3624f88-e572-4dd6-b06a-b5e5442aec27_1746x718.png)
   - Caption: A selection of parameter-efficient finetuning techniques covered in this article.

3. ![Figure](https://substackcdn.com/image/fetch/$s_!U1xT!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fe1eeee00-21d3-40c6-ad51-a1489c62678a_1582x330.png)
   - Caption: An example of hard prompt tuning, that is, rearranging the input to get better outputs.

4. ![Figure](https://substackcdn.com/image/fetch/$s_!0cMd!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F9419bfad-62d8-4a7a-b04c-02a4ba99eafd_2044x1082.png)
   - Caption: Pseudo-code illustrating the concept of soft prompting.

5. ![Figure](https://substackcdn.com/image/fetch/$s_!JCuv!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa6759987-0dda-4356-b3b2-f835fd1f82c9_2148x1144.png)
   - Caption: Annotated figure from soft prompting paper, https://arxiv.org/abs/2104.08691.

6. ![Figure](https://substackcdn.com/image/fetch/$s_!qaFN!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fbf5c7f2d-a30d-42fe-9fc5-0936eb60c467_2104x1242.png)
   - Caption: Illustration of prefix tuning.

7. ![Figure](https://substackcdn.com/image/fetch/$s_!nZ4j!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F312dfd19-a7d4-4a24-88f0-2f9736718706_1360x710.png)
   - Caption: Pseudo-code illustration of prefix tuning.

8. ![Figure](https://substackcdn.com/image/fetch/$s_!sVId!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F7edd462c-e270-4ee6-82db-e2fc9f4d945c_1788x1758.png)
   - Caption: Annotated figures from the Prefix Tuning paper by Li and Liang.

---

## Full Text Content

Last week, I shared an overview of different Large Language Model (LLM) finetuning techniques. In a series of short articles, I am planning to discuss a selection of the most relevant techniques one by one.

Finetuning Large Language Models
SEBASTIAN RASCHKA
·
APRIL 22, 2023
Read full story

Let's start with a selection of parameter-efficient finetuning techniques concerning prompt modifications.

A selection of parameter-efficient finetuning techniques covered in this article.
Prompt Tuning

The original concept of prompt tuning refers to techniques that vary the input prompt to achieve better modeling results. For example, suppose we are interested in translating an English sentence into German. We can ask the model in various different ways, as illustrated below.

An example of hard prompt tuning, that is, rearranging the input to get better outputs.

Now, this concept illustrated above is referred to as hard prompt tuning since we directly change the discrete input tokens, which are not differentiable.

In contrast to hard prompt tuning, soft prompt tuning (Lester et al. 2021) concatenates the embeddings of the input tokens with a trainable tensor that can be optimized via backpropagation to improve the modeling performance on a target task.

In pseudocode, this looks like as follows:

Pseudo-code illustrating the concept of soft prompting.

Soft prompts differ from the discrete text prompts in that they are acquired through back-propagation and is thus adjusted based on loss feedback from a labeled dataset.

Soft prompt tuning is significantly more parameter-efficient than full-finetuning, although the modeling performance of soft prompt-finetuned model can be slightly worse as shown in the figure below.

Annotated figure from soft prompting paper, https://arxiv.org/abs/2104.08691.

On the other hand, if the model has 11B as shown in the figure above, soft prompt tuning matches the performance of full fine tuning (for reference, the smallest LLaMA model has 7B parameters, the largest LLaMA model has 65B parameters.)

Storage efficiency

If we finetune a pretrained model for a specific task, we have to keep a separate copy of the entire model for each of these tasks. However, with prompt tuning, only a small task-specific (soft) prompt needs to be stored for each task. For instance, a T5 "XXL" model requires 11 billion parameters for each copy of the fine-tuned model. In contrast, the tuned prompts only require 20,480 parameters per task, assuming a prompt length of 5 tokens and a 4096-dimensional embedding size. This represents a reduction of over five orders of magnitude.

From Prompt Tuning to Prefix Tuning

Now, a specific, independently developed flavor of prompt tuning is prefix tuning (Li & Liang 2021). The idea in prefix tuning is to add trainable tensors to each transformer block instead of only the input embeddings, as in soft prompt tuning. Also, we obtain the soft prompt embedding via fully connected layers (a mini multilayer perceptron with two layers and a nonlinear activation function in between). The following figure illustrates the difference between a regular transformer block and a transformer block modified with a prefix.

Illustration of prefix tuning.

Note that in the figure above, the “fully connected layers” refer to a small multilayer perceptron (two fully connected layers with a nonlinear activation function in-between). These fully connected layers embed the soft prompt in a feature space with the same dimensionality as the transformer-block input to ensure compatibility for concatenation.

Using (Python) pseudo-code, we can illustrate the difference between a regular transformer block and a prefix-modified transformer block as follows:

Pseudo-code illustration of prefix tuning.

According to the original prefix tuning paper, prefix tuning achieves comparable modeling performance to finetuning all layers while only requiring the training of 0.1% of the parameters – the experiments were based on GPT-2 models. Moreover, in many cases, prefix tuning even outperformed the finetuning of all layers, which is likely because fewer parameters are involved, which helps reduce overfitting on smaller target datasets.

Annotated figures from the Prefix Tuning paper by Li and Liang.

Lastly, to clarify the use of soft prompts during inference: after learning a soft prompt, we have to supply it as a prefix when performing the specific task we finetuned the model on. This allows the model to tailor its responses to that particular task. Moreover, we can have multiple soft prompts, each corresponding to a different task, and provide the appropriate prefix during inference to achieve optimal results for a particular task.

Prefix Versus Prompt Tuning

How do soft prompt tuning and prefix tuning compare performance-wise?

Prefix tuning

Unfortunately, since both methods were developed independently and published around the same time, the respective papers don't include a direct comparison. Furthermore, when searching the later parameter-efficient LLM literature, I couldn't find a benchmark that included both of these methods.

Prefix tuning modifies more layers of the model by inserting a task-specific prefix to the input sequence, thus requiring more parameters to be finetuned. On the other hand, soft prompt tuning involves only finetuning the input prompt embeddings, resulting in fewer parameters being updated. This may make soft prompt tuning more parameter-efficient than prefix tuning, but it could also limit its capacity to adapt to the target task.

Regarding performance, it is reasonable to expect that prefix tuning might perform better since it has more parameters to adjust the model to the new task. However, this may come at the cost of increased computational resources and a higher risk of overfitting. On the other hand, soft prompt tuning might be more computationally efficient, but the smaller number of finetuned parameters could limit the modeling performance.

Conclusion

This article covered a subset of parameter-efficient finetuning techniques. Both of these techniques, soft prompt tuning, and prefix tuning, only require a few parameters compared to full finetuning.

Furthermore, in practice, soft prompt tuning may be particularly attractive because we only need to modify the input embeddings, not the inner transformer blocks as in prefix tuning.

Before you jump into action and try implementing these techniques, I'd say stay tuned for even more interesting parameter-efficient finetuning techniques: Adapters, LLaMA-Adapter (related but also different from regular adapters), and Low-Rank Adaptation (LoRA). I am planning to cover these in the upcoming weeks!