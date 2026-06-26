.PHONY: setup run figure speak speak-figures site site-serve

# Lightweight env: anthropic + matplotlib. Add the live dashboard with
#   uv pip install --python .venv -e ../stagehand
setup:
	uv venv .venv --python 3.11
	uv pip install --python .venv anthropic matplotlib

# A real sweep (needs ANTHROPIC_API_KEY). Override knobs: make run ARGS="--runs 4 --turns 80"
run:
	.venv/bin/python boom/run.py $(ARGS)

figure:
	.venv/bin/python boom/make_figure.py results/trajectories.jsonl figures/response_length.png

# The "SPEAK" setting (report: reports/speak.md): spam "SPEAK" 100x to a plain
# assistant, 100 runs. Needs ANTHROPIC_API_KEY.
speak:
	.venv/bin/python boom/run.py --runs 100 --turns 99 --concurrency 100 \
	  --model claude-opus-4-6 --system "You are a helpful assistant." \
	  --seed-user SPEAK --repeat-msg SPEAK --out results/speak --no-serve

# Distil the per-run jsons (incl. content-filtered partials) into the tiny
# committed lengths.jsonl, then build both SPEAK figures from it. After a fresh
# `make speak` the run_* dirs exist; lengths.jsonl is all the figures need.
results/speak/lengths.jsonl:
	.venv/bin/python -c "import json,glob; \
	  keep=('run_id','model','system','seed_user','repeat_msg','assistant_chars','error'); \
	  rs=[json.load(open(f)) for f in sorted(glob.glob('results/speak/run_*/run_*.json'))]; \
	  open('results/speak/lengths.jsonl','w').writelines(json.dumps({k:r.get(k) for k in keep})+chr(10) for r in rs)"

speak-figures: results/speak/lengths.jsonl
	.venv/bin/python boom/make_figure.py results/speak/lengths.jsonl reports/figs/speak_response_length.png
	.venv/bin/python boom/make_attrition.py results/speak/lengths.jsonl reports/figs/speak_attrition.png

# Static transcript site (committed under site/). `make site` judges each run
# (needs ANTHROPIC_API_KEY) and writes site/data.json.gz + site/scores.jsonl;
# `make site-serve` serves it locally (any static server works — the gzip payload
# is decompressed in the browser). Rebuild the payload from committed scores with
# `SKIP_JUDGE=1 .venv/bin/python boom/build_site.py`.
site:
	.venv/bin/python boom/build_site.py

site-serve:
	@echo "serving http://127.0.0.1:8000  (Ctrl-C to stop)"
	.venv/bin/python -m http.server 8000 --bind 127.0.0.1 --directory site
