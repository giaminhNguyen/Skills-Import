---
name: story-branch-writer
description: Create a complete alternate-branch story from a reference story. Use when the user provides a sample story and asks for a new branch, alternate timeline, reincarnation/transmigration variant, what-if version, changed premise, or an automatically selected new storyline. If the user gives no branch idea, automatically find leverage points, generate only a few viable branches, select one quickly, rebuild causality, plan the arc, write scene by scene, maintain story state, and deliver the finished story rather than exposing internal planning by default.
---

# Story Branch Writer

Turn a reference story into a genuinely new branch while preserving the useful narrative DNA of the source. Treat the reference as canon plus a storytelling model, not as a plot to replay.

## Inputs

Require only the reference story.

Accept these optional inputs:
- `branch`: a user-specified divergence or premise.
- `direction`: tonal or structural preference such as psychological, revenge, romance, mystery, high-twist, realistic, or dark.
- `target_length`: desired approximate length.

If `branch` is absent, run automatic branch selection. Do not ask the user to choose unless they explicitly request branch options.

## Default user-facing output

Return the finished story only, unless the user asks to see analysis, branch candidates, outline, state, or QA notes.

Do not expose routine internal files or chain-of-thought. Keep analysis artifacts as working memory.

## Workflow

### 1. Understand canon

Read the complete reference before planning the branch. Extract only what is useful for generation:
- characters and story functions;
- relationships;
- chronological event chain;
- cause -> effect links;
- character knowledge and hidden information;
- central conflict and emotional engine;
- recurring story mechanisms;
- setup -> payoff patterns;
- hook and reveal rhythm;
- pacing, POV, dialogue density, prose density, and ending shape;
- leverage points: facts which, if changed, would force major downstream consequences.

Create or update `canon.md` when persistent files are available. Avoid producing a generic summary in place of structural analysis.

### 2. Choose a branch efficiently

If the user supplied `branch`, accept it and skip candidate generation unless it is internally contradictory.

If no branch was supplied:
1. Identify 3-5 high-leverage points.
2. Generate at most 3-5 branch candidates total.
3. Describe each candidate internally in only 1-3 lines.
4. Select quickly using these questions:
   - Is there a clear source of conflict?
   - Can the change create multiple new consequences rather than one gimmick?
   - Is there enough room for escalation and an ending?
   - Is it meaningfully different from replaying canon?
5. Do not search for an absolute optimum. Prefer a strong branch and move on to writing.

Branch selection should consume little context compared with planning and prose generation.

### 3. Define the divergence

Record in `branch.md`:
- divergence point;
- changed variable(s);
- who knows what at the divergence;
- immediate consequences;
- canon events invalidated by the change;
- narrative promise: the main experience/question that should keep the reader engaged.

Do not preserve narrator, POV, or scene order blindly. Preserve them only when they remain useful after the branch change. If the premise is "transmigrate into Character X", a POV shift may be the correct consequence.

### 4. Rebuild causality

Never bolt the new premise onto the old plot.

For each major changed fact:
1. Find downstream canon events that depended on the old fact.
2. Mark impossible events as invalidated.
3. Generate new consequences from character goals, knowledge, personality, relationships, and constraints.
4. Propagate those consequences forward until the new timeline is coherent.

Avoid the repetitive pattern "the protagonist knew event A -> event A happened exactly as expected." Knowledge of canon must change decisions, and changed decisions must eventually make canon knowledge less reliable.

### 5. Build the story arc

Create `outline.md` with enough detail to sustain the target length, but do not over-plan sentence-level prose.

Include:
- opening hook;
- early proof that the branch matters;
- escalation chain;
- major reveals;
- reversals or shifts in advantage;
- emotional progression;
- climax;
- resolution/ending.

Plan events, not just themes. Make sure something materially changes at regular intervals.

### 6. Maintain compact story state

Use `story_state.json` when persistent files are available. Keep it concise.

Track at minimum:
- current timeline position;
- character knowledge matrix;
- current goals and conflicts;
- relationship changes;
- unresolved reader questions;
- setups awaiting payoff;
- resolved payoffs;
- canon facts still valid;
- branch facts now established.

Do not duplicate large prose passages in state.

See `references/state-schema.md` for the recommended schema.

### 7. Plan and write the next scene

Before prose, make a compact internal scene card:
- scene goal;
- active conflict;
- what changes by the end;
- information revealed or withheld;
- payoff, if any;
- hook/question carried into the next scene.

Then write the scene using only the relevant canon, branch, outline, state, and nearby prose.

Prefer action, dialogue, decisions, discoveries, confrontations, and consequences over long explanatory thought loops.

### 8. Run quick local QA

After each scene, check:
- causal logic;
- knowledge consistency;
- character consistency;
- whether the scene changes story state;
- whether the reader receives progress, payoff, complication, or meaningful new information;
- whether the ending gives a reason to continue;
- whether the scene is merely replaying canon.

Revise only when a real problem exists. Do not spend more tokens polishing analysis than writing the story.

### 9. Run global QA periodically

Every 3-5 scenes, check the arc rather than individual wording:
- Is conflict escalating or evolving?
- Is the narrative promise still active?
- Is the same gimmick repeating?
- Are reveals arriving too early or too late?
- Is the protagonist winning too easily?
- Has canon diverged enough that future events should be replanned?
- Does the planned ending still follow naturally?

Adjust the remaining outline when needed.

### 10. Final edit

After the draft is complete, perform one focused pass for:
- continuity errors;
- repeated explanations;
- pacing dead zones;
- forgotten setups;
- weak or missing payoffs;
- abrupt character decisions;
- ending satisfaction;
- accidental copying of source phrasing.

Deliver the finished story.

## Reader-engagement rules

Optimize for a reader who may never have seen the reference story.

- The branch must work as a standalone story.
- Establish a compelling question early.
- Do not depend on the reader recognizing what changed from canon.
- Convert questions into payoffs; do not stack mysteries indefinitely.
- After a payoff, open a larger or different question when appropriate.
- Use information asymmetry deliberately: track what the reader knows versus each character.
- A high-concept premise is not enough; events must keep happening.
- Do not make every scene end with an artificial twist.
- Let characters reveal themselves through choices and consequences.

See `references/quality-checks.md` for the compact review checklist.

## Token-efficiency rules

- Generate at most 3-5 auto-branch candidates.
- Do not fully simulate every candidate.
- Keep `canon.md`, `branch.md`, and `story_state.json` compressed and factual.
- Do not reread or reinsert the entire reference for every scene when a structured canon summary is sufficient.
- Keep only nearby prose plus relevant state in the active writing context when possible.
- Spend most available generation budget on outline quality, prose, and targeted revision.

## CLI workspace

For a persistent CLI workspace, initialize this layout:

```text
story-project/
├── reference.txt
├── request.md
├── canon.md
├── branch.md
├── outline.md
├── story_state.json
└── story.md
```

Use `scripts/init_story_project.py <directory>` to create the empty workspace.

`request.md` may contain:

```yaml
branch: null
direction: null
target_length: null
```

A null `branch` means fully automatic branch selection.

## Compatibility

- For Codex and OpenCode, use the bundled `AGENTS.md` as project instructions.
- For Claude Code, use the bundled `CLAUDE.md`.
- The workflow and quality rules are intentionally provider-agnostic.
