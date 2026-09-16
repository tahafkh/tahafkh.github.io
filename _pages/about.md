---
layout: about
title: about
permalink: /
subtitle: Ph.D. student, <a href="https://oist.mlds.jp/">Machine Learning and Data Science Unit</a> · <a href="https://www.oist.jp/">OIST</a>

profile:
  align: right
  image: prof_pic.jpg
  image_circular: false # crops the image to make it circular
  more_info: >
    <p>Okinawa Institute of Science<br>and Technology (OIST)</p>
    <p>1919-1 Tancha, Onna-son<br>Okinawa 904-0495, Japan</p>

selected_papers: true # includes a list of papers marked as "selected={true}"
social: true # includes social icons at the bottom of the page

announcements:
  enabled: true # includes a list of news items
  scrollable: true # adds a vertical scroll bar if there are more than 3 news items
  limit: 5 # leave blank to include all the news in the `_news` folder

latest_posts:
  enabled: true
  scrollable: true # adds a vertical scroll bar if there are more than 3 new posts items
  limit: 3 # leave blank to include all the blog posts
---

I'm a Ph.D. student at [OIST](https://www.oist.jp/), in the [Machine Learning and Data Science Unit](https://oist.mlds.jp/) under [Prof. Makoto Yamada](https://www.oist.jp/research/research-units/mlds/makoto-yamada), co-supervised by [Prof. Kenji Doya](https://www.oist.jp/research/research-units/ncu/kenji-doya) of the [Neural Computation Unit](https://www.oist.jp/research/research-units/ncu).

I want to understand how a system that only ever sees sensory data ends up with knowledge that transfers — how brains do it, and why our models so often don't. That question keeps pulling me back to **neural representations**: the geometry a network settles into, and what that geometry commits the system to once the data runs out.

Lately I've been circling a more specific version of it. Curiosity-driven world models treat surprise as the learning signal, and the [free-energy](https://www.nature.com/articles/nrn2787) framing gives that signal a clean objective — but surprise and _learnable_ surprise are not the same quantity, and conflating them is what strands an agent in front of a noisy screen or in a dark room. Two recent ideas sharpen the distinction: [**epiplexity**](https://arxiv.org/abs/2601.03220), which asks what a computationally bounded observer can actually extract from data, and [**learnable novelty**](https://arxiv.org/abs/2607.18433), which isolates the fraction of novelty a learner can convert into knowledge. Set beside Wilson's argument that generalization is governed by [**soft inductive biases**](https://arxiv.org/abs/2503.02113) rather than hard constraints, the question I'd like to answer is: _given a learnable-novelty signal and a particular soft bias, which world model does the agent end up with?_ Not whether it learns, but what it learns.

Before OIST I did three rotations here — spiking basal-ganglia models of dopamine and temporal-difference learning with [Prof. Doya](https://www.oist.jp/research/research-units/ncu/kenji-doya), short-term plasticity and temporal associative memory with [Prof. Tomoki Fukai](https://www.oist.jp/research/research-units/ncbc/tomoki-fukai), and an evolutionary-developmental extension of curiosity-driven robot learning with [Prof. Jun Tani](https://www.oist.jp/research/research-units/cnru/jun-tani). Before that I worked with [Prof. Shervin Safavi](https://shervinsafavi.github.io/cmclab/) on how RNN architecture shapes internal dynamics, wrote a B.Sc. thesis on delay learning in spiking networks with [Prof. Mohammadreza Abolghasemi](https://profile.ut.ac.ir/en/~dehaqani) and [Prof. Timothée Masquelier](https://cerco.cnrs.fr/pagesp/tim/index.lab.htm), and spent a year as a data scientist at [Tapsi](https://tapsi.ir/en) helping start its data-science team.

Away from the desk: football, far too much of it. Also [bands](/bands/) and [games](/games/), and currently a losing battle with _Genki I_.
