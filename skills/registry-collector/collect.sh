#!/usr/bin/env bash
set -euo pipefail

# Registry Collector 스킬
# GitHub과 MCP에서 스킬들을 수집하여 ~/.hamstern/skills-registry.json 생성

FORCE=${1:-}
REGISTRY_FILE="$HOME/.hamstern/skills-registry.json"
CACHE_FILE="$HOME/.hamstern/.registry-cache.json"
CACHE_AGE_LIMIT=$((24 * 60 * 60)) # 24시간

mkdir -p "$HOME/.hamstern"

# 캐시 확인
if [[ -f "$CACHE_FILE" && -z "$FORCE" ]]; then
  CACHE_AGE=$(($(date +%s) - $(stat -f%m "$CACHE_FILE" 2>/dev/null || echo 0)))
  if [[ $CACHE_AGE -lt $CACHE_AGE_LIMIT ]]; then
    echo "📦 Using cached registry ($(($CACHE_AGE / 60)) minutes old)"
    echo "   (Use --force to refresh)"
    cp "$CACHE_FILE" "$REGISTRY_FILE"
    exit 0
  fi
fi

echo "🔄 Collecting skill registry from GitHub and MCP..."
echo ""

# 임시 파일
TEMP_JSON=$(mktemp)
trap "rm -f $TEMP_JSON" EXIT

# JSON 시작
echo "[" > "$TEMP_JSON"

FIRST=1

# superpowers 스킬 수집
echo "📚 superpowers 스킬 수집..."
SUPERPOWERS_SKILLS=(
  "test-driven-development:🧪:TDD 워크플로우"
  "systematic-debugging:🐛:체계적 디버깅"
  "writing-plans:📝:구현 계획 작성"
  "executing-plans:⚙️:계획 실행"
  "brainstorming:💭:창의적 브레인스토밍"
  "verification-before-completion:✅:완료 검증"
  "requesting-code-review:👀:코드 리뷰 요청"
  "receiving-code-review:📖:코드 리뷰 피드백"
  "finishing-a-development-branch:🚀:개발 완료"
  "writing-skills:🎯:스킬 작성"
)

for skill_info in "${SUPERPOWERS_SKILLS[@]}"; do
  IFS=':' read -r skill_id icon desc <<< "$skill_info"

  if [[ $FIRST -eq 0 ]]; then
    echo "," >> "$TEMP_JSON"
  fi
  FIRST=0

  cat >> "$TEMP_JSON" <<EOF
  {
    "id": "superpowers:$skill_id",
    "provider": "superpowers",
    "name": "$(echo "$desc" | cut -d' ' -f1)",
    "description": "$desc",
    "category": "engineering-workflow",
    "icon": "$icon",
    "github_repo": "anthropics/claude-code",
    "github_stars": 0,
    "github_forks": 0,
    "installed": false,
    "popularity_score": 0.85
  }
EOF
done

# gstack 스킬들 (기본 목록)
echo "🏗️  gstack 스킬 수집..."
GSTACK_SKILLS=(
  "investigate:🔍:체계적 디버깅"
  "ship:🚀:배포 워크플로우"
  "design-review:🎨:디자인 검토"
  "qa:✅:QA 테스트"
  "health:📊:코드 품질 대시보드"
)

for skill_info in "${GSTACK_SKILLS[@]}"; do
  IFS=':' read -r skill_id icon desc <<< "$skill_info"

  echo "," >> "$TEMP_JSON"

  cat >> "$TEMP_JSON" <<EOF
  {
    "id": "gstack:$skill_id",
    "provider": "gstack",
    "name": "$(echo "$desc" | cut -d' ' -f1)",
    "description": "$desc",
    "category": "development",
    "icon": "$icon",
    "github_repo": "getinthere/gstack",
    "github_stars": 0,
    "github_forks": 0,
    "installed": false,
    "popularity_score": 0.75
  }
EOF
done

# MCP 스킬들
echo "🔗 MCP 서버 수집..."
MCP_SKILLS=(
  "filesystem:📁:File system operations"
  "postgres:🗄️:PostgreSQL database"
  "slack:💬:Slack integration"
)

for skill_info in "${MCP_SKILLS[@]}"; do
  IFS=':' read -r skill_id icon desc <<< "$skill_info"

  echo "," >> "$TEMP_JSON"

  cat >> "$TEMP_JSON" <<EOF
  {
    "id": "mcp:$skill_id",
    "provider": "mcp",
    "name": "$skill_id",
    "description": "$desc",
    "category": "integration",
    "icon": "$icon",
    "github_repo": "anthropics/mcp",
    "github_stars": 0,
    "github_forks": 0,
    "installed": false,
    "popularity_score": 0.70
  }
EOF
done

# JSON 종료
echo "" >> "$TEMP_JSON"
echo "]" >> "$TEMP_JSON"

# 파일 이동
mv "$TEMP_JSON" "$REGISTRY_FILE"

# 캐시도 저장
cp "$REGISTRY_FILE" "$CACHE_FILE"

echo ""
echo "✅ Registry saved to: $REGISTRY_FILE"
echo "   (Next update: 24 hours, or use --force)"

# 통계 출력
TOTAL=$(grep -c '"id":' "$REGISTRY_FILE" 2>/dev/null || echo 0)
echo ""
echo "📊 Collected $TOTAL skills:"
echo "   ├─ superpowers: $(grep -c '"superpowers' "$REGISTRY_FILE" 2>/dev/null || echo 0)"
echo "   ├─ gstack: $(grep -c '"gstack' "$REGISTRY_FILE" 2>/dev/null || echo 0)"
echo "   └─ mcp: $(grep -c '"mcp' "$REGISTRY_FILE" 2>/dev/null || echo 0)"
