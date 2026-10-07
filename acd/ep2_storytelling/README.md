# ACD · EP2 "Cold Enough for Company": storytelling fixes and replacement scenes

| File | What it is |
|---|---|
| [`EP2_STORY_ANALYSIS.md`](EP2_STORY_ANALYSIS.md) | Where the storytelling fails and why, using the EP2 render reports and your notes as evidence. Includes the cliffhanger ladder for every scene, the render list with costs, and the free edit fixes. |
| [`EP2_REPLACEMENT_SCENES.md`](EP2_REPLACEMENT_SCENES.md) | The 6 replacement scenes and 6 inserts as script pages: shots, dialogue, why each changed, and "Hang the cliff". |
| [`pika/shots/`](pika/shots/) | 10 render-ready files for `pika/run-shot.js`: 2 plates, 6 scenes and 2 insert reels. |
| [`run_ep2_replacements.sh`](run_ep2_replacements.sh) | Renders them in order inside your `Fantasy` project. |
| [`tools/build_shots.py`](tools/build_shots.py) | Rebuilds the JSON files. Change prompts here, then run `python3 tools/build_shots.py`. |

## The changes in one minute

1. **Cold-open hook (C1).** A frozen man at breakfast, and a passenger borrows his sugar. The episode's question lands in the first second instead of at 1:30.
2. **Show the clues, then pay them off.** Kell's rimed knuckles (P1), Kell **alive** inside the reconstruction (Sc04 v5), KELL written in the empty PASSENGERS column (C3), and a clue replay under the solution (edit only).
3. **The route's next victim is Beatrice, on screen.** The pods turn to her (Sc14 v3), rime grows on her hand (C2), she walks to the wall to pay it herself (Sc16 v4), and Tomas lifts her hand out of the slot before he says the six words (Sc17 v4). The climax now answers a threat the viewer has seen.
4. **Restored buttons.** The aborted "I—" (Sc00 v3), "And nobody looked up" (P2), and both Sc08 jokes (Sc08 v2).
5. **Ysra's exit on screen** (P3).

## Run it on your Mac

```bash
git clone -b claude/ep2-storytelling-scenes-9kr5nf https://github.com/Supamotion/policyIDs.git ~/Downloads/acd-ep2-fixes
cd ~/Downloads/acd-ep2-fixes/acd/ep2_storytelling

./run_ep2_replacements.sh --dry-run    # validates every file against your project, spends nothing
./run_ep2_replacements.sh --tier 1     # story-critical set: Sc14, Sc16, Sc17, hook + inserts (~$13.70)
./run_ep2_replacements.sh --tier 2     # also Sc04, Sc08, pier inserts (~$24 in total)
./run_ep2_replacements.sh              # also the pre-intro (~$27 in total)
```

Set `FANTASY=/path/to/Fantasy` if the project isn't at `~/Downloads/Fantasy`.

The runner:
* copies the shot files into `Fantasy/pika/shots/` and renders **plates first**;
* saves each plate to `pika/refs/` as a 2048 px JPEG (§194), **opens it in Preview, and asks before spending on the scenes that use it**;
* skips anything already rendered, so you can re-run safely;
* stops on `insufficient_balance` (refused jobs aren't billed) and prints the exact `--from` command to resume;
* prints the `--recover <job> <slug>` command if the network drops mid-poll (§203);
* writes logs to `Fantasy/out/ep2_replacement_logs/`.

After rendering, verify each file the usual way (1 fps contact sheet plus windowed transcription), then cut it in following §7 of the analysis.

## Why this wasn't rendered from the cloud session

This session had no route to Pika:
* the environment's network policy blocks `api.pika.art` and `cdn.pika.art`;
* there is no `PIKA_API_KEY` in the environment;
* the reference library (`Fantasy/pika/refs/`) exists only on your Mac.

The runner was tested end to end against a mock of `pika/run-shot.js`: dry run, tiered run, balance stop and resume, network-drop recovery, plate promotion, and plate review with and without a terminal.
