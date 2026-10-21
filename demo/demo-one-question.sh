#!/usr/bin/env bash
# Demonstration for the video: one call, the returned SQL, the sandbox value,
# the verdict, then the vote on the same question.
#
#   bash demo/demo-one-question.sh            # live: ONE real call to groq:openai/gpt-oss-120b on C10
#   bash demo/demo-one-question.sh --replay   # offline: re-runs the stored SQL of traces-td1.jsonl (nature = replay)
#
# Live mode writes to demo/ (separate experiment files, outside the TD 1 batch);
# delete demo/state-demo.jsonl to make a new call. Keys come from the environment.
set -euo pipefail
cd "$(dirname "$0")/.."
CASE=${CASE:-C10}
MODEL=${MODEL:-groq:openai/gpt-oss-120b}

if [[ "${1:-}" == "--replay" ]]; then
  rm -f demo/state-replay.jsonl
  python3 skeleton-multi-llm-en.py --replay traces-td1.jsonl --models "$MODEL" --cases "$CASE" \
    --state demo/state-replay.jsonl --out demo/traces-replay.csv
  STATE=demo/state-replay.jsonl
else
  python3 skeleton-multi-llm-en.py --run --models "$MODEL" --cases "$CASE" \
    --state demo/state-demo.jsonl --out demo/traces-demo.csv
  STATE=demo/state-demo.jsonl
fi

echo; echo "=== Returned SQL, sandbox value, verdict ($STATE, last line)"
python3 - "$STATE" <<'PY'
import json, sys
t = [json.loads(l) for l in open(sys.argv[1]) if l.strip()][-1]
for k in ("nature", "cell_id", "prompt_sha256", "http_status", "sql", "value", "reference", "verdict", "verdict_detail",
          "latency_ms", "tokens_prompt", "tokens_completion", "date_utc"):
    print(f"{k:18} {t[k]}")
PY

echo; echo "=== 2-of-3 vote on $CASE from the TD 1 traces (nature = real)"
python3 atelier-vote.py --traces traces-td1.csv --case "$CASE"
