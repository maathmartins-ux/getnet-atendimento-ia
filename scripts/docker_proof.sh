#!/usr/bin/env bash
# Prova de produção no ambiente de construção: sobe o serviço do Docker se ele estiver parado, constrói a imagem, testa
# (sem pacotes de dev, /health com dados, eval via HTTP, MCP com JWT, container sem rede, 2 réplicas) e grava
# docs/DOCKER.md com o commit testado e a tabela de etapas. Por quê: a imagem é provada no próprio ambiente em que o
# código foi construído, não só na CI, e o resultado fica no repositório para quem não abre o Actions.
# Uso: scripts/docker_proof.sh   (~9 min; rode em segundo plano)
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p var docs
if ! docker info >/dev/null 2>&1; then
  (dockerd >var/dockerd.log 2>&1 &)
  for _ in $(seq 1 30); do docker info >/dev/null 2>&1 && break; sleep 1; done
fi
docker info >/dev/null 2>&1 || { echo "sem Docker neste ambiente: nada gravado" >&2; exit 2; }
sha=$(git rev-parse --short HEAD 2>/dev/null || echo "sem-git")
dirty=$(git status --porcelain 2>/dev/null | grep -v -e '^?? var/' -e 'docs/DOCKER.md' | head -1 || true)
set +e
python scripts/check.py --part docker --docker --scale >var/docker_check.log 2>&1
rc=$?
set -e
table=$(sed -n '/^| etapa |/,/^$/p' var/docker_check.log)
size=$(docker image ls app-check --format '{{.Size}}' 2>/dev/null | head -1)
{
  echo "# Imagem construída e testada no ambiente de construção"
  echo
  echo "Gerado por \`scripts/docker_proof.sh\` em $(date -u +%Y-%m-%dT%H:%MZ), commit \`${sha}\`${dirty:+ (árvore com mudanças)};"
  echo "Docker $(docker version --format '{{.Server.Version}}' 2>/dev/null); imagem ${size:-?}. Resultado: $([ $rc -eq 0 ] && echo VERDE || echo VERMELHO)."
  echo
  echo "$table"
  echo
  echo "O mesmo teste roda na CI (job \`check (docker)\`); este arquivo é a prova para quem lê o repositório sem abrir o Actions."
} >docs/DOCKER.md
echo "gravado docs/DOCKER.md (rc=$rc)"
exit $rc
