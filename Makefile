# Atalhos para Linux/CI. No Windows, rode os comandos python diretamente (ou scripts/live_eval.ps1).
.PHONY: check check-docker docker-proof eval gate compare live judge readme up scale video deliver final

check:
	python scripts/check.py

check-docker:
	python scripts/check.py --docker

# prova no ambiente de construção: sobe o Docker se parado, testa a imagem e grava docs/DOCKER.md
docker-proof:
	scripts/docker_proof.sh

# eval: o que roda a cada mudança (gate offline + ablação do replanejamento). A comparação de buscadores (8 min
# medidos num corpus real) é decisão à parte, tomada antes: `make compare`.
eval:
	python -m evals.run_evals
	python -m evals.run_evals --ablate-replan

# gate: o gate offline inteiro, na ordem certa e com os commits que ele pede (o `make eval` recusa árvore suja nos
# arquivos que o gate lê; `git commit -- <arquivo>` leva só aquele arquivo, nunca as remoções da preparação).
# 1. limiar do portão calibrado no corpus → commit; 2. buscador medido no domínio (offline; --keep-default mantém o
# padrão do kit) → commit; 3. make eval + official_check verdes → commit do resultado. Para no 1º vermelho.
CALIBRATION := src/app/domain/challenge/__init__.py
RETRIEVER := data/retriever.json evals/results/retrieval_compare.json
GATE_RESULTS := evals/results/latest.json evals/results/ablation_replan.json
gate:
	python -m evals.run_evals --calibrate-gate --apply
	git add -- $(CALIBRATION)
	git diff --cached --quiet -- $(CALIBRATION) || git commit -q -m "gate: limiar do portão calibrado" -- $(CALIBRATION)
	python -m evals.run_evals --choose-retriever --fast --keep-default --apply
	git add -- $(RETRIEVER)
	git diff --cached --quiet -- $(RETRIEVER) || git commit -q -m "busca: buscador medido no domínio" -- $(RETRIEVER)
	$(MAKE) eval
	python scripts/official_check.py
	git add -- $(GATE_RESULTS)
	git diff --cached --quiet -- $(GATE_RESULTS) || git commit -q -m "gate: eval offline e oficiais conferidos" -- $(GATE_RESULTS)
	@echo "GATE COMMITADO $$(git rev-parse --short HEAD)"

compare:
	python -m evals.run_evals --compare-retrievers

live:
	python -m evals.run_evals --live --max-usd $${MAX_USD:-3} --workers 4

judge:
	LLM_PROVIDER=anthropic python -m evals.judge --max-usd $${MAX_USD:-1}

readme:  # só o README a partir dos resultados commitados (refazer o eval é `make eval`)
	python scripts/fill_readme.py

up:
	docker compose up -d --build

scale:
	python scripts/scale_smoke.py

video:
	scripts/video/make_video.sh

# deliver: o fim em um comando. DEMO dos oficiais → commit só dele → scripts/final.sh, que já gera FAILURE_MODES,
# TIMESHEET e a mensagem de entrega e faz o último commit (README) com push. A prova da imagem
# (scripts/docker_proof.sh, ~9 min) roda no início e a CI do commit final a refaz; para refazê-la aqui também, com
# Docker local: DOCKER_PROOF=1 make deliver. Fim da linha do tempo antes do último commit: CLOCK_END=<sha> make deliver.
deliver:
	python scripts/demo_md.py
	git add -- docs/DEMO.md
	git diff --cached --quiet -- docs/DEMO.md || git commit -q -m "demo: respostas reais dos oficiais" -- docs/DEMO.md
	if [ "$${DOCKER_PROOF:-0}" = 1 ]; then scripts/docker_proof.sh && git add -- docs/DOCKER.md && \
	  { git diff --cached --quiet -- docs/DOCKER.md || git commit -q -m "docker: imagem testada" -- docs/DOCKER.md; }; fi
	scripts/final.sh

final:
	scripts/final.sh
