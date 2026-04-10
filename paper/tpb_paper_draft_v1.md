# The Trust Percolation Bound: Correlated Trust Failure and the Topology of Governance Transitions

**Amadeus Brandes**

**Draft — April 2026**

---

## Abstract

Trust-based governance fails not because bilateral trust erodes, but because trust failures become correlated. This paper models trust as decision-relevant information that depreciates unless refreshed, and shows that when the network of trust intermediation becomes sufficiently connected, local failures cascade systemically. The paper derives an exact analytic floor for cascade initiation — the minimum contagion sensitivity below which no secondary trust failure can occur, regardless of network structure — and demonstrates computationally that the materiality boundary converges to this floor as effective connectivity increases. The transition from trust-viable to cascade-exposed coordination is sharp, topology-dependent in severity, and governed primarily by network structure, with bilateral trust quality entering through the coordination threshold and contagion sensitivity parameters. These results provide a measurable critical condition for governance transitions, distinguishing this theory from transaction-cost economics and embeddedness approaches that predict smooth institutional scaling rather than abrupt regime shifts.

---

## 1. Introduction

Every coordination system faces a foundational choice: trust or verify. Small communities coordinate through trust — internalized models of each other's behavior, built through repeated costly interaction. Large institutions coordinate through verification — contracts, audits, compliance frameworks, cryptographic proof. The transition between these regimes is among the most consequential structural events in economic and institutional life.

The existing literature treats this transition as driven by scaling pressures. Transaction cost economics locates the driver in asset specificity and bounded rationality (Williamson 1975, 1985). Embeddedness theory points to the erosion of social relations (Granovetter 1985). Commons governance research identifies institutional design conditions under which self-governance succeeds or fails (Ostrom 1990). These frameworks are insightful but share a common limitation: they do not predict *when* the governance transition occurs, *why* it is often abrupt rather than gradual, or *whether* it is reversible. "Increasing complexity" and "rising transaction costs" are descriptions, not mechanisms.

This paper derives the governance transition from two foundations: information theory and percolation theory. The central claim is that governance architecture is determined primarily not by the quality of bilateral trust relationships, but by the *topology of correlated trust dependence* — the network structure through which trust failures propagate. Bilateral trust quality enters through two parameters — the coordination threshold $\tau$ and the contagion sensitivity $\rho$ — but the phase boundary is governed by effective connectivity conditional on contagion sensitivity exceeding the initiation floor. There exists a measurable threshold at which local trust failures become systemically correlated. Below it, relational governance is viable. Above it, verification dominates.

The paper makes three contributions. First, it derives an exact analytic condition — the *cascade initiation floor* — below which no secondary trust failure can occur under a single-node shock, regardless of network structure (Proposition 1). Second, it demonstrates computationally that the materiality boundary converges to this floor as network connectivity increases, producing a sharp phase boundary in the space of connectivity and contagion sensitivity (Benchmark Result 1). Third, it shows that effective branching governs cascade onset while network topology governs cascade severity conditional on onset (Benchmark Result 2). Together, these results provide a formal basis for predicting governance transitions as critical phenomena rather than smooth institutional drift.

---

## 2. Trust as Stored Information

### 2.1 Trust as Information Gain

Let $G = (V, E)$ be a network of $n$ agents. Agent $i$'s trust in agent $j$ is defined as the information $i$ has accumulated about $j$'s decision function, measured as the divergence from a maximum-ignorance prior.

**Definition 1 (Trust).** Let $p_{ij}(\theta)$ be agent $i$'s posterior distribution over agent $j$'s decision function $\theta$, and let $p_0(\theta)$ be the uninformed prior. The trust of $i$ in $j$ is:

$$I_{ij} = D_{\text{KL}}\left( p_{ij}(\theta) \| p_0(\theta) \right)$$

When $I_{ij}$ is large, agent $i$ has a specific, confident model of $j$'s behavior. When $I_{ij} \approx 0$, $i$ knows nothing about $j$ beyond base rates. This quantity is non-negative, invariant to reparameterization of $\theta$, and naturally connected to Bayesian learning: each observation about $j$'s behavior updates $p_{ij}$ and increases $I_{ij}$ on average.

**Definition 2 (Network trust stock).** The total trust stock of the network is $\mathcal{I}(G) = \sum_{e_{ij} \in E} I_{ij}$, measuring the aggregate decision-relevant information embedded in the network's trust relationships.

### 2.2 Trust Depreciation

Trust models decay under noise. Personnel turnover replaces the individual whose behavior was modeled. Changing incentives shift decision functions. Strategic drift makes old observations less predictive. Even without betrayal, the posterior $p_{ij}$ drifts back toward the prior $p_0$.

**Definition 3 (Trust depreciation).** The information content of edge $e_{ij}$ depreciates at rate $\gamma_{ij}$:

$$\frac{dI_{ij}}{dt} = -\gamma_{ij} \cdot I_{ij} + r_{ij}(t)$$

where $r_{ij}(t)$ is the refresh rate from ongoing interaction. Maintaining trust at steady state requires continuous expenditure at rate $r_{ij}^* = \gamma_{ij} \cdot I_{ij}^*$. This expenditure is observable: regular meetings, relationship maintenance, shared risk-taking. These are informational expenditures required to keep $p_{ij}$ from reverting to $p_0$.

### 2.3 The Construction–Destruction Asymmetry

Building a trust relationship requires accumulating information incrementally through costly signals. Destroying it requires only a single sufficiently informative defection that resets the posterior to the prior or beyond. Formally, construction is $O(I_{ij} / \bar{r})$ in time; destruction is $O(1)$. This asymmetry, well-documented empirically (Slovic 1993; Kramer 1999), is a structural feature of Bayesian learning under asymmetric signal informativeness.

---

## 3. Correlated Trust Dependence

### 3.1 Three Distinct Graphs

To avoid conflation, we distinguish three network structures:

**The direct trust graph $G_T$.** An edge exists if agent $i$ has accumulated non-trivial information about $j$ through direct interaction.

**The coordination dependence graph $G_C$.** An edge exists if agents $i$ and $j$ must coordinate — they depend on each other's actions.

**The trust intermediation graph $G_I$.** An edge exists if agent $i$'s trust in some third agent depends on information routed through $j$. This graph determines how trust failures propagate.

The central theoretical object is $G_I$. Governance transitions occur when $G_I$ exhibits sufficient connectivity for local failures to cascade.

### 3.2 Inferred Trust and the Cascade Model

When agents cannot interact directly with all coordination partners, they rely on inferred trust through intermediaries.

**Definition 4 (Coordination threshold).** A pair $(i,j)$ is *trust-coordinable* if the effective trust across their best path in $G_I$ exceeds a minimum threshold: $I_{\text{eff}}(i,j) \geq \tau$, where $\tau > 0$ is the minimum information required for trust-based coordination.

**Definition 5 (Cascade model).** In the benchmark model, each edge in $G_I$ carries trust stock $I_e$, initialized at $I_0$. A single-node shock removes all edges incident to a target node. Surviving edges adjacent to failed edges are then updated:

$$I_e \leftarrow I_e \cdot (1 - \rho)^{h_e}$$

where $h_e$ is the number of failed edges adjacent to $e$ (the *hit count*) and $\rho \in (0,1)$ is the *contagion sensitivity* — how much a neighboring failure degrades an edge's trust stock. Any edge whose trust stock drops below $\tau$ fails and joins the cascade. The process iterates until no further edges fail.

**Definition 6 (Cascade size).** The cascade size $|\mathcal{C}|$ is the number of agent pairs that were trust-coordinable before the shock but are no longer coordinable after the cascade stabilizes, *net of* the direct disruption from removing the target node. This net secondary cascade isolates the amplification effect from the mechanical baseline.

### 3.3 Control Parameters

**Definition 7 (Effective connectivity).** The effective connectivity of $G_I$ is the Molloy–Reed branching factor:

$$B = \frac{\langle k^2 \rangle - \langle k \rangle}{\langle k \rangle}$$

where $\langle k \rangle$ and $\langle k^2 \rangle$ are the first and second moments of the degree distribution. In Erdős–Rényi random graphs, $B = \langle k \rangle$; the giant component emerges at $B = 1$.

The two control parameters of the model are $B$ (effective connectivity of $G_I$) and $\rho$ (contagion sensitivity). The coordination threshold $\tau$ is treated as a fixed system parameter.

---

## 4. The Cascade Initiation Floor

### 4.1 Proposition 1

**Proposition 1.** *Under the benchmark update rule with a single-node shock, if*

$$\rho \leq 1 - \sqrt{\tau}$$

*then no secondary edge failure can occur. The cascade size is zero on any graph.*

**Proof.** On the first post-shock update, every surviving edge can receive hits from at most two directions: through its two endpoints. Each endpoint contributes at most one hit from an adjacent failed edge. Therefore the maximum hit count in the first wave is $h_{\max} = 2$. The trust stock of a maximally hit edge after the first wave is $I_0 \cdot (1 - \rho)^2$. For this edge to survive, we require $I_0 \cdot (1-\rho)^2 \geq \tau$. With $I_0 = 1$, this holds whenever $(1-\rho)^2 \geq \tau$, i.e., $\rho \leq 1 - \sqrt{\tau}$. If no edge fails in the first wave, there is no second wave: $h_e = 0$ for all surviving edges in subsequent rounds, and the cascade terminates with zero secondary failures. $\square$

At $\tau = 0.55$, the floor is $\rho_{\min} = 1 - \sqrt{0.55} \approx 0.2584$.

**Verification.** *Why is there a universal initiation floor?* Because the first wave of a single-node shock delivers at most a double hit to any surviving edge, and $(1-\rho)^2 \geq \tau$ suffices to survive it. Figure 1 confirms this across 12 values of $\tau$ from 0.25 to 0.80: the empirical onset of cascade amplification tracks $\rho_{\min} = 1 - \sqrt{\tau}$ with deviations smaller than the $\rho$-grid resolution.

### 4.2 Interpretation

Proposition 1 establishes a hard lower bound that is independent of network structure: no amount of connectivity, clustering, or hub concentration can produce a cascade if the contagion sensitivity is below the floor. This separates the problem into two regimes. Below $\rho_{\min}$, governance architecture is unconstrained by cascade risk. Above $\rho_{\min}$, the network's topology and connectivity determine whether cascades reach materiality.

The parameter $\rho$ admits a natural institutional interpretation. It measures how much a neighboring trust failure degrades an agent's trust in its other relationships — the degree to which trust is locally correlated. In organizations with strong compartmentalization, $\rho$ is low: a failure in one team does not spill over to others. In organizations with dense mutual dependence, $\rho$ is high: a failure in one relationship makes agents question their other relationships.

---

## 5. The Phase Boundary

Proposition 1 is an initiation bound, not a materiality bound: material cascade requires both $\rho > \rho_{\min}$ and sufficient effective connectivity $B$ for secondary failures to propagate beyond the immediate neighborhood of the shock.

### 5.1 Benchmark Result 1: Convergence to the Floor

For a materiality threshold $q > 0$, define the *critical contagion sensitivity* as the minimum $\rho$ at which expected net secondary cascade exposure exceeds $q$:

$$\rho^*_q(B; \tau) = \inf \left\{ \rho : \mathbb{E}\left[ |\mathcal{C}| / \binom{n}{2} \right] \geq q \right\}$$

**Result.** In the ER benchmark with $\tau = 0.55$ and $n = 250$:

(a) $\rho^*_q(B) \geq \rho_{\min}$ for all $B$ and $q$, consistent with Proposition 1.

(b) $\rho^*_q(B) \to \rho_{\min}$ as $B$ increases. At $B \geq 4$, the boundary sits at the analytic floor to within $\pm 0.0002$ (95% bootstrap CI).

(c) The boundary gap $\Delta\rho = \rho^*_q(B) - \rho_{\min}$ is a decreasing function of $B$ that approaches zero. At low $B$ ($\approx 3$), $\Delta\rho \approx 0.02$ with wide confidence intervals. At high $B$ ($\geq 5$), $\Delta\rho < 0.001$.

**Interpretation.** In dense networks, the system transitions from zero secondary cascade to material cascade in an arbitrarily narrow $\rho$ band. The transition sharpens with connectivity: at high $B$, there is essentially no buffer between the analytic floor and the onset of systemic disruption. This is the formal sense in which the governance transition is "sharp" — not discontinuous, but concentrated in a vanishingly narrow parameter range.

*Why is the transition sharp?* Because the boundary gap $\Delta\rho$ shrinks to zero as $B$ increases, concentrating the onset of material cascading into a vanishingly narrow $\rho$ band. Figure 2 shows $\rho^*_q(B)$ for three materiality thresholds ($q = 1\%, 3\%, 5\%$) with 95% bootstrap confidence intervals, all converging to the Proposition 1 floor. At $B \geq 5$, the CI width is less than $\pm 0.001$: the system is either cascade-immune or cascade-exposed, with essentially no intermediate regime.

### 5.2 The Phase Space

The model's behavior is fully characterized by position in $(\rho, B)$ space relative to two boundaries:

1. **The initiation floor** $\rho_{\min} = 1 - \sqrt{\tau}$: a horizontal line below which no cascade occurs.
2. **The materiality boundary** $\rho^*_q(B)$: a curve above the floor, converging to it as $B$ increases.

The region below the floor is cascade-immune. The region between the floor and the materiality boundary contains possible but sub-material cascades. The region above the materiality boundary is cascade-exposed: trust-based governance faces systemic risk from single-node failures.

*What does the full phase space look like?* Figure 3 maps cascade amplification and exposure across the $(\langle k \rangle, \rho)$ plane for the ER benchmark, with the analytic floor marked. The transition from white (no cascade) to dark (systemic cascade) is visually sharp and aligned with the $\rho_{\min}$ line, confirming that the two analytical boundaries — initiation floor and materiality boundary — organize the entire parameter space.

---

## 6. Topology Governs Severity

### 6.1 Benchmark Result 2: Onset vs. Severity Decomposition

The cascade initiation floor $\rho_{\min}$ is topology-independent (Proposition 1). The question is whether topology affects the cascade *above* the floor.

To test this cleanly, we compare Erdős–Rényi and modular (stochastic block model) networks at *matched effective connectivity* $B$. This controls for the degree-distribution effect and isolates the contribution of community structure.

**Result.** At matched $B$ and $\rho$:

(a) The critical contagion sensitivity $\rho^*_q$ is approximately invariant to topology. ER and modular networks cross the materiality threshold at nearly the same $\rho$, controlling for $B$.

(b) The cascade *severity* above the threshold is strongly topology-dependent. Modular networks exhibit 2–12× higher cascade exposure than ER networks at the same $(B, \rho)$.

**Interpretation.** This yields a clean decomposition:

- **Effective connectivity $B$ governs onset**: whether enough double-hit paths exist for cascades to initiate and propagate.
- **Topology $\mathcal{G}$ governs severity conditional on onset**: community structure, clustering, and local overlap determine how much damage a cascade produces once it starts.
- **The analytic floor $\rho_{\min}$ is universal**: it depends only on $\tau$ and the update rule, not on any network property.

### 6.2 Hub-Dominated Networks

Barabási–Albert (scale-free) networks reach a given $B$ at far lower mean degree $\langle k \rangle$ than ER networks, because their degree variance $\langle k^2 \rangle$ is much higher. This means hub-dominated networks become cascade-exposed earlier in $\langle k \rangle$ space — not because the phase boundary shifts, but because their topology generates high effective connectivity at low average connectivity.

This prediction is institutionally important: financial networks, supply chains with keystone firms, and social platforms with influencer hubs should formalize governance earlier than distributed networks of comparable average connectivity. The driver is not the density of relationships but the concentration of intermediation through high-degree nodes.

*What does higher $B$ actually do to realized cascade severity?* Figure 4 shows net secondary cascade profiles at five levels of effective connectivity. Below $\rho_{\min}$, every curve sits at exactly zero — no secondary cascade at any $B$. Above $\rho_{\min}$, the curves separate immediately: at $B \approx 6.7$, net secondary exposure reaches 35–40% of all pairs within the first grid step above the floor; at $B \approx 3.6$, it takes until $\rho \approx 0.28$ to cross 1%. The figure makes visible both the universality of the floor (all curves share the same left boundary) and the B-dependence of severity (vertical separation between curves at any fixed $\rho$).

---

## 7. Discriminating Predictions

### 7.1 Comparative Predictions

The table below states predictions that distinguish the TPB from three incumbent frameworks. Entries marked "—" indicate the framework does not naturally generate a prediction on that dimension.

| Prediction | TPB | TCE (Williamson) | Embeddedness (Granovetter) | Commons (Ostrom) |
|---|---|---|---|---|
| **Is the governance transition sharp or smooth?** | Sharp: concentrated in a narrow $(B, \rho)$ band that narrows further as $B$ increases | Smooth: continuous cost optimization over asset specificity | Ambiguous: cultural shift, no threshold mechanism | Conditional on rule compliance; no formal threshold |
| **Does topology matter independently of bilateral trust quality?** | Yes: high $B$ forces cascade exposure even with high bilateral trust (high $I_{ij}$) | No: governance driven by bilateral asset specificity and bounded rationality | Partially: network position matters, but no formal connectivity threshold | Partially: group size matters, but no connectivity threshold |
| **Do hub-dominated networks formalize earlier than distributed ones at equal average connectivity?** | Yes: hub topology generates high $B$ at low $\langle k \rangle$ | — | — | — |
| **Does topology affect cascade severity at matched connectivity?** | Yes: community structure amplifies cascades 2–12× at matched $B$ | — | — | — |
| **Is contagion sensitivity ($\rho$) a decisive institutional variable?** | Yes: below $\rho_{\min} = 1 - \sqrt{\tau}$, no cascade on any graph; above it, $B$ determines onset | — | — | — |

The rows marked "—" across competing frameworks identify the TPB's most distinctive predictions.

### 7.2 Falsification Conditions

The theory is disconfirmed if, in settings where the modeled trust-dependence network crosses the benchmark connectivity criterion:

- governance costs and architecture shift smoothly with no evidence of threshold behavior or topology-specific effects,
- networks with high $B$ but high bilateral trust quality sustain trust-based governance indefinitely (topology does not matter independently of trust quality),
- hub-dominated and distributed networks of equal $B$ exhibit identical cascade severity (topology does not affect damage conditional on onset), or
- organizations with low compartmentalization do not experience more cascade-like trust failures than highly compartmentalized organizations at the same connectivity.

---

## 8. Discussion

### 8.1 Institutional Interpretation of the Phase Space

The model's two control parameters — effective connectivity $B$ and contagion sensitivity $\rho$ — admit natural institutional readings.

$B$ reflects the density of trust intermediation: how many agents' trust assessments depend on common intermediaries. It increases with organizational growth, market integration, and communication technology. In the medieval context, $B$ rose as trade routes connected previously isolated merchant communities. In the modern context, it rises as financial institutions become more interconnected or as digital platforms reduce the cost of forming new interaction edges.

$\rho$ reflects the local correlation of trust: how much a failure in one relationship contaminates adjacent relationships. It increases with organizational cultures of mutual dependence, decreases with compartmentalization, and is high in systems where reputation is the primary coordination mechanism (a reputational failure propagates to all relationships). It is also high in agent systems with volatile counterpart sets, where each agent's model of its partners is shallow and easily revised.

The governance phase boundary then says: trust-based governance is viable as long as the system remains below the $\rho^*(B)$ curve. Crossing it — through growth in intermediation density, reduction in compartmentalization, or both — triggers a cascade regime in which verification becomes the dominant architecture.

### 8.2 Limitations

The model makes several simplifying assumptions that should be relaxed in future work. The trust intermediation graph $G_I$ is treated as static; in reality, agents form and sever edges endogenously. The contagion sensitivity $\rho$ is uniform; real organizations have heterogeneous compartmentalization. The shock is a single-node failure; correlated multi-node shocks would produce different phase boundaries. The coordination threshold $\tau$ is uniform; real coordination tasks vary in their trust requirements.

The benchmark uses Erdős–Rényi, Barabási–Albert, and modular random graphs. These are standard but stylized. Empirical calibration to real organizational or financial networks is needed to test whether the predicted phase boundary corresponds to observed governance transitions.

The model does not yet include hysteresis — the prediction that returning from verification-based to trust-based governance requires crossing a *lower* threshold than the forward transition, because verification infrastructure degrades the trust-information stock. This is a natural extension with clear institutional implications (deregulation is harder than regulation) but requires additional state variables.

### 8.3 What This Theory Is About

Underneath the formal apparatus, the paper makes one claim: governance form is determined by the topology of correlated trust dependence, and changes abruptly when that topology crosses a critical threshold.

Most governance theories focus on incentives, bounded rationality, social norms, or monitoring costs. The distinctive move here is that local trust can remain high — every bilateral relationship can be strong — but once the correlation structure of trust failure percolates, trust governance ceases to scale. The failure is not in the parts but in the wiring.

---

## 9. Related Work and References

The TPB engages four literatures. Transaction cost economics (Williamson 1975, 1985) locates governance choice in bilateral asset specificity and bounded rationality but does not predict a threshold or explain the abruptness of governance transitions; the TPB supplies both via the phase boundary in $(B, \rho)$ space. Embeddedness theory (Granovetter 1985) establishes that economic action is embedded in social relations but does not specify when embedded governance fails; the TPB identifies the failure condition as sufficient connectivity and contagion sensitivity for cascading trust failures. Commons governance research (Ostrom 1990) identifies institutional conditions for successful self-governance that map onto the TPB's low-$B$, low-$\rho$ regime. Cascade models on random networks (Watts 2002) provide the closest formal antecedent; the TPB extends binary-state contagion to trust-information degradation with a coordination threshold and derives an exact analytic initiation floor absent from that framework. Trust production theory (Zucker 1986) distinguishes process-based and institutional trust; the TPB provides a topological condition for the transition between the two. The construction–destruction asymmetry of trust is well-documented empirically (Slovic 1993; Kramer 1999); the TPB formalizes it as a feature of Bayesian learning under asymmetric signal informativeness.

The mathematical foundations draw on percolation theory (Broadbent and Hammersley 1957; Stauffer and Aharony 1994) and the theory of random graphs with given degree sequences (Molloy and Reed 1995).

The author has explored adjacent information-theoretic constraints on coordination and organizational overhead in separate work. The relationship between those results and the present theory is a direction for future research.

### References

Broadbent, S.R. and Hammersley, J.M. (1957). Percolation processes: I. Crystals and mazes. *Mathematical Proceedings of the Cambridge Philosophical Society*, 53(3), 629–641.
Granovetter, M. (1985). Economic action and social structure: The problem of embeddedness. *American Journal of Sociology*, 91(3), 481–510.
Kramer, R.M. (1999). Trust and distrust in organizations: Emerging perspectives, enduring questions. *Annual Review of Psychology*, 50, 569–598.
Molloy, M. and Reed, B. (1995). A critical point for random graphs with a given degree sequence. *Random Structures & Algorithms*, 6(2–3), 161–179.
Ostrom, E. (1990). *Governing the Commons.* Cambridge University Press.
Slovic, P. (1993). Perceived risk, trust, and democracy. *Risk Analysis*, 13(6), 675–682.
Stauffer, D. and Aharony, A. (1994). *Introduction to Percolation Theory.* CRC Press.
Watts, D.J. (2002). A simple model of global cascades on random networks. *Proceedings of the National Academy of Sciences*, 99(9), 5766–5771.
Williamson, O.E. (1975). *Markets and Hierarchies.* Free Press.
Williamson, O.E. (1985). *The Economic Institutions of Capitalism.* Free Press.
Zucker, L.G. (1986). Production of trust: Institutional sources of economic structure, 1840–1920. *Research in Organizational Behavior*, 8, 53–111.

---

## Appendix A: Computational Methods

### A.1 Benchmark Model

All simulations use $n = 250$ agents, trust stock $I_0 = 1$, coordination threshold $\tau = 0.55$, and contagion sensitivity $\rho$ swept across the range $[0.10, 0.50]$. Networks are generated from three families: Erdős–Rényi $G(n, p)$, Barabási–Albert preferential attachment with parameter $m = \text{round}(\langle k \rangle / 2)$, and stochastic block model with 5 communities and 85/15 intra/inter-community edge ratio.

For each parameter combination, results are averaged over 15 independent graph realizations with 10–12 independent single-node shocks per graph. Cascade size is measured as net secondary disruption: total pairs disconnected minus pairs that would be disconnected by node removal alone (without cascade propagation).

### A.2 Bootstrap Confidence Intervals

Critical contagion sensitivity $\rho^*_q(B)$ is estimated by linear interpolation across the $\rho$ grid at the first crossing of materiality threshold $q$, clamped below at $\rho_{\min} = 1 - \sqrt{\tau}$ per Proposition 1. 95% confidence intervals are computed from 150 bootstrap resamples of the per-graph, per-shock cascade outcomes.

### A.3 B-Matched Topology Comparison

To compare topologies at matched effective connectivity, the mapping from mean degree $\langle k \rangle$ to Molloy–Reed branching factor $B$ is calibrated separately for each graph family using 20 independent realizations per $\langle k \rangle$ value. Target $B$ values are then achieved by interpolation, and cascade sweeps are run at the calibrated $\langle k \rangle$.

---

## Figure Captions

**Figure 1. Why is there a universal initiation floor?** Analytic cascade initiation floor $\rho_{\min} = 1 - \sqrt{\tau}$ (solid line) and empirical onset of cascade amplification (points), across 12 values of $\tau$. The floor holds because a single-node shock delivers at most a double hit to any surviving edge. ER benchmark, $n = 250$, $\langle k \rangle = 5.5$.

**Figure 2. Why is the transition sharp?** Critical contagion sensitivity $\rho^*_q(B)$ for net secondary cascade exceeding 1% (blue) and cascade amplification exceeding 1.5× (purple), with 95% bootstrap CI. The boundary converges to the Proposition 1 floor (dashed green) as $B$ increases, concentrating the transition into a vanishingly narrow $\rho$ band. Old method (total cascade > 3%, unclamped) shown for comparison (gray). ER benchmark, $n = 250$, $\tau = 0.55$.

**Figure 3. What does the phase space look like?** Left: cascade amplification in $(\langle k \rangle, \rho)$ space. Right: cascade exposure in the same space. The analytic floor $\rho_{\min} = 1 - \sqrt{\tau}$ (dashed line) separates the cascade-immune region from the cascade-exposed region. ER benchmark, $n = 250$, $\tau = 0.55$.

**Figure 4. What does higher $B$ do to realized cascade severity?** Net secondary cascade exposure as a function of $\rho$ for five levels of effective connectivity. All curves share an identical left boundary at $\rho_{\min}$ (zero net cascade below the floor). Above the floor, severity scales with $B$: at $B \approx 6.7$, cascade exposure reaches 35–40% immediately; at $B \approx 3.6$, it barely exceeds 1%. ER benchmark, $n = 250$, $\tau = 0.55$.

---

*Word count: approximately 3,800 (main text, excluding appendix and references).*
*Target venue: Journal of Economic Behavior & Organization or Journal of Institutional Economics.*
*Companion materials: simulation code and all figures available at [github.com/AMBRA7592/trust-percolation-bound](https://github.com/AMBRA7592/trust-percolation-bound).*
