#!/usr/bin/env bash
# Render the EP2 replacement scenes, inserts and plates with the existing Pika runner (pika/run-shot.js).
#
#   ./run_ep2_replacements.sh --dry-run                validate every file, spend nothing
#   ./run_ep2_replacements.sh --tier 1                 story-critical set only      (~$13.70)
#   ./run_ep2_replacements.sh --tier 2                 tiers 1 + 2                  (~$24)
#   ./run_ep2_replacements.sh                          everything                   (~$27)
#   ./run_ep2_replacements.sh --only ep2_scene17_v4    one file (its plate must already exist)
#   ./run_ep2_replacements.sh --from ep2_scene16_v4    resume after a top-up
#   ./run_ep2_replacements.sh --yes                    do not ask before spending
#
# FANTASY=/path/to/Fantasy overrides the project folder (default: ~/Downloads/Fantasy).
# Already-rendered outputs are skipped, so re-running after a failure only spends on what is missing.
# Written for the macOS default bash 3.2.

set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
FANTASY="${FANTASY:-$HOME/Downloads/Fantasy}"
TIER=3
ONLY=""
FROM=""
DRY=0
YES=0

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1 ;;
    --yes|-y) YES=1 ;;
    --tier) shift; TIER="${1:-3}" ;;
    --only) shift; ONLY="${1:-}" ;;
    --from) shift; FROM="${1:-}" ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
    *) echo "Unknown option: $1 (see --help)"; exit 64 ;;
  esac
  shift
done

# name | tier | kind | promote plate output to (relative to $FANTASY) | cost USD
# Plates come first: the scenes after them reference what they produce.
STEPS="ep2_beatrice_frost_still|1|plate|pika/refs/ep2_beatrice_frost_lock.jpg|0.10
ep2_scene14_v3|1|video||3.39
ep2_scene16_v4|1|video||3.39
ep2_scene17_v4|1|video||3.39
ep2_inserts_reel2|1|video||3.39
ep2_kell_alive_still|2|plate|pika/refs/ep2_kell_alive_lock.jpg|0.10
ep2_scene04_v5|2|video||3.39
ep2_scene08_v2|2|video||3.39
ep2_inserts_reel1|2|video||3.39
ep2_scene00_preintro_v3|3|video||3.39"

die() { echo "ERROR: $*" >&2; exit 1; }

[ -d "$FANTASY" ] || die "project folder not found: $FANTASY (set FANTASY=/path/to/Fantasy)"
[ -f "$FANTASY/pika/run-shot.js" ] || die "no pika/run-shot.js in $FANTASY"
command -v node >/dev/null 2>&1 || die "node is not installed"
command -v python3 >/dev/null 2>&1 || die "python3 is not installed"

mkdir -p "$FANTASY/pika/shots" "$FANTASY/out" "$FANTASY/out/ep2_replacement_logs" || die "cannot create folders"
cp "$HERE"/pika/shots/*.json "$FANTASY/pika/shots/" || die "could not copy shot files"
LOGDIR="$FANTASY/out/ep2_replacement_logs"
cd "$FANTASY" || die "cannot cd to $FANTASY"

json_field() {  # json_field <file> <key>
  python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])' "$1" "$2" < /dev/null
}

missing_refs() {  # prints every reference file the shot needs that does not exist yet
  python3 -I -c '
import json, os, sys
d = json.load(open(sys.argv[1]))
for r in d.get("reference_images", []) + d.get("reference_audio", []):
    if not os.path.exists(r):
        print(r)' "$1" < /dev/null
}

promote_plate() {  # promote_plate <slug> <dest.jpg>: newest out/<slug>* image -> 2048px JPEG q92 (§194)
  src="$(ls -t out/"$1"*.png out/"$1"*.jpg out/"$1"*.jpeg 2>/dev/null | head -n 1)"
  [ -n "$src" ] || { echo "   could not find the plate output out/$1*.png"; return 1; }
  if python3 -I - "$src" "$2" <<'PY'
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert("RGB")
im.thumbnail((2048, 2048), Image.LANCZOS)
im.save(sys.argv[2], "JPEG", quality=92, subsampling=0, optimize=True)
PY
  then :
  elif command -v sips >/dev/null 2>&1; then
    sips -s format jpeg -s formatOptions 92 -Z 2048 "$src" --out "$2" >/dev/null || return 1
  else
    echo "   neither Pillow nor sips is available to convert $src"; return 1
  fi
  echo "   plate: $src -> $2"
  echo "   LOOK AT IT before the scenes that use it render: open \"$FANTASY/$2\""
}

# --- select steps ---------------------------------------------------------------------------------
SELECTED=""
TOTAL="0"
started=1
[ -n "$FROM" ] && started=0
while IFS='|' read -r name tier kind dest cost; do
  [ -z "$name" ] && continue
  if [ "$started" = 0 ]; then
    [ "$name" = "$FROM" ] && started=1 || continue
  fi
  if [ -n "$ONLY" ]; then
    [ "$name" = "$ONLY" ] || continue
  elif [ "$tier" -gt "$TIER" ]; then
    continue
  fi
  SELECTED="${SELECTED}${name}|${tier}|${kind}|${dest}|${cost}
"
  TOTAL="$(python3 -I -c 'import sys; print(round(float(sys.argv[1]) + float(sys.argv[2]), 2))' "$TOTAL" "$cost" < /dev/null)"
done <<EOF
$STEPS
EOF

[ -n "$SELECTED" ] || die "nothing selected (check --only / --from / --tier)"

echo "Project:  $FANTASY"
echo "Mode:     $([ "$DRY" = 1 ] && echo 'dry run (no spend)' || echo 'RENDER')"
echo "Steps:"
printf '%s' "$SELECTED" | while IFS='|' read -r name tier kind dest cost; do
  [ -n "$name" ] && printf '  tier %s  %-6s %-28s $%s\n' "$tier" "$kind" "$name" "$cost"
done
echo "Estimated spend if everything renders: \$$TOTAL (each 30 s job holds ~\$4.40 while in flight; refused jobs are not billed)"

if [ "$DRY" = 0 ] && [ "$YES" = 0 ]; then
  printf 'Proceed? [y/N] '
  read -r answer
  case "$answer" in y|Y|yes|YES) ;; *) echo "Nothing spent."; exit 0 ;; esac
fi

# --- run --------------------------------------------------------------------------------------------
STEPFILE="$LOGDIR/.selected_steps"
printf '%s' "$SELECTED" > "$STEPFILE"
while IFS='|' read -r name tier kind dest cost; do
  [ -z "$name" ] && continue
  shot="pika/shots/$name.json"
  slug="$(json_field "$shot" slug)" || die "cannot read $shot"
  log="$LOGDIR/$name.log"
  echo ""
  echo "== $name  ($kind, tier $tier)"

  if [ "$DRY" = 1 ]; then
    miss="$(missing_refs "$shot")"
    if [ -n "$miss" ]; then
      echo "   not validated yet; it waits on files a plate step will create:"
      printf '%s\n' "$miss" | sed 's/^/     /'
      continue
    fi
    node pika/run-shot.js "$shot" --dry-run > "$log" 2>&1 < /dev/null
    echo "   dry-run exit $? (log: $log)"
    tail -n 3 "$log" | sed 's/^/   | /'
    continue
  fi

  if [ "$kind" = plate ] && [ -f "$dest" ]; then
    echo "   $dest already exists; skipping (delete it to rebuild the plate)"
    continue
  fi
  if [ "$kind" = video ] && ls out/"$slug".mp4 >/dev/null 2>&1; then
    echo "   out/$slug.mp4 already exists; skipping (delete it to re-render)"
    continue
  fi
  miss="$(missing_refs "$shot")"
  if [ -n "$miss" ]; then
    echo "   missing reference files; render the plate steps first:"
    printf '%s\n' "$miss" | sed 's/^/     /'
    exit 1
  fi

  node pika/run-shot.js "$shot" > "$log" 2>&1 < /dev/null
  code=$?
  if grep -q "insufficient_balance" "$log"; then
    echo "   STOPPED: insufficient balance (not billed). Top up at https://dev.pika.art/dashboard, then:"
    echo "     $0 --from $name --tier $TIER"
    exit 2
  fi
  if ! grep -q "saved:" "$log"; then
    echo "   FAILED (exit $code). Last lines of $log:"
    tail -n 8 "$log" | sed 's/^/   | /'
    job="$(grep -o 'media_[0-9a-fA-F-]\{8,\}' "$log" | tail -n 1)"
    if [ -n "$job" ]; then
      echo "   The job may still be running on the server (a network drop is not a failed job, §203). Recover with:"
      echo "     node pika/run-shot.js --recover $job $slug"
    fi
    echo "   Resume with: $0 --from $name --tier $TIER"
    exit 1
  fi
  grep "saved:" "$log" | tail -n 1 | sed 's/^/   /'
  if [ "$kind" = plate ]; then
    promote_plate "$slug" "$dest" || die "plate rendered but could not be promoted to $dest"
    if [ "$YES" = 0 ]; then
      command -v open >/dev/null 2>&1 && open "$dest" 2>/dev/null
      printf '   Does the plate match the sheet (face, costume, frost only on her/him)? Continue? [y/N] '
      ok=""
      if ! { read -r ok < /dev/tty; } 2>/dev/null; then
        echo ""
        echo "   No terminal to answer on, so stopping here before any scene spends money."
        echo "   Check $dest yourself. If it is right, continue with (the plate step will be skipped):"
        echo "     $0 --from $name --tier $TIER"
        echo "   If it is wrong, delete it, adjust tools/build_shots.py, rebuild, and run the same command."
        exit 3
      fi
      case "$ok" in
        y|Y|yes|YES) ;;
        *) rm -f "$dest"
           echo "   Stopped before spending on scenes. The plate was removed so the next run rebuilds it (~\$0.10)."
           echo "   Adjust tools/build_shots.py if needed, rebuild, then: $0 --from $name --tier $TIER"
           exit 3 ;;
      esac
    fi
  fi
done < "$STEPFILE"
rm -f "$STEPFILE"

echo ""
if [ "$DRY" = 1 ]; then
  echo "Dry run finished. Files that wait on a plate are validated during the real run."
else
  echo "Done. New renders are in $FANTASY/out/ (logs in $LOGDIR)."
  echo "Cut list and edit order: $HERE/EP2_STORY_ANALYSIS.md section 7, scene pages in EP2_REPLACEMENT_SCENES.md."
  echo "Verify each render as usual: 1 fps contact sheet + windowed transcription (10-14 s windows, §48)."
fi
