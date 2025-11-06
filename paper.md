# Abstract

Visual Geometry Bench (VisGeomBench) evaluates how large language models reason about geometric and topological structure from text alone. The suite probes core abilities: recovering global shape and extremal structure; inferring combinatorial triangulations under metric invariances; establishing necessary edge connections and junctions from boundary labels; mapping between hierarchical subdivisions and exact adjacency; satisfying discrete tiling constraints; and constructive partition design with specified region counts. We target invariance to relabelling and order, robustness to clutter and near‑degeneracy, and compositional reasoning across local‑to‑global cues, providing a focused measure of text‑only visual geometry competence.

## Narrative

- Visual and topological reasoning through multiple steps
- Questions which naturally force you to draw and visually solve, even though theorteically it can be solved analytically.
- Gather how these models would exploit and solve tasks which necissarily require humans to visualise and draw.

- Another spin?
    - We are measuring geoemtric intuition. And then stress testing it.
    

Interesting questions to show:
- change of configurations: breaking of pattern leads to spending more deliberate attention.
    - in corner configurations of N domains meeting in quad.
    - in axis configurations of half subdivision.
- This leads to a few open questions:
    - How is attention spent?
        - Is there an ablation here for different kind of attention spending mechanims like sparse, ring, etc?
        - Can we teach the model to intentionally spend more attention on certain tasks? 