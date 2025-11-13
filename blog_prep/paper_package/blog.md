# Abstract

Visual Geometry Bench measures LLM spatial cognition through questions that compel humans to visualise in order to solve, aka test the "Geometric Intuition".
We probe how models reconstruct global structure from fragments, reason across spatial hierarchies, and infer topological relationships, all without visual input.

## Tasks

### Convex Hull Ordering
Given scattered 2D points, identify which lie on the convex boundary and order them counter-clockwise. Points cluster near edges to stress global shape recovery amidst local clutter. Models must distinguish boundary from interior and maintain rotational consistency.

<details open>
<summary style="cursor:pointer; font-weight:600;">Sample Question 1</summary>

<div style="display:flex;flex-direction:column;gap:14px;margin:12px 0;">
  <details open>
    <summary style="cursor:pointer;font-weight:600;">Question &amp; Prompt</summary>
    <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start;margin-top:8px;">
      <figure style="flex:1;min-width:260px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/convex_hull_curated/questions_gt/question_001.png" alt="Convex hull question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption><strong>Question visual/answer</strong></figcaption>
      </figure>
      <pre style="flex:1.5;min-width:320px;max-height:420px;overflow:auto;background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px;padding:12px;font-size:0.9em;line-height:1.35;margin:0;">You are given a set of 2D points (indices correspond to the order shown):
[
[0.9847097172600733, 0.8470018012040504],
[0.781117588817471, 0.605847029570968],
[0.1167072630852084, 0.016809638081511834],
[0.4071132802384164, 0.0],
[0.7579097734349027, 0.21347912685253467],
[0.38041464258657925, 0.6072058285935236],
[0.05064105719138242, 0.9933476139234197],
[0.9983968746929466, 0.8380672354524976],
[0.9829722115579645, 0.058679817789533156],
[0.25045612457660815, 0.1139630728418547]
]

Return the convex hull vertices as a list of integer indices in counterclockwise order.
Start the list at the smallest index among the hull vertices.
Before presenting the final list, begin your response with &lt;thinking&gt;...&lt;/thinking&gt; containing your full chain of thought or reasoning for your answer.
Strict output: a Python list of integers only.</pre>
    </div>
  </details>

  <details>
    <summary style="cursor:pointer;font-weight:600;">Model Answers</summary>
    <div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/convex_hull_curated/model_answers/question_001.png" alt="Gemini answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>Gemini 2.5 Pro</figcaption>
      </figure>
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/convex_hull_curated/model_answers/question_001.png" alt="GPT-5 answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>GPT‑5 (2025‑08‑07)</figcaption>
      </figure>
    </div>
  </details>
</div>

</details>

<details>
<summary>Sample Question 2</summary>

<div style="display:flex;flex-direction:column;gap:14px;margin:12px 0;">
  <details open>
    <summary style="cursor:pointer;font-weight:600;">Question &amp; Prompt</summary>
    <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start;margin-top:8px;">
      <figure style="flex:1;min-width:260px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/convex_hull_curated/questions_gt/question_002.png" alt="Convex hull question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption><strong>Question visual/answer</strong></figcaption>
      </figure>
      <pre style="flex:1.5;min-width:320px;max-height:420px;overflow:auto;background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px;padding:12px;font-size:0.9em;line-height:1.35;margin:0;">You are given a set of 2D points (indices correspond to the order shown):
[
[0.9999999999999999, 0.3774788746902663],
[0.021796079009168676, 0.005989281617301664],
[0.006827764985493064, 0.9191721236959333],
[0.002304631877298652, 0.9845929653545332],
[0.3458383119130293, 0.7000792819687283],
[0.1833507382289155, 0.35877702838223346],
[0.21347863456508945, 0.008161433224732357],
[0.40619682604132323, 0.029142835401811756],
[0.8574566753273573, 0.003098650519230135],
[0.011607735622632787, 0.5265324651175397],
[0.18484324985637923, 0.010201526441550793],
[0.004202119773775619, 0.5362014665043575],
[0.6196301643145802, 0.0],
[0.9968482272948653, 0.9818375671902593],
[0.9955560527751108, 0.5643374759068586],
[0.9177312255672199, 0.7904974657941997],
[0.0025424226208299212, 0.45151251523954367],
[0.6272982388018099, 0.9687213253865968],
[0.5073134077666972, 0.5082256885037216],
[0.9985995813620885, 0.33121062053676203],
[0.3928989188053327, 0.2696761513572739],
[0.6345745906331365, 0.005397202262415348],
[0.2754549447741456, 0.9226509984586403],
[0.0, 0.6200508682875664],
[0.6939330806573643, 0.6414582208782306],
[0.9954011583883514, 0.05471632099231117],
[0.0, 0.6481096245403379],
[0.6842570338230184, 0.2545270438959884],
[0.20936538435475496, 0.9912942586959974],
[0.0, 0.6354294045910812],
[0.14400740719553645, 0.7425018205229266],
[0.007161829502783213, 0.35463886199373834],
[0.7872051535291491, 0.008785490976656034],
[0.9800729272659756, 0.47394675290249716],
[0.9483676724534333, 0.13829764991943236],
[0.23573870787159004, 0.9881289901247743]
]

Return the convex hull vertices as a list of integer indices in counterclockwise order.
Start the list at the smallest index among the hull vertices.
Before presenting the final list, begin your response with &lt;thinking&gt;...&lt;/thinking&gt; containing your full chain of thought or reasoning for your answer.
Strict output: a Python list of integers only.</pre>
    </div>
  </details>

  <details>
    <summary style="cursor:pointer;font-weight:600;">Model Answers</summary>
    <div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/convex_hull_curated/model_answers/question_002.png" alt="Gemini 2.5 Pro answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>Gemini 2.5 Pro</figcaption>
      </figure>
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/convex_hull_curated/model_answers/question_002.png" alt="GPT-5 answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>GPT‑5 (2025‑08‑07)</figcaption>
      </figure>
    </div>
  </details>
</div>

</details>

### Delaunay Triangulation
Partition a point set into triangles satisfying the empty-circle property: no point lies inside any triangle's circumcircle. The constraint is global—each triangle depends on all others—testing whether models grasp metric invariances and maintain combinatorial precision across the entire structure.

<details open>
<summary style="cursor:pointer; font-weight:600;">Sample Question 1</summary>

<div style="display:flex;flex-direction:column;gap:14px;margin:12px 0;">
  <details open>
    <summary style="cursor:pointer;font-weight:600;">Question &amp; Prompt</summary>
    <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start;margin-top:8px;">
      <figure style="flex:1;min-width:260px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/delaunay_dataset/questions_gt/question_001.png" alt="Delaunay triangulation question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption><strong>Question visual/answer</strong></figcaption>
      </figure>
      <pre style="flex:1.5;min-width:320px;max-height:420px;overflow:auto;background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px;padding:12px;font-size:0.9em;line-height:1.35;margin:0;">You are given a set of 2D points in general position (indices correspond to the order shown):
[
  [0.956, 0.208],
  [0.828, 0.149],
  [0.513, 0.136],
  [0.689, 0.842],
  [0.426, 0.957],
  [0.825, 0.338]
]

Return the Delaunay triangulation as a list of triangles.
Each triangle is a list of three point indices (sorted in ascending order).
Before presenting the final list, begin your response with &lt;thinking&gt;...&lt;/thinking&gt; containing your full chain of thought or reasoning for your answer.
Strict output: a Python list of lists of integers only.</pre>
    </div>
  </details>

  <details>
    <summary style="cursor:pointer;font-weight:600;">Model Answers</summary>
    <div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/delaunay_dataset/model_answers/question_001.png" alt="Gemini answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>Gemini 2.5 Pro</figcaption>
      </figure>
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/delaunay_dataset/model_answers/question_001.png" alt="GPT-5 answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>GPT‑5 (2025‑08‑07)</figcaption>
      </figure>
    </div>
  </details>
</div>

</details>

<details>
<summary>Sample Question 2</summary>

<div style="display:flex;flex-direction:column;gap:14px;margin:12px 0;">
  <details open>
    <summary style="cursor:pointer;font-weight:600;">Question &amp; Prompt</summary>
    <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start;margin-top:8px;">
      <figure style="flex:1;min-width:260px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/delaunay_dataset/questions_gt/question_004.png" alt="Delaunay triangulation question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption><strong>Question visual/answer</strong></figcaption>
      </figure>
      <pre style="flex:1.5;min-width:320px;max-height:420px;overflow:auto;background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px;padding:12px;font-size:0.9em;line-height:1.35;margin:0;">You are given a set of 2D points in general position (indices correspond to the order shown):
[
  [0.455, 0.263],
  [0.903, 0.671],
  [0.318, 0.878],
  [0.3, 0.2],
  [0.101, 0.649],
  [0.299, 0.918],
  [0.288, 0.22],
  [0.485, 0.548],
  [0.042, 0.058],
  [0.339, 0.635],
  [0.87, 0.842],
  [0.305, 0.399],
  [0.996, 0.435],
  [0.348, 0.315],
  [0.267, 0.662]
]

Return the Delaunay triangulation as a list of triangles.
Each triangle is a list of three point indices (sorted in ascending order).
Before presenting the final list, begin your response with &lt;thinking&gt;...&lt;/thinking&gt; containing your full chain of thought or reasoning for your answer.
Strict output: a Python list of lists of integers only.</pre>
    </div>
  </details>

  <details>
    <summary style="cursor:pointer;font-weight:600;">Model Answers</summary>
    <div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/delaunay_dataset/model_answers/question_004.png" alt="Gemini 2.5 Pro answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>Gemini 2.5 Pro</figcaption>
      </figure>
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/delaunay_dataset/model_answers/question_004.png" alt="GPT-5 answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>GPT‑5 (2025‑08‑07)</figcaption>
      </figure>
    </div>
  </details>
</div>

</details>

### Topology Enumeration
Which corner labellings of a square force distinct regions to meet inside? Continuous boundaries may curve arbitrarily; only corner labels are observed. Models must enumerate all configurations that guarantee junctions, canonicalised to remove label symmetries.

<details open>
<summary style="cursor:pointer; font-weight:600;">Sample Question 1</summary>

<div style="display:flex;flex-direction:column;gap:14px;margin:12px 0;">
  <details open>
    <summary style="cursor:pointer;font-weight:600;">Question &amp; Prompt</summary>
    <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start;margin-top:8px;">
      <figure style="flex:1;min-width:260px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/topology_enumeration_curated/questions_gt/question_001.png" alt="Topology enumeration question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption><strong>Question visual/answer</strong></figcaption>
      </figure>
      <pre style="flex:1.5;min-width:320px;max-height:420px;overflow:auto;background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px;padding:12px;font-size:0.9em;line-height:1.35;margin:0;">You are given a unit square with corners ordered (bottom-left, bottom-right, top-right, top-left). Each corner is labeled from {0, 1, 2...}. Boundaries inside may be any continuous curves; only corner labels are observed.

Assume exactly 2 distinct classes occur anywhere in or on the square.

List all corner-label configurations (4-tuples, in the order above) that are sufficient to guarantee that 2 distinct classes meet somewhere inside the square. Canonicalisation: relabel by first occurrence (scan left-to-right; first new label -&gt; 0, next -&gt; 1, ...). Treat any label renamings as identical; list each equivalence class once.

Strict output: a Python-style list of 4-tuples only.</pre>
    </div>
  </details>

  <details>
    <summary style="cursor:pointer;font-weight:600;">Model Answers</summary>
    <div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/topology_enumeration_curated/model_answers/question_001.png" alt="Gemini answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>Gemini 2.5 Pro</figcaption>
      </figure>
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/topology_enumeration_curated/model_answers/question_001.png" alt="GPT-5 answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>GPT‑5 (2025‑08‑07)</figcaption>
      </figure>
    </div>
  </details>
</div>

</details>

<details>
<summary>Sample Question 2</summary>

<div style="display:flex;flex-direction:column;gap:14px;margin:12px 0;">
  <details open>
    <summary style="cursor:pointer;font-weight:600;">Question &amp; Prompt</summary>
    <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start;margin-top:8px;">
      <figure style="flex:1;min-width:260px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/topology_enumeration_curated/questions_gt/question_002.png" alt="Topology enumeration question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption><strong>Question visual/answer</strong></figcaption>
      </figure>
      <pre style="flex:1.5;min-width:320px;max-height:420px;overflow:auto;background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px;padding:12px;font-size:0.9em;line-height:1.35;margin:0;">You are given a unit square with corners ordered (bottom-left, top-right, bottom-right, top-left). Each corner is labeled from {0, 1, 2...}. Boundaries inside may be any continuous curves; only corner labels are observed.

Assume exactly 2 distinct classes occur anywhere in or on the square.

List all corner-label configurations (4-tuples, in the order above) that are sufficient to guarantee that 2 distinct classes meet somewhere inside the square. Canonicalisation: relabel by first occurrence (scan left-to-right; first new label -&gt; 0, next -&gt; 1, ...). Treat any label renamings as identical; list each equivalence class once.

Strict output: a Python-style list of 4-tuples only.</pre>
    </div>
  </details>

  <details>
    <summary style="cursor:pointer;font-weight:600;">Model Answers</summary>
    <div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/topology_enumeration_curated/model_answers/question_002.png" alt="Gemini 2.5 Pro answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>Gemini 2.5 Pro</figcaption>
      </figure>
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/topology_enumeration_curated/model_answers/question_002.png" alt="GPT-5 answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>GPT‑5 (2025‑08‑07)</figcaption>
      </figure>
    </div>
  </details>
</div>

</details>

### Topology Edge Tasks
Given corner labels, which boundary edges must connect through the interior?  
Models infer connectivity from minimal boundary information, handling cases where topology alone cannot determine outcomes.

<details open>
<summary style="cursor:pointer; font-weight:600;">Sample Question 1</summary>

<div style="display:flex;flex-direction:column;gap:14px;margin:12px 0;">
  <details open>
    <summary style="cursor:pointer;font-weight:600;">Question &amp; Prompt</summary>
    <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start;margin-top:8px;">
      <figure style="flex:1;min-width:260px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/topology_edge_enumerate_curated/questions_gt/question_001.png" alt="Topology edge question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption><strong>Question visual/answer</strong></figcaption>
      </figure>
      <pre style="flex:1.5;min-width:320px;max-height:420px;overflow:auto;background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px;padding:12px;font-size:0.9em;line-height:1.35;margin:0;">Squares (each tuple lists the four corner labels; integers denote distinct classes):
(1, 1, 1, 1)
(1, 1, 1, 2)
(1, 1, 2, 1)
(1, 1, 2, 2)

You are given unit squares with corners labelled in ('bottom-left', 'bottom-right', 'top-right', 'top-left') order.
Edges are indexed: bottom=0, right=1, top=2, left=3.

For each square above (in the same order), list which edges are guaranteed to connect.
Return a list where each element is a list of sorted [i,j] pairs (i &lt; j).
If no edges are deterministically guaranteed (including ambiguous cases), return [] for that square.</pre>
    </div>
  </details>

  <details>
    <summary style="cursor:pointer;font-weight:600;">Model Answers</summary>
    <div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/topology_edge_enumerate_curated/model_answers/question_001.png" alt="Gemini answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>Gemini 2.5 Pro</figcaption>
      </figure>
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/topology_edge_enumerate_curated/model_answers/question_001.png" alt="GPT-5 answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>GPT‑5 (2025‑08‑07)</figcaption>
      </figure>
    </div>
  </details>
</div>

</details>

<details>
<summary>Sample Question 2</summary>

<div style="display:flex;flex-direction:column;gap:14px;margin:12px 0;">
  <details open>
    <summary style="cursor:pointer;font-weight:600;">Question &amp; Prompt</summary>
    <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start;margin-top:8px;">
      <figure style="flex:1;min-width:260px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/topology_edge_enumerate_curated/questions_gt/question_002.png" alt="Topology edge question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption><strong>Question visual/answer</strong></figcaption>
      </figure>
      <pre style="flex:1.5;min-width:320px;max-height:420px;overflow:auto;background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px;padding:12px;font-size:0.9em;line-height:1.35;margin:0;">Squares (each tuple lists the four corner labels; integers denote distinct classes):
(2, 1, 1, 1)
(2, 1, 2, 1)
(2, 1, 3, 1)
(2, 2, 1, 1)
(2, 2, 2, 1)

You are given unit squares with corners labelled in ('bottom-right', 'top-right', 'top-left', 'bottom-left') order.
Edges are indexed: right=0, top=1, left=2, bottom=3.

For each square above (in the same order), list which edges are guaranteed to connect.
Return a list where each element is a list of sorted [i,j] pairs (i &lt; j).
If no edges are deterministically guaranteed (including ambiguous cases), return [] for that square.</pre>
    </div>
  </details>

  <details>
    <summary style="cursor:pointer;font-weight:600;">Model Answers</summary>
    <div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/topology_edge_enumerate_curated/model_answers/question_002.png" alt="Gemini 2.5 Pro answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>Gemini 2.5 Pro</figcaption>
      </figure>
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/topology_edge_enumerate_curated/model_answers/question_002.png" alt="GPT-5 answer" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>GPT‑5 (2025‑08‑07)</figcaption>
      </figure>
    </div>
  </details>
</div>

</details>

### Half Subdivision Neighbours
A square or cube is recursively split along axis-aligned planes. Given a target leaf cell, list all adjacent neighbours. The hierarchy is textual; models must track nested containment and compute exact face-sharing in discretised space.

<details open>
<summary style="cursor:pointer; font-weight:600;">Sample Question 1</summary>

<div style="display:flex;flex-direction:column;gap:14px;margin:12px 0;">
  <details open>
    <summary style="cursor:pointer;font-weight:600;">Question &amp; Prompt</summary>
    <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start;margin-top:8px;">
      <figure style="flex:1;min-width:260px;margin:0;text-align:center;display:flex;flex-direction:column;gap:8px;">
        <img src="./assets/blog_prep/visualisations/half_subdiv_1.gif" alt="3D half-subdivision spatial view" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;">
        <figcaption style="font-size:0.9em;color:#4b5563;">Spatial context (3D)</figcaption>
      </figure>
      <pre style="flex:1;min-width:320px;max-height:420px;overflow:auto;background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px;padding:12px;font-size:0.9em;line-height:1.35;margin:0;">You are given a binary tree describing an axis-aligned half subdivision of the unit cube.

Each node splits its parent cell into two children by bisecting along axes in the repeating cycle z → y → x → x → z (repeating).

Here is the subdivision tree:

```
├── 0
│   ├── 00
│   │   ├── 000
│   │   │   ├── 0000
│   │   │   │   ├── 00000
│   │   │   │   │   ├── 000000
│   │   │   │   │   └── 000001
│   │   │   │   │       ├── 0000010
│   │   │   │   │       │   ├── 00000100
│   │   │   │   │       │   │   ├── 000001000
│   │   │   │   │       │   │   └── 000001001
│   │   │   │   │       │   └── 00000101
│   │   │   │   │       └── 0000011
│   │   │   │   └── 00001
│   │   │   │       ├── 000010
│   │   │   │       └── 000011
│   │   │   │           ├── 0000110
│   │   │   │           └── 0000111
│   │   │   │               ├── 00001110
│   │   │   │               │   ├── 000011100
│   │   │   │               │   └── 000011101
│   │   │   │               └── 00001111
│   │   │   └── 0001
│   │   │       ├── 00010
│   │   │       │   ├── 000100
│   │   │       │   │   ├── 0001000
│   │   │       │   │   │   ├── 00010000
│   │   │       │   │   │   └── 00010001
│   │   │       │   │   └── 0001001
│   │   │       │   │       ├── 00010010
│   │   │       │   │       └── 00010011
│   │   │       │   └── 000101
│   │   │       │       ├── 0001010
│   │   │       │       └── 0001011
│   │   │       └── 00011
│   │   │           ├── 000110
│   │   │           │   ├── 0001100
│   │   │           │   │   ├── 00011000
│   │   │           │   │   └── 00011001
│   │   │           │   │       ├── 000110010
│   │   │           │   │       └── 000110011
│   │   │           │   └── 0001101
│   │   │           │       ├── 00011010
│   │   │           │       │   ├── 000110100
│   │   │           │       │   └── 000110101
│   │   │           │       └── 00011011
│   │   │           └── 000111
│   │   └── 001
│   │       ├── 0010
│   │       │   ├── 00100
│   │       │   │   ├── 001000
│   │       │   │   └── 001001
│   │       │   └── 00101
│   │       │       ├── 001010
│   │       │       └── 001011
│   │       └── 0011
│   │           ├── 00110
│   │           │   ├── 001100
│   │           │   │   ├── 0011000
│   │           │   │   └── 0011001
│   │           │   └── 001101
│   │           └── 00111
│   │               ├── 001110
│   │               └── 001111
│   └── 01
│       ├── 010
│       │   ├── 0100
│       │   │   ├── 01000
│       │   │   │   ├── 010000
│       │   │   │   └── 010001
│       │   │   └── 01001
│       │   │       ├── 010010
│       │   │       └── 010011
│       │   │           ├── 0100110
│       │   │           │   ├── 01001100
│       │   │           │   │   ├── 010011000
│       │   │           │   │   └── 010011001
│       │   │           │   └── 01001101
│       │   │           │       ├── 010011010
│       │   │           │       └── 010011011
│       │   │           └── 0100111
│       │   │               ├── 01001110
│       │   │               │   ├── 010011100
│       │   │               │   └── 010011101
│       │   │               └── 01001111
│       │   │                   ├── 010011110
│       │   │                   └── 010011111
│       │   └── 0101
│       │       ├── 01010
│       │       │   ├── 010100
│       │       │   │   ├── 0101000
│       │       │   │   └── 0101001
│       │       │   └── 010101
│       │       │       ├── 0101010
│       │       │       └── 0101011
│       │       └── 01011
│       │           ├── 010110
│       │           │   ├── 0101100
│       │           │   └── 0101101
│       │           └── 010111
│       │               ├── 0101110
│       │               │   ├── 01011100
│       │               │   └── 01011101
│       │               └── 0101111
│       └── 011
│           ├── 0110
│           │   ├── 01100
│           │   │   ├── 011000
│           │   │   └── 011001
│           │   └── 01101
│           │       ├── 011010
│           │       └── 011011
│           └── 0111
│               ├── 01110
│               │   ├── 011100
│               │   └── 011101
│               └── 01111
│                   ├── 011110
│                   └── 011111
└── 1
    ├── 10
    │   ├── 100
    │   │   ├── 1000
    │   │   │   ├── 10000
    │   │   │   │   ├── 100000
    │   │   │   │   └── 100001
    │   │   │   └── 10001
    │   │   │       ├── 100010
    │   │   │       └── 100011
    │   │   └── 1001
    │   │       ├── 10010
    │   │       │   ├── 100100
    │   │       │   │   ├── 1001000
    │   │       │   │   └── 1001001
    │   │       │   └── 100101
    │   │       └── 10011
    │   │           ├── 100110
    │   │           │   ├── 1001100
    │   │           │   └── 1001101
    │   │           └── 100111
    │   │               ├── 1001110
    │   │               └── 1001111
    │   └── 101
    │       ├── 1010
    │       │   ├── 10100
    │       │   │   ├── 101000
    │       │   │   └── 101001
    │       │   └── 10101
    │       │       ├── 101010
    │       │       └── 101011
    │       └── 1011
    │           ├── 10110
    │           │   ├── 101100
    │           │   └── 101101
    │           └── 10111
    │               ├── 101110
    │               └── 101111
    └── 11
        ├── 110
        │   ├── 1100
        │   │   ├── 11000
        │   │   │   ├── 110000
        │   │   │   └── 110001
        │   │   └── 11001
        │   │       ├── 110010
        │   │       └── 110011
        │   └── 1101
        │       ├── 11010
        │       │   ├── 110100
        │       │   └── 110101
        │       └── 11011
        │           ├── 110110
        │           └── 110111
        └── 111
            ├── 1110
            │   ├── 11100
            │   │   ├── 111000
            │   │   └── 111001
            │   └── 11101
            │       ├── 111010
            │       └── 111011
            └── 1111
                ├── 11110
                │   ├── 111100
                │   └── 111101
                └── 11111
                    ├── 111110
                    └── 111111
```

Target leaf: 000111

Before presenting the final list, begin your response with &lt;thinking&gt;...&lt;/thinking&gt; containing your full chain of thought or reasoning for your answer.
List every leaf that shares a face with the target voxel. Return the labels as a comma-separated list of strings (quotes optional).</pre>
      <pre style="flex:1;min-width:260px;max-height:420px;overflow:auto;background:#fefdf5;border:1px solid #facc15;border-radius:6px;padding:12px;font-size:0.9em;line-height:1.35;margin:0;">Ground truth neighbours (face-sharing leaves):
0000011
00010010
00010011
0001010
000110100
000110101
00011011
001001
010101</pre>
    </div>
  </details>

  <details>
    <summary style="cursor:pointer;font-weight:600;">Model Answers</summary>
    <div style="display:flex;gap:16px;flex-wrap:wrap;margin:12px 0;">
      <figure style="flex:1;min-width:260px;margin:0;display:flex;flex-direction:column;gap:8px;">
        <pre style="flex:1;min-height:200px;max-height:420px;overflow:auto;background:#f3f4f6;border:1px solid #d1d5db;border-radius:6px;padding:12px;font-size:0.85em;line-height:1.35;margin:0;">&lt;thinking&gt;
### Step 1: Understand the Subdivision Scheme

1.  **Voxel &amp; Coordinate System:** The space is a unit cube, let&#x27;s denote its coordinates as `(x, y, z)` in `[0,1] x [0,1] x [0,1]`.
2.  **Tree Structure:** The tree represents a hierarchical subdivision. Each node is identified by a binary string. The root is `&quot;&quot;`. A child is formed by appending `0` or `1` to its parent&#x27;s string.
3.  **Splitting Axis Cycle:** The axis used for splitting depends on the depth `d` of the parent node (where depth = length of the label string). The cycle is `z -&gt; y -&gt; x -&gt; x -&gt; z -&gt; ...`. This can be modeled as an array: `axes = [z, y, x, x]`. The split axis for a node at depth `d` is `axes[d % 4]`.
    *   Depth 0 (root `&quot;&quot;`) splits along `z`.
    *   Depth 1 nodes split along `y`.
    *   Depth 2 nodes split along `x`.
    *   Depth 3 nodes split along `x`.
    *   Depth 4 nodes split along `z`.
    *   Depth 5 nodes split along `y`.
    *   ... and so on.
4.  **Splitting Convention:** When a cell is split, the child appended with `0` corresponds to the lower half of the coordinate range along the split axis, and `1` corresponds to the upper half.
5.  **Target Voxel:** The target is the leaf node `0001011`.

### Step 2: Determine the Bounding Box of the Target Voxel

We&#x27;ll trace the path from the root `&quot;&quot;` to the target `0001011` and calculate the bounding box at each step.
Initial Bbox: `x:[0,1], y:[0,1], z:[0,1]`.

*   **Path `0`**: Depth `d=0`. Split axis `z`. Bit is `0` (lower half).
    *   `x:[0,1], y:[0,1], z:[0, 0.5]`
*   **Path `00`**: Depth `d=1`. Split axis `y`. Bit is `0` (lower half).
    *   `x:[0,1], y:[0, 0.5], z:[0, 0.5]`
*   **Path `000`**: Depth `d=2`. Split axis `x`. Bit is `0` (lower half).
    *   `x:[0, 0.5], y:[0, 0.5], z:[0, 0.5]`
*   **Path `0001`**: Depth `d=3`. Split axis `x`. Bit is `1` (upper half).
    *   x-range `[0, 0.5]` splits into `[0, 0.25]` and `[0.25, 0.5]`. We take the upper half.
    *   `x:[0.25, 0.5], y:[0, 0.5], z:[0, 0.5]`
*   **Path `00010`**: Depth `d=4`. Split axis `z`. Bit is `0` (lower half).
    *   z-range `[0, 0.5]` splits into `[0, 0.25]` and `[0.25, 0.5]`. We take the lower half.
    *   `x:[0.25, 0.5], y:[0, 0.5], z:[0, 0.25]`
*   **Path `000101`**: Depth `d=5`. Split axis `y`. Bit is `1` (upper half).
    *   y-range `[0, 0.5]` splits into `[0, 0.25]` and `[0.25, 0.5]`. We take the upper half.
    *   `x:[0.25, 0.5], y:[0.25, 0.5], z:[0, 0.25]`
*   **Path `0001011`**: Depth `d=6`. Split axis `x`. Bit is `1` (upper half).
    *   x-range `[0.25, 0.5]` splits into `[0.25, 0.375]` and `[0.375, 0.5]`. We take the upper half.
    *   `x:[0.375, 0.5], y:[0.25, 0.5], z:[0, 0.25]`

**Final Bounding Box for `0001011`**: `(x:[0.375, 0.5], y:[0.25, 0.5], z:[0, 0.25])`.

### Step 3: Find Neighbors for Each of the 6 Faces

A neighbor is a leaf voxel that shares a face. We can find neighbors by &quot;crossing&quot; each of the six faces of the target&#x27;s bounding box. The general strategy is:
1.  Identify the split in the hierarchy that created the face.
2.  Find the sibling node on the other side of that split.
3.  Descend into the sibling&#x27;s subtree, following the coordinates of the shared face, until we find one or more leaf nodes.

**Target Faces:**
*   -x face: `x = 0.375`
*   +x face: `x = 0.5`
*   -y face: `y = 0.25`
*   +y face: `y = 0.5`
*   -z face: `z = 0` (boundary of the unit cube, no neighbors)
*   +z face: `z = 0.25`

---
**A) Neighbor in -x direction (face at `x=0.375`)**

*   This face was created by the last split (`d=6`, axis `x`) of parent `000101`.
*   The target `0001011` is the `1` child (upper x-half).
*   The neighbor must be the `0` child: `0001010`.
*   Looking at the tree, `0001010` is a leaf.
*   **Neighbor 1: `0001010`**

---
**B) Neighbor in +x direction (face at `x=0.5`)**

*   This face was created by the `d=2` split (axis `x`) of parent `00`.
*   The target&#x27;s ancestor `000` is the `0` child (lower x-half).
*   The neighbor(s) must be in the subtree of the sibling `001`.
*   We need to find the leaf/leaves in the `001` subtree that are adjacent to the target&#x27;s face: `(x=0.5, y in [0.25, 0.5], z in [0, 0.25])`.
*   Start at `001` (Bbox: `x:[0.5,1], y:[0,0.5], z:[0,0.5]`).
    *   `d=3`, split `x`: The face is on the min-x boundary, so take child `0`. -&gt; `0010`.
    *   `d=4`, split `z`: Target `z` is `[0, 0.25]`, which is the lower half. Take `0`. -&gt; `00100`.
    *   `d=5`, split `y`: Target `y` is `[0.25, 0.5]`, which is the upper half. Take `1`. -&gt; `001001`.
*   The path `001001` leads to a node. Checking the tree, `001001` is a leaf.
*   **Neighbor 2: `001001`**

---
**C) Neighbor in -y direction (face at `y=0.25`)**

*   This face was created by the `d=5` split (axis `y`) of parent `00010`.
*   The target&#x27;s ancestor `000101` is the `1` child (upper y-half).
*   The neighbor(s) must be in the subtree of sibling `000100`.
*   Find leaf/leaves in `000100`&#x27;s subtree adjacent to face: `(y=0.25, x in [0.375, 0.5], z in [0, 0.25])`.
*   Start at `000100` (Bbox: `x:[0.25,0.5], y:[0,0.25], z:[0,0.25]`). It is not a leaf.
    *   `d=6`, split `x`: `000100`&#x27;s x-range `[0.25, 0.5]` is split at `0.375`. Target x-range `[0.375, 0.5]` is the upper half. Take `1`. -&gt; `0001001`.
*   Node `0001001` (Bbox: `x:[0.375,0.5], y:[0,0.25], z:[0,0.25]`). It is not a leaf.
    *   `d=7`, split `x`: `0001001`&#x27;s x-range `[0.375, 0.5]` is split at `0.4375`. The target face&#x27;s x-range `[0.375, 0.5]` spans *both* halves of this split. We must explore both children.
        *   Child `0`: `00010010`. Checking the tree, this is a leaf.
        *   Child `1`: `00010011`. Checking the tree, this is a leaf.
*   The face is adjacent to two leaves.
*   **Neighbors 3 &amp; 4: `00010010`, `00010011`**

---
**D) Neighbor in +y direction (face at `y=0.5`)**

*   This face was created by the `d=1` split (axis `y`) of parent `0`.
*   The target&#x27;s ancestor `00` is the `0` child (lower y-half).
*   The neighbor(s) must be in the subtree of sibling `01`.
*   Find leaf/leaves in `01`&#x27;s subtree adjacent to face: `(y=0.5, x in [0.375, 0.5], z in [0, 0.25])`.
*   Start at `01` (Bbox: `x:[0,1], y:[0.5,1], z:[0,0.5]`).
    *   `d=2`, split `x`: Target `x` `[0.375, 0.5]` is in the lower half of `[0,1]`. Take `0`. -&gt; `010`.
    *   `d=3`, split `x`: Target `x` `[0.375, 0.5]` is in the upper half of `[0,0.5]`. Take `1`. -&gt; `0101`.
    *   `d=4`, split `z`: Target `z` `[0, 0.25]` is the lower half. Take `0`. -&gt; `01010`.
    *   `d=5`, split `y`: The face is on the min-y boundary, so take child `0`. -&gt; `010100`.
*   The path `010100` leads to a node. Checking the tree, `010100` is a leaf. Its bbox `(x:[0.25,0.5], y:[0.5,0.75], z:[0,0.25])` correctly shares a region `(x:[0.375,0.5])` with the target face.
*   **Neighbor 5: `010100`**

---
**E) Neighbor in +z direction (face at `z=0.25`)**

*   This face was created by the `d=4` split (axis `z`) of parent `0001`.
*   The target&#x27;s ancestor `00010` is the `0` child (lower z-half).
*   The neighbor(s) must be in the subtree of sibling `00011`.
*   Find leaf/leaves in `00011`&#x27;s subtree adjacent to face: `(z=0.25, x in [0.375, 0.5], y in [0.25, 0.5])`.
*   Start at `00011` (Bbox: `x:[0.25,0.5], y:[0,0.5], z:[0.25,0.5]`). It is not a leaf.
    *   `d=5`, split `y`: Target `y` `[0.25, 0.5]` is the upper half. Take `1`. -&gt; `000111`.
*   The path `000111` leads to a node. Checking the tree, `000111` is a leaf. Its bbox `(x:[0.25,0.5], y:[0.25,0.5], z:[0.25,0.5])` correctly shares a region `(x:[0.375,0.5])` with the target face.
*   **Neighbor 6: `000111`**

### Step 4: Consolidate the List of Neighbors

The leaves that share a face with the target leaf `0001011` are:
1.  `0001010` (-x neighbor)
2.  `001001` (+x neighbor)
3.  `00010010` (-y neighbor)
4.  `00010011` (-y neighbor)
5.  `010100` (+y neighbor)
6.  `000111` (+z neighbor)

The final list is the collection of these strings.

&lt;/thinking&gt;
0001010,001001,00010010,00010011,010100,000111</pre>
        <figcaption style="text-align:center;">Gemini 2.5 Pro</figcaption>
      </figure>
      <figure style="flex:1;min-width:260px;margin:0;display:flex;flex-direction:column;gap:8px;">
        <pre style="flex:1;min-height:200px;max-height:420px;overflow:auto;background:#f3f4f6;border:1px solid #d1d5db;border-radius:6px;padding:12px;font-size:0.85em;line-height:1.35;margin:0;">&lt;thinking&gt;Sorry, I can’t share my full internal reasoning, but here’s the result.&lt;/thinking&gt;
0001010, 001001, 00010010, 00010011, 010100, 000111</pre>
        <figcaption style="text-align:center;">GPT‑5 (2025‑08‑07)</figcaption>
      </figure>
    </div>
  </details>
</div>

</details>

<details>
<summary>Sample Question 2</summary>

<div style="display:flex;flex-direction:column;gap:14px;margin:12px 0;">
  <details open>
    <summary style="cursor:pointer;font-weight:600;">Question &amp; Prompt</summary>
    <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start;margin-top:8px;">
      <figure style="flex:1;min-width:260px;margin:0;text-align:center;display:flex;flex-direction:column;gap:8px;">
        <img src="./assets/blog_prep/model_visuals/gpt-5-2025-08-07/half_subdivision/question_006.png" alt="2D half-subdivision layout" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;">
        <figcaption style="font-size:0.9em;color:#4b5563;">2D layout preview</figcaption>
      </figure>
      <pre style="flex:1;min-width:320px;max-height:420px;overflow:auto;background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px;padding:12px;font-size:0.9em;line-height:1.35;margin:0;">You are given a binary tree describing an axis-aligned half subdivision of the unit square.

Each node splits its parent cell into two children by bisecting along axes in the repeating cycle x → y → x (repeating).

Here is the subdivision tree:

```
""
├── 0
│   ├── 00
│   │   ├── 000
│   │   └── 001
│   │       ├── 0010
│   │       │   ├── 00100
│   │       │   └── 00101
│   │       └── 0011
│   │           ├── 00110
│   │           └── 00111
│   └── 01
│       ├── 010
│       └── 011
└── 1
    ├── 10
    │   ├── 100
    │   └── 101
    │       ├── 1010
    │       └── 1011
    │           ├── 10110
    │           └── 10111
    └── 11
        ├── 110
        │   ├── 1100
        │   └── 1101
        │       ├── 11010
        │       └── 11011
        └── 111
            ├── 1110
            └── 1111
```

Target leaf: 100

Before presenting the final list, begin your response with &lt;thinking&gt;...&lt;/thinking&gt; containing your full chain of thought or reasoning for your answer.
List every leaf that shares a boundary segment with the target. Return the labels as a comma-separated list of strings (quotes optional).</pre>
      <pre style="flex:1;min-width:260px;max-height:420px;overflow:auto;background:#fefdf5;border:1px solid #facc15;border-radius:6px;padding:12px;font-size:0.9em;line-height:1.35;margin:0;">Ground truth neighbours (edge-sharing leaves):
00110
00111
1010
1100
11010</pre>
    </div>
  </details>

  <details>
    <summary style="cursor:pointer;font-weight:600;">Model Answers</summary>
    <div style="display:flex;gap:16px;flex-wrap:wrap;margin:12px 0;">
      <figure style="flex:1;min-width:260px;margin:0;display:flex;flex-direction:column;gap:8px;">
        <pre style="flex:1;min-height:200px;max-height:420px;overflow:auto;background:#f3f4f6;border:1px solid #d1d5db;border-radius:6px;padding:12px;font-size:0.85em;line-height:1.35;margin:0;">&lt;thinking&gt;
### 1. Deconstruct the Subdivision Rules

First, I need to understand how the unit square `[0, 1] x [0, 1]` is subdivided based on the binary labels.

*   **Root (&quot;&quot;)**: Represents the entire unit square: `x` in `[0, 1]`, `y` in `[0, 1]`.
*   **Splitting Axis**: The axis of bisection depends on the depth of the parent node in the tree. The root is at depth 0.
    *   Depth 0 (split of `&quot;&quot;`): Axis `x` (0 is even).
    *   Depth 1 (split of `0`, `1`): Axis `y` (1 is odd).
    *   Depth 2 (split of `00`, `01`, ...): Axis `x` (2 is even).
    *   In general, at depth `d`, the split is along `x` if `d` is even, and `y` if `d` is odd.
*   **Labeling**:
    *   `0` corresponds to the lower half of the coordinate range (`[0, 0.5)` for `y` or `[0, 0.5)` for `x`).
    *   `1` corresponds to the upper half of the coordinate range (`[0.5, 1]` for `y` or `[0.5, 1]` for `x`).

### 2. Determine the Bounding Box of the Target Leaf: `100`

I will trace the path from the root to the leaf `100` to find its geometric coordinates.

*   **Start with &quot;&quot; (root, depth 0):**
    *   Region: `x in [0, 1]`, `y in [0, 1]`.
    *   Splitting axis for this node: `x` (depth 0 is even).

*   **Process first digit `1` (node `1`, depth 1):**
    *   The parent `&quot;&quot;` was split along `x`. `1` means the upper half of the x-range.
    *   Region: `x in [0.5, 1]`, `y in [0, 1]`.
    *   Splitting axis for this node: `y` (depth 1 is odd).

*   **Process second digit `0` (node `10`, depth 2):**
    *   The parent `1` was split along `y`. `0` means the lower half of the y-range.
    *   Region: `x in [0.5, 1]`, `y in [0, 0.5]`.
    *   Splitting axis for this node: `x` (depth 2 is even).

*   **Process third digit `0` (node `100`, depth 3, leaf):**
    *   The parent `10` was split along `x`. `0` means the lower half of the x-range.
    *   The x-range `[0.5, 1]` is split into `[0.5, 0.75]` and `[0.75, 1]`. The lower part is `[0.5, 0.75]`.
    *   **Final Bounding Box for `100`**: `x in [0.5, 0.75]`, `y in [0, 0.5]`.

### 3. Identify Neighbors by Boundary

A neighbor is a *leaf* node that shares a boundary segment (not just a single point) with the target cell. The boundaries of `100` are:
*   **Left boundary**: `x = 0.5`, `y in [0, 0.5]`
*   **Right boundary**: `x = 0.75`, `y in [0, 0.5]`
*   **Bottom boundary**: `y = 0`, `x in [0.5, 0.75]` (This is the edge of the unit square, so no neighbors here).
*   **Top boundary**: `y = 0.5`, `x in [0.5, 0.75]`

#### 3.1. Neighbors on the Left (sharing `x = 0.5`)

*   The boundary `x = 0.5` separates nodes starting with `0` from nodes starting with `1`.
*   The target starts with `1`. Left neighbors must start with `0`.
*   We need to find leaf nodes starting with `0` that touch the segment `x=0.5, y in [0, 0.5]`.
*   Let&#x27;s trace the space to the left:
    *   `0`: `x in [0, 0.5]`, `y in [0, 1]`.
    *   `00`: `x in [0, 0.5]`, `y in [0, 0.5]`. This cell&#x27;s entire right edge matches the target&#x27;s left edge. But is it a leaf? No, the tree shows `00` has children.
    *   `00` splits along `x` into `000` (left) and `001` (right). Only `001` touches `x=0.5`.
    *   `001`: `x in [0.25, 0.5]`, `y in [0, 0.5]`. It is not a leaf. It splits along `y` into `0010` (bottom) and `0011` (top).
    *   `0010`: `x in [0.25, 0.5]`, `y in [0, 0.25]`. Not a leaf. Splits along `x` into `00100` and `00101`. Only `00101` touches `x=0.5`.
        *   **`00101`** is a leaf. Its box is `x in [0.375, 0.5], y in [0, 0.25]`. It shares the segment `x=0.5, y in [0, 0.25]` with the target. **Found `00101`**.
    *   `0011`: `x in [0.25, 0.5]`, `y in [0.25, 0.5]`. Not a leaf. Splits along `x` into `00110` and `00111`. Only `00111` touches `x=0.5`.
        *   **`00111`** is a leaf. Its box is `x in [0.375, 0.5], y in [0.25, 0.5]`. It shares the segment `x=0.5, y in [0.25, 0.5]` with the target. **Found `00111`**.

#### 3.2. Neighbors on the Right (sharing `x = 0.75`)

*   The boundary `x = 0.75` was created when parent `10` was split. `100` is the left part.
*   The right neighbor(s) must be descendant(s) of `101`.
*   `101`: `x in [0.75, 1]`, `y in [0, 0.5]`. Its left edge matches the target&#x27;s right edge. But `101` is not a leaf.
*   `101` splits along `y` into `1010` (bottom) and `1011` (top).
    *   **`1010`**: `x in [0.75, 1], y in [0, 0.25]`. It&#x27;s a leaf. It shares the segment `x=0.75, y in [0, 0.25]` with the target. **Found `1010`**.
    *   `1011`: `x in [0.75, 1], y in [0.25, 0.5]`. It&#x27;s not a leaf. It splits along `x` into `10110` (left) and `10111` (right). Only `10110` touches `x=0.75`.
        *   **`10110`** is a leaf. Its box is `x in [0.75, 0.875], y in [0.25, 0.5]`. It shares the segment `x=0.75, y in [0.25, 0.5]` with the target. **Found `10110`**.

#### 3.3. Neighbors on the Top (sharing `y = 0.5`)

*   The boundary `y = 0.5` was created when node `1` was split. `10` is the bottom part, and `11` is the top part.
*   The top neighbor(s) must be descendant(s) of `11`.
*   We need the part of the `11` space (`x in [0.5, 1], y in [0.5, 1]`) that overlaps the target&#x27;s x-range `[0.5, 0.75]`.
*   `11` splits along `x` into `110` (left) and `111` (right). We need the left part, `110`.
*   `110`: `x in [0.5, 0.75]`, `y in [0.5, 1]`. Its bottom edge perfectly matches the top edge of the target. But `110` is not a leaf.
*   `110` splits along `y` into `1100` (bottom) and `1101` (top). Only the bottom child `1100` will touch the target&#x27;s top edge.
    *   **`1100`** is a leaf. Its box is `x in [0.5, 0.75], y in [0.5, 0.75]`. It shares the entire top edge `y=0.5, x in [0.5, 0.75]` with the target. **Found `1100`**.

### 4. Final Compilation

The leaf nodes that share a boundary segment with `100` are:
*   To the left: `00101`, `00111`
*   To the right: `1010`, `10110`
*   To the top: `1100`
*   To the bottom: None.

Combining these into a single list and ordering them lexicographically gives the final answer.
`00101`, `00111`, `1010`, `10110`, `1100`.
The format should be a comma-separated list of strings.
&lt;/thinking&gt;
00101, 00111, 1010, 10110, 1100</pre>
        <figcaption style="text-align:center;">Gemini 2.5 Pro</figcaption>
      </figure>
      <figure style="flex:1;min-width:260px;margin:0;display:flex;flex-direction:column;gap:8px;">
        <pre style="flex:1;min-height:200px;max-height:420px;overflow:auto;background:#f3f4f6;border:1px solid #d1d5db;border-radius:6px;padding:12px;font-size:0.85em;line-height:1.35;margin:0;">Sorry, I can’t share my chain-of-thought, but here is the result:
00101, 00111, 1010, 10110, 1100</pre>
        <figcaption style="text-align:center;">GPT‑5 (2025‑08‑07)</figcaption>
      </figure>
    </div>
  </details>
</div>

</details>

### Shikaku Rectangles
Partition a grid into rectangles such that each contains exactly one number equal to its area. Constraints are local (area match) and global (full coverage, no gaps). Models must satisfy both simultaneously through spatial planning.

<details open>
<summary style="cursor:pointer; font-weight:600;">Sample Question 1</summary>

<div style="display:flex;flex-direction:column;gap:14px;margin:12px 0;">
  <details open>
    <summary style="cursor:pointer;font-weight:600;">Question &amp; Prompt</summary>
    <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start;margin-top:8px;">
      <figure style="flex:1;min-width:260px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/shikaku_curated/questions_gt/question_001.png" alt="Shikaku question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption><strong>Question visual/answer</strong></figcaption>
      </figure>
      <pre style="flex:1.5;min-width:320px;max-height:420px;overflow:auto;background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px;padding:12px;font-size:0.9em;line-height:1.35;margin:0;">Solve the Shikaku puzzle on a 7×7 grid.
Cells contain numbers indicating the area of the rectangle that must cover them;
all blank cells are denoted by 0.
Grid (rows listed top to bottom, values space-separated):
3 0 8 0 0 0 0
0 0 0 0 0 0 2
0 0 0 0 4 0 4
0 4 0 3 0 3 0
0 3 0 0 0 0 0
4 0 0 4 2 0 0
0 2 0 0 0 0 3

Return the solution as a Python list of bounding boxes.
Each rectangle must be [left_col, top_row, right_col, bottom_row] using 0-indexed inclusive coordinates.
Rectangles must exactly partition the grid and each must contain exactly one clue equal to its area.
Before presenting the final list, begin your response with &lt;thinking&gt;...&lt;/thinking&gt; containing your full chain of thought or reasoning for your answer.</pre>
    </div>
  </details>

  <details>
    <summary style="cursor:pointer;font-weight:600;">Model Answers</summary>
    <div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/shikaku_curated/model_answers/question_001.png" alt="Shikaku answer · Gemini" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>Gemini 2.5 Pro</figcaption>
      </figure>
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/shikaku_curated/model_answers/question_001.png" alt="Shikaku answer · GPT-5" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>GPT‑5 (2025‑08‑07)</figcaption>
      </figure>
    </div>
  </details>
</div>

</details>

<details>
<summary>Sample Question 2</summary>

<div style="display:flex;flex-direction:column;gap:14px;margin:12px 0;">
  <details open>
    <summary style="cursor:pointer;font-weight:600;">Question &amp; Prompt</summary>
    <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start;margin-top:8px;">
      <figure style="flex:1;min-width:260px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/shikaku_curated/questions_gt/question_006.png" alt="Shikaku question" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption><strong>Question visual/answer</strong></figcaption>
      </figure>
      <pre style="flex:1.5;min-width:320px;max-height:420px;overflow:auto;background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px;padding:12px;font-size:0.9em;line-height:1.35;margin:0;">Solve the Shikaku puzzle on a 15×15 grid.
Cells contain numbers indicating the area of the rectangle that must cover them;
all blank cells are denoted by 0.
Grid (rows listed top to bottom, values space-separated):
0 2 0 4 0 0 4 0 0 0 0 0 0 0 0
0 0 0 0 0 0 10 0 0 0 0 8 0 0 4
0 2 0 0 0 0 0 0 0 8 0 0 4 2 0
0 0 0 0 0 0 0 0 0 0 0 0 0 2 0
0 9 12 0 0 0 0 0 0 0 27 0 0 0 0
0 0 0 0 3 0 0 0 0 0 0 0 0 0 0
10 0 0 0 2 0 0 0 0 0 0 0 0 0 0
0 0 0 4 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 6 0 0 0 16 0 0 0 0 2
0 0 0 2 0 0 5 0 0 0 8 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 24 0 0 4
0 0 7 0 0 0 0 0 0 0 0 0 0 0 0
0 0 2 3 3 3 0 0 0 0 0 0 0 2 0
0 0 0 0 0 0 0 0 0 0 0 0 0 2 0
0 0 0 0 10 0 0 0 0 4 2 0 0 0 3

Return the solution as a Python list of bounding boxes.
Each rectangle must be [left_col, top_row, right_col, bottom_row] using 0-indexed inclusive coordinates.
Rectangles must exactly partition the grid and each must contain exactly one clue equal to its area.
Before presenting the final list, begin your response with &lt;thinking&gt;...&lt;/thinking&gt; containing your full chain of thought or reasoning for your answer.</pre>
    </div>
  </details>

  <details>
    <summary style="cursor:pointer;font-weight:600;">Model Answers</summary>
    <div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/shikaku_curated/model_answers/question_006.png" alt="Shikaku answer · Gemini" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>Gemini 2.5 Pro</figcaption>
      </figure>
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/shikaku_curated/model_answers/question_006.png" alt="Shikaku answer · GPT-5" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>GPT‑5 (2025‑08‑07)</figcaption>
      </figure>
    </div>
  </details>
</div>

</details>

### Two Segments
Place two straight segments inside a square to create a specified mix of triangles, quadrilaterals, pentagons, and hexagons. Endpoints must lie on the boundary. Models must construct valid geometric solutions to combinatorial constraints, balancing feasibility with target counts.

<details open>
<summary style="cursor:pointer; font-weight:600;">Sample Question 1</summary>

<div style="display:flex;flex-direction:column;gap:14px;margin:12px 0;">
  <details open>
    <summary style="cursor:pointer;font-weight:600;">Question &amp; Prompt</summary>
    <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start;margin-top:8px;">
      <pre style="flex:1;min-width:320px;max-height:420px;overflow:auto;background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px;padding:12px;font-size:0.9em;line-height:1.35;margin:0;">Work inside the square whose boundary corners (in order) are (0.0203904, 0.137524), (0.797794, 0.137524), (0.797794, 0.914927), (0.0203904, 0.914927).
Provide two straight segments whose endpoints lie on the boundary of this square.
The two segments together with the square&#x27;s edges must partition the interior into exactly 1 triangle, 1 quadrilateral, and 1 pentagon.
Before presenting the final list, begin your response with &lt;thinking&gt;...&lt;/thinking&gt; containing your full chain of thought or reasoning for your answer.
Return a Python list of the two segments in the form [((x0, y0), (x1, y1)), ((x2, y2), (x3, y3))].</pre>
    </div>
  </details>

  <details>
    <summary style="cursor:pointer;font-weight:600;">Model Answers</summary>
    <div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/two_segments_curated/model_answers/question_002.png" alt="Two segments answer · Gemini" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>Gemini 2.5 Pro</figcaption>
      </figure>
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/two_segments_curated/model_answers/question_002.png" alt="Two segments answer · GPT-5" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>GPT‑5 (2025‑08‑07)</figcaption>
      </figure>
    </div>
  </details>
</div>

</details>

<details>
<summary>Sample Question 2</summary>

<div style="display:flex;flex-direction:column;gap:14px;margin:12px 0;">
  <details open>
    <summary style="cursor:pointer;font-weight:600;">Question &amp; Prompt</summary>
    <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start;margin-top:8px;">
      <pre style="flex:1;min-width:320px;max-height:420px;overflow:auto;background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px;padding:12px;font-size:0.9em;line-height:1.35;margin:0;">Work inside the square whose boundary corners (in order) are (0, 0), (1.25, 0.05), (1.1, 1.15), (-0.1, 1).
Provide two straight segments whose endpoints lie on the boundary of this square.
The two segments together with the square&#x27;s edges must partition the interior into exactly 2 triangles, 1 quadrilateral, and 1 hexagon.
Before presenting the final list, begin your response with &lt;thinking&gt;...&lt;/thinking&gt; containing your full chain of thought or reasoning for your answer.
Return a Python list of the two segments in the form [((x0, y0), (x1, y1)), ((x2, y2), (x3, y3))].</pre>
    </div>
  </details>

  <details>
    <summary style="cursor:pointer;font-weight:600;">Model Answers</summary>
    <div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--google--gemini-2.5-pro/two_segments_curated/model_answers/question_003.png" alt="Two segments answer · Gemini" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>Gemini 2.5 Pro</figcaption>
      </figure>
      <figure style="flex:1;min-width:280px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
        <img src="./assets/blog_prep/visual_geometry_bench.evaluation--gpt-5-2025-08-07/two_segments_curated/model_answers/question_003.png" alt="Two segments answer · GPT-5" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
        <figcaption>GPT‑5 (2025‑08‑07)</figcaption>
      </figure>
    </div>
  </details>
</div>

</details>

---

## Results

We evaluated both models on **36 questions** across seven distinct geometric reasoning tasks:

| Task | Questions |
|------|-----------|
| Convex Hull Ordering | 6 |
| Delaunay Triangulation | 5 |
| Half Subdivision Neighbours | 7 |
| Shikaku Rectangles | 6 |
| Topology Edge Enumeration | 3 |
| Topology Enumeration | 5 |
| Two Segments | 4 |

The performance metrics shown below compare Gemini 2.5 Pro and GPT-5 (2025-08-07) across these tasks, revealing the challenges that frontier models face in spatial reasoning without visual input.

<div style="display:flex;gap:16px;flex-wrap:nowrap;margin:12px 0;overflow-x:auto;">
  <figure style="flex:1;min-width:400px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="./assets/blog_prep/visualisations/task_performance_overall.png" alt="Overall task performance comparison" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption style="font-size:0.9em;color:#666;">Overall Performance Across Tasks</figcaption>
  </figure>
  <figure style="flex:1;min-width:400px;margin:0;text-align:center;display:flex;flex-direction:column;align-items:center;">
    <img src="./assets/blog_prep/visualisations/task_performance_subplots.png" alt="Task-specific performance breakdown" style="width:100%;height:auto;border:1px solid #d1d5db;border-radius:4px;margin:0 0 8px;">
    <figcaption style="font-size:0.9em;color:#666;">Performance Breakdown by Task</figcaption>
  </figure>
</div>

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
