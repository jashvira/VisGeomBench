# Abstract

Visual Geometry Bench measures LLM spatial cognition through questions that compel humans to visualise in order to solve, aka test the "Geometric Intuition".
We probe how models reconstruct global structure from fragments, reason across spatial hierarchies, and infer topological relationships, all without visual input.

## Tasks

### Convex Hull Ordering
Given scattered 2D points, identify which lie on the convex boundary and order them counter-clockwise. Points cluster near edges to stress global shape recovery amidst local clutter. Models must distinguish boundary from interior and maintain rotational consistency.

<details open>
<summary style="cursor:pointer; font-weight:600;">Sample Question 1</summary>

<div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/convex_hull_curated/questions_gt/question_001.png" alt="Convex hull question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption><strong>Question</strong></figcaption>
  </figure>
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/convex_hull_curated/model_answers/question_001.png" alt="Gemini answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption>Gemini 2.5 Pro</figcaption>
  </figure>
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/convex_hull_curated/model_answers/question_001.png" alt="GPT-5 answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption>GPT‑5 (2025‑08‑07)</figcaption>
  </figure>
</div>

</details>

<details>
<summary>Sample Question 2</summary>

<div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/convex_hull_curated/questions_gt/question_002.png" alt="Question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption style="font-size:0.9em;color:#666;">Question</figcaption>
  </figure>
  
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/convex_hull_curated/model_answers/question_002.png" alt="Gemini 2.5 Pro Answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption style="font-size:0.9em;color:#666;">Gemini 2.5 Pro Answer</figcaption>
  </figure>
  
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/convex_hull_curated/model_answers/question_002.png" alt="GPT-5 Answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption style="font-size:0.9em;color:#666;">GPT-5 Answer</figcaption>
  </figure>
</div>

</details>

### Delaunay Triangulation
Partition a point set into triangles satisfying the empty-circle property: no point lies inside any triangle's circumcircle. The constraint is global—each triangle depends on all others—testing whether models grasp metric invariances and maintain combinatorial precision across the entire structure.

<details open>
<summary style="cursor:pointer; font-weight:600;">Sample Question 1</summary>

<div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/delaunay_dataset/questions_gt/question_001.png" alt="Delaunay question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption><strong>Question</strong></figcaption>
  </figure>
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/delaunay_dataset/model_answers/question_001.png" alt="Gemini answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption>Gemini 2.5 Pro</figcaption>
  </figure>
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/delaunay_dataset/model_answers/question_001.png" alt="GPT-5 answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption>GPT‑5 (2025‑08‑07)</figcaption>
  </figure>
</div>

</details>

<details>
<summary>Sample Question 2</summary>

<div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/delaunay_dataset/questions_gt/question_002.png" alt="Question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption style="font-size:0.9em;color:#666;">Question</figcaption>
  </figure>
  
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/delaunay_dataset/model_answers/question_002.png" alt="Gemini 2.5 Pro Answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption style="font-size:0.9em;color:#666;">Gemini 2.5 Pro Answer</figcaption>
  </figure>
  
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/delaunay_dataset/model_answers/question_002.png" alt="GPT-5 Answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption style="font-size:0.9em;color:#666;">GPT-5 Answer</figcaption>
  </figure>
</div>

</details>

### Topology Enumeration
Which corner labellings of a square force distinct regions to meet inside? Continuous boundaries may curve arbitrarily; only corner labels are observed. Models must enumerate all configurations that guarantee junctions, canonicalised to remove label symmetries.

<details open>
<summary style="cursor:pointer; font-weight:600;">Sample Question 1</summary>

<div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/topology_enumeration_curated/questions_gt/question_001.png" alt="Topology enumeration question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption><strong>Question</strong></figcaption>
  </figure>
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <div style="width:100%;border:1px dashed #d1d5db;margin:0 0 8px;padding:28px 16px;font-style:italic;color:#6b7280;text-align:center;">Pending render</div>
    <figcaption>Gemini 2.5 Pro</figcaption>
  </figure>
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <div style="width:100%;border:1px dashed #d1d5db;margin:0 0 8px;padding:28px 16px;font-style:italic;color:#6b7280;text-align:center;">Pending render</div>
    <figcaption>GPT‑5 (2025‑08‑07)</figcaption>
  </figure>
</div>

</details>

<details>
<summary>Sample Question 2</summary>

<div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/topology_enumeration_curated/questions_gt/question_002.png" alt="Question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption style="font-size:0.9em;color:#666;">Question</figcaption>
  </figure>
  
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/topology_enumeration_curated/model_answers/question_002.png" alt="Gemini 2.5 Pro Answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption style="font-size:0.9em;color:#666;">Gemini 2.5 Pro Answer</figcaption>
  </figure>
  
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/topology_enumeration_curated/model_answers/question_002.png" alt="GPT-5 Answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption style="font-size:0.9em;color:#666;">GPT-5 Answer</figcaption>
  </figure>
</div>

</details>

### Topology Edge Tasks
**Enumerate edges**: Given corner labels, which boundary edges must connect through the interior?  

Models infer connectivity from minimal boundary information, handling cases where topology alone cannot determine outcomes.

<details open>
<summary style="cursor:pointer; font-weight:600;">Sample Question 1</summary>

<div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/topology_edge_enumerate_curated/questions_gt/question_001.png" alt="Topology edge question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption><strong>Question</strong></figcaption>
  </figure>
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/topology_edge_enumerate_curated/model_answers/question_001.png" alt="Gemini answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption>Gemini 2.5 Pro</figcaption>
  </figure>
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/topology_edge_enumerate_curated/model_answers/question_001.png" alt="GPT-5 answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption>GPT‑5 (2025‑08‑07)</figcaption>
  </figure>
</div>

</details>

<details>
<summary>Sample Question 2</summary>

<div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/topology_edge_enumerate_curated/questions_gt/question_002.png" alt="Question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption style="font-size:0.9em;color:#666;">Question</figcaption>
  </figure>
  
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/topology_edge_enumerate_curated/model_answers/question_002.png" alt="Gemini 2.5 Pro Answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption style="font-size:0.9em;color:#666;">Gemini 2.5 Pro Answer</figcaption>
  </figure>
  
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/topology_edge_enumerate_curated/model_answers/question_002.png" alt="GPT-5 Answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption style="font-size:0.9em;color:#666;">GPT-5 Answer</figcaption>
  </figure>
</div>

</details>

### Half Subdivision Neighbours
A square or cube is recursively split along axis-aligned planes. Given a target leaf cell, list all adjacent neighbours. The hierarchy is textual; models must track nested containment and compute exact face-sharing in discretised space.

<details open>
<summary style="cursor:pointer; font-weight:600;">Sample Question 1</summary>

<div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/half_subdivision/questions_gt/question_002.png" alt="Half subdivision question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption><strong>Question</strong></figcaption>
  </figure>
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <div style="width:100%;border:1px dashed #d1d5db;margin:0 0 8px;padding:28px 16px;font-style:italic;color:#6b7280;text-align:center;">Pending render</div>
    <figcaption>Gemini 2.5 Pro</figcaption>
  </figure>
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/half_subdivision/model_answers/question_002.png" alt="GPT-5 answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption>GPT‑5 (2025‑08‑07)</figcaption>
  </figure>
</div>

</details>

<details>
<summary>Question 2 visuals</summary>

<div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/half_subdivision/questions_gt/question_003.png" alt="Question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption style="font-size:0.9em;color:#666;">Question</figcaption>
  </figure>
  
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/half_subdivision/model_answers/question_003.png" alt="Gemini 2.5 Pro Answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption style="font-size:0.9em;color:#666;">Gemini 2.5 Pro Answer</figcaption>
  </figure>
  
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/half_subdivision/model_answers/question_003.png" alt="GPT-5 Answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption style="font-size:0.9em;color:#666;">GPT-5 Answer</figcaption>
  </figure>
</div>

</details>

### Shikaku Rectangles
Partition a grid into rectangles such that each contains exactly one number equal to its area. Constraints are local (area match) and global (full coverage, no gaps). Models must satisfy both simultaneously through spatial planning.

<details open>
<summary style="cursor:pointer; font-weight:600;">Sample Question 1</summary>

<div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/shikaku_curated/questions_gt/question_003.png" alt="Shikaku question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption><strong>Question</strong></figcaption>
  </figure>
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/shikaku_curated/model_answers/question_003.png" alt="Shikaku answer · Gemini" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption>Gemini 2.5 Pro</figcaption>
  </figure>
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/shikaku_curated/model_answers/question_003.png" alt="Shikaku answer · GPT-5" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption>GPT‑5 (2025‑08‑07)</figcaption>
  </figure>
</div>

</details>

<details>
<summary>Sample Question 2</summary>

<div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/shikaku_curated/questions_gt/question_004.png" alt="Question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption style="font-size:0.9em;color:#666;">Question</figcaption>
  </figure>
  
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/shikaku_curated/model_answers/question_004.png" alt="Gemini 2.5 Pro Answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption style="font-size:0.9em;color:#666;">Gemini 2.5 Pro Answer</figcaption>
  </figure>
  
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/shikaku_curated/model_answers/question_004.png" alt="GPT-5 Answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption style="font-size:0.9em;color:#666;">GPT-5 Answer</figcaption>
  </figure>
</div>

</details>

### Two Segments
Place two straight segments inside a square to create a specified mix of triangles, quadrilaterals, pentagons, and hexagons. Endpoints must lie on the boundary. Models must construct valid geometric solutions to combinatorial constraints, balancing feasibility with target counts.

<details open>
<summary style="cursor:pointer; font-weight:600;">Sample Question 1</summary>

<div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/two_segments_curated/questions_gt/question_002.png" alt="Two segments question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption><strong>Question</strong></figcaption>
  </figure>
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/two_segments_curated/model_answers/question_002.png" alt="Two segments answer · Gemini" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption>Gemini 2.5 Pro</figcaption>
  </figure>
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/two_segments_curated/model_answers/question_002.png" alt="Two segments answer · GPT-5" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption>GPT‑5 (2025‑08‑07)</figcaption>
  </figure>
</div>

</details>

<details>
<summary>Question 2 visuals</summary>

<div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/two_segments_curated/questions_gt/question_003.png" alt="Question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption style="font-size:0.9em;color:#666;">Question</figcaption>
  </figure>
  
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/two_segments_curated/model_answers/question_003.png" alt="Gemini 2.5 Pro Answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption style="font-size:0.9em;color:#666;">Gemini 2.5 Pro Answer</figcaption>
  </figure>
  
  <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/two_segments_curated/model_answers/question_003.png" alt="GPT-5 Answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption style="font-size:0.9em;color:#666;">GPT-5 Answer</figcaption>
  </figure>
</div>

</details>

---

## Narrative

- Visual and topological reasoning through multiple steps
- Questions which naturally force you to draw and visually solve, even though theoretically it can be solved analytically.
- Gather how these models would exploit and solve tasks which necessarily require humans to visualise and draw.

- Another spin?
    - We are measuring geometric intuition. And then stress testing it.
    

Interesting questions to show:
- change of configurations: breaking of pattern leads to spending more deliberate attention.
    - in corner configurations of N domains meeting in quad.
    - in axis configurations of half subdivision.
- This leads to a few open questions:
    - How is attention spent?
        - Is there an ablation here for different kind of attention spending mechanisms like sparse, ring, etc?
        - Can we teach the model to intentionally spend more attention on certain tasks? 