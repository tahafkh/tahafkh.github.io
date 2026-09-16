---
layout: post
title: Surprise you can use
date: 2026-09-16 21:00:00+0900
description: Curiosity-driven agents optimize surprise. Two recent papers argue the quantity that matters is the part of surprise you can actually learn from — which changes the question from whether a world model forms to which one.
tags: world-models neuroai
related_posts: false
---

There is an old embarrassment at the heart of curiosity-driven learning, and it comes in two mirror-image forms.

Point a novelty-seeking agent at a screen of television static and it will sit there forever. Every frame is maximally surprising; every frame is worth nothing. This is the **noisy-TV problem**. Run the argument the other way — take an agent that minimizes surprise, as the free-energy principle prescribes — and it finds a dark, quiet corner and stays in it. Nothing unexpected ever happens again. This is the **dark-room problem**.

The two failures are usually filed separately, one as a bug in intrinsic motivation and one as a philosophical objection to Friston. I think they are the same bug. Both objectives treat _surprise_ as a single scalar, when it is plainly two things glued together: the part of an observation you could, with effort, come to predict, and the part you could not, ever, no matter how long you looked. Static is all of the second kind. A dark room has neither. Maximize the sum and you get static; minimize the sum and you get the dark room. Neither objective ever had the vocabulary to say _"interesting"_.

## Splitting the scalar

Two papers from this year take that split seriously, from different directions.

[Finzi et al.](https://arxiv.org/abs/2601.03220) introduce **epiplexity**, which asks what a _computationally bounded_ observer can extract from data. Their starting point is a set of results that ought to bother anyone who trains models for a living: information cannot be increased by deterministic transformations; information is independent of the order of the data; likelihood modeling is "merely" distribution matching. Every one of these is true in Shannon's frame and false in practice — we reorder data and models get better, we transform data and models get better. The resolution is that Shannon and Kolmogorov both assume unbounded compute. Epiplexity carves off what they call _time-bounded entropy_ — the content that is unpredictable only because you can't afford to predict it, the output of a good PRNG, the trajectory of a chaotic system past its Lyapunov horizon — and keeps the structural remainder. Static is almost entirely time-bounded entropy. It is not that the static carries no bits; it is that no bounded learner will ever turn those bits into a program.

[Zhang and Levin](https://arxiv.org/abs/2607.18433) arrive from the agent side with **learnable novelty**: isolate the fraction of novelty a learner can convert into knowledge, make it differentiable, optimize it. Their claim is that novelty search and the free-energy principle are two projections of this one quantity, and that their characteristic failures are what you get when you project badly. They then show complexity generation, abstraction, and exploration falling out of the same objective across cellular automata, image encoding, and RL.

So: the same cut, made twice, once as a theory of data and once as a theory of drive. That convergence is what made me pay attention.

## Why this changes the question

Here is the part I keep turning over. Suppose you hand an agent a clean learnable-novelty signal. It will no longer stare at static and it will no longer hide in the dark. Good. But the signal tells you _that_ there is structure worth acquiring — it does not tell you _which_ structure the agent will end up representing. Two agents with identical learnable-novelty objectives, pointed at the same environment, can walk away with different world models.

What separates them is the model's inductive bias, and this is where [Wilson's](https://arxiv.org/abs/2503.02113) argument becomes load-bearing for me. His case is that the generalization behaviour we find mysterious in deep networks — benign overfitting, double descent, the success of overparametrization — is neither unique to neural networks nor especially strange, once you stop thinking in terms of _restricting_ the hypothesis space and start thinking in terms of a flexible space with a **soft preference** for simpler solutions consistent with the data. Not a constraint. A tilt.

Put the two together and the question I actually want to answer comes out:

> Given a learnable-novelty signal and a particular soft inductive bias, **which** world model does the agent converge to?

Not whether it learns. What it learns. The novelty signal decides where the agent spends its data budget; the soft bias decides which of the many models consistent with that data it settles into. Those are different knobs and I don't think we understand how they interact.

## The manifold is where I'd look

My instinct is that this is a question about representational geometry, which is where I came from and where I keep ending up.

If you record a population of neurons — biological or artificial — during a structured task, the activity does not fill its ambient space. It concentrates on a low-dimensional **neural manifold**, and the shape of that manifold is not incidental. It encodes what the system takes to be the degrees of freedom of its world. Two systems that solve the same task with different manifold geometry have, in a real sense, different theories of the task, and they will generalize differently the moment the task shifts.

That makes the manifold a natural measuring instrument for the question above. A soft inductive bias should be visible as a systematic distortion of the geometry an agent settles into — not as a hard constraint on what it _can_ represent, but as a tilt in what it _does_ represent. And a learnable-novelty signal should be visible in which parts of that geometry get refined and which stay coarse.

There is a methodological wrinkle, which is that comparing dynamics across systems at scale is genuinely hard — geometric metrics are cheap but blind to the dynamics, and faithful dynamical metrics have historically been too expensive to run at the scale you'd need for a sweep over biases. This is the problem [fastDSA](https://arxiv.org/abs/2511.22828) was built for, which is convenient, because a sweep over inductive biases is exactly the kind of experiment that needs hundreds of pairwise comparisons.

## What I don't know yet

Plenty. Whether epiplexity is estimable cheaply enough to serve as an online learning signal rather than a post-hoc diagnostic. Whether "soft inductive bias" can be made concrete enough to vary systematically, or whether it stays a useful description that resists being turned into a knob. Whether manifold geometry is the right readout at all, or a convenient one that happens to be measurable.

And a biological question underneath all of it, which is the one I actually care about: brains clearly do not chase static, and clearly do not seek out dark rooms. Whatever implements that distinction in a nervous system, it does it cheaply, online, and without anyone computing a Kolmogorov complexity. If epiplexity is the right abstraction, something must be approximating it in neural hardware. I would like to know what.

_Corrections and disagreements welcome — [email](mailto:mohammad.fakharian@oist.jp) is best._
