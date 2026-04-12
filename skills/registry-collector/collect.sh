#!/usr/bin/env bash
set -euo pipefail

# Registry Collector 스킬
# GitHub 큐레이션 소스에서 실제 Claude Code 스킬/플러그인 수집 (증분 업데이트)

REGISTRY_FILE="$HOME/.hamstern/skills-registry.json"
TEMP_REGISTRY=$(mktemp)
trap "rm -f $TEMP_REGISTRY" EXIT

mkdir -p "$HOME/.hamstern"

# GitHub API 호출 (GITHUB_TOKEN 지원)
github_api() {
  local url="$1"
  if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    curl -sf \
      -H "Accept: application/vnd.github.v3+json" \
      -H "Authorization: Bearer $GITHUB_TOKEN" \
      "$url" 2>/dev/null || return 1
  else
    curl -sf \
      -H "Accept: application/vnd.github.v3+json" \
      "$url" 2>/dev/null || return 1
  fi
}

# jq로 JSON entry 안전하게 생성
build_entry() {
  local id="$1" provider="$2" name="$3" description="$4"
  local category="$5" icon="$6" github_repo="$7"
  local stars="${8:-0}" popularity="${9:-0.5}"

  jq -n \
    --arg id          "$id" \
    --arg provider    "$provider" \
    --arg name        "$name" \
    --arg description "$description" \
    --arg category    "$category" \
    --arg icon        "$icon" \
    --arg github_repo "$github_repo" \
    --argjson stars   "$stars" \
    --argjson popularity "$popularity" \
    '{
      id: $id,
      provider: $provider,
      name: $name,
      description: $description,
      category: $category,
      icon: $icon,
      github_repo: $github_repo,
      github_stars: $stars,
      popularity_score: $popularity
    }' 2>/dev/null || echo "{}"
}

# popularity 점수 계산 (0.0~1.0)
calc_popularity() {
  local stars="$1"
  local max_stars="${2:-200000}"

  jq -n \
    --argjson stars "$stars" \
    --argjson max_stars "$max_stars" \
    'if $max_stars == 0 then 0.5 else
      (($stars / $max_stars) | if . > 1 then 1 else . end) as $norm |
      ($norm * 0.8 + 0.1) as $score |
      if $score < 0 then 0 elif $score > 1 then 1 else $score end
    end | (. * 100 | round) / 100' 2>/dev/null || echo 0.5
}

# awesome-claude-code README 파싱 (GitHub API 호출 없음)
collect_awesome() {
  echo "📚 awesome-claude-code 수집..."

  local readme
  readme=$(curl -sf "https://raw.githubusercontent.com/hesreallyhim/awesome-claude-code/main/README.md" 2>/dev/null) || {
    echo "   ⚠️  Failed to fetch README"
    return 1
  }

  # README에서 마크다운 링크 추출
  local count=0
  while IFS= read -r line; do
    # 마크다운 링크 매칭: - [name](url) ... - description
    if [[ "$line" == "- ["* ]] && [[ "$line" == *")"* ]]; then
      # 간단한 문자열 처리
      local name url desc
      # name: [ 다음부터 ] 전까지
      name="${line#*\[}"      # [ 제거
      name="${name%%\]*}"     # ] 이후 제거

      # url: ( 다음부터 ) 전까지
      url="${line#*\(}"       # ( 제거
      url="${url%%\)*}"       # ) 이후 제거

      # desc: - 다음부터 끝까지 (있으면)
      if [[ "$line" =~ " - "([^[].*) ]]; then
        desc="${BASH_REMATCH[1]}"
      else
        desc=""
      fi

      # GitHub 레포 URL만 처리
      if echo "$url" | grep -q "github.com"; then
        local github_repo
        github_repo=$(echo "$url" | sed 's|.*github.com/||' | sed 's|\.git$||')

        # category/icon 추론
        local category icon
        category="engineering-workflow"
        icon="⚡"
        [[ "$name" =~ debug|bug ]] && { category="debugging"; icon="🐛"; }
        [[ "$name" =~ test|tdd ]] && { category="testing"; icon="🧪"; }
        [[ "$name" =~ deploy|ship ]] && { category="deployment"; icon="🚀"; }
        [[ "$name" =~ review|audit ]] && { category="code-review"; icon="👀"; }
        [[ "$name" =~ plan|design ]] && { category="planning"; icon="📝"; }

        # GitHub API 없이 기본값 사용 (레이트 리밋 회피)
        local popularity=0.6

        local entry
        entry=$(build_entry \
          "awesome:${name// /-}" "awesome" "$name" "$desc" \
          "$category" "$icon" "$github_repo" "0" "$popularity")

        ALL_ENTRIES=$(echo "$ALL_ENTRIES" | jq --argjson e "$entry" '. + [$e]' 2>/dev/null || echo "[]")
        ((count++))
      fi
    fi
  done <<< "$readme"

  if [[ $count -eq 0 ]]; then
    echo "   ⚠️  No skills found (but README fetched)"
  else
    echo "   ✓ Added $count awesome skills"
  fi
}

# claude-plugins-official 수집
collect_official() {
  echo "🔌 anthropics/claude-plugins-official 수집..."

  local marketplace
  marketplace=$(curl -sf \
    "https://raw.githubusercontent.com/anthropics/claude-plugins-official/main/.claude-plugin/marketplace.json" 2>/dev/null) || {
    echo "   ⚠️  Failed to fetch marketplace.json"
    return 1
  }

  # 레포 메타데이터
  local repo_meta
  repo_meta=$(github_api "https://api.github.com/repos/anthropics/claude-plugins-official" 2>/dev/null) || {
    echo "   ⚠️  Failed to fetch repo meta"
    return 1
  }

  local repo_stars
  repo_stars=$(echo "$repo_meta" | jq -r '.stargazers_count // 0' 2>/dev/null || echo 0)

  # marketplace.json의 plugins[] 배열을 jq로 변환
  local entries count
  entries=$(echo "$marketplace" | jq \
    --arg repo "anthropics/claude-plugins-official" \
    --argjson stars "$repo_stars" \
    '[.plugins[]? | select(.name != null) | {
      id: ("official:" + .name),
      provider: "official",
      name: .name,
      description: (.description // ""),
      category: (.category // "productivity"),
      icon: "🔌",
      github_repo: $repo,
      github_stars: $stars,
      popularity_score: (if $stars == 0 then 0.5 else (($stars / 200000) | if . > 1 then 1 else . end) * 0.8 + 0.15 end)
    }]' 2>/dev/null) || {
    echo "   ⚠️  Failed to parse marketplace.json"
    return 1
  }

  if [[ -n "$entries" && "$entries" != "null" ]]; then
    count=$(echo "$entries" | jq 'length' 2>/dev/null || echo 0)
    if [[ $count -gt 0 ]]; then
      ALL_ENTRIES=$(echo "$ALL_ENTRIES" | jq --argjson e "$entries" '. + $e' 2>/dev/null || echo "[]")
      echo "   ✓ Added $count official plugins"
    fi
  fi
}

# claude-skill-registry JSON 수집
collect_registry() {
  echo "🎯 claude-skill-registry 수집..."

  local registry
  registry=$(curl -sf \
    "https://raw.githubusercontent.com/majiayu000/claude-skill-registry/main/registry.json" 2>/dev/null) || \
  registry=$(curl -sf \
    "https://majiayu000.github.io/claude-skill-registry-core/registry.json" 2>/dev/null) || {
    echo "   ⚠️  Failed to fetch registry"
    return 1
  }

  # skills[] 배열 변환 (원본 형식 유지)
  local entries count
  entries=$(echo "$registry" | jq \
    '[.[]? | select(.name != null) |
      {
        id: ("registry:" + (.id // .name // "unknown")),
        provider: "registry",
        name: .name // .id // "Unknown",
        description: .description // "",
        category: (.category // "engineering"),
        icon: (.icon // "⚡"),
        github_repo: (.repo // ""),
        github_stars: (.stars // 0),
        popularity_score: (if (.stars // 0) == 0 then 0.5 else ((.stars // 0) / 50000 | if . > 1 then 1 else . end) * 0.7 + 0.2 end)
      }
    ] | .[0:20]' 2>/dev/null) || {
    echo "   ⚠️  Failed to parse registry"
    return 1
  }

  if [[ -n "$entries" && "$entries" != "null" ]]; then
    count=$(echo "$entries" | jq 'length' 2>/dev/null || echo 0)
    if [[ $count -gt 0 ]]; then
      ALL_ENTRIES=$(echo "$ALL_ENTRIES" | jq --argjson e "$entries" '. + $e' 2>/dev/null || echo "[]")
      echo "   ✓ Added $count community skills"
    fi
  fi
}

# glama.ai MCP 서버 수집
collect_mcp() {
  echo "🤖 glama.ai MCP 서버 수집..."

  local mcp_list
  mcp_list=$(curl -sf "https://glama.ai/api/mcp/v1/servers?sort=popularity&limit=30" 2>/dev/null) || {
    echo "   ⚠️  Failed to fetch MCP servers"
    return 1
  }

  # servers[] 배열 변환
  local entries count
  entries=$(echo "$mcp_list" | jq \
    '[.servers[]? | select(.name != null) |
      {
        id: ("mcp:" + .name),
        provider: "mcp",
        name: .name,
        description: (.description // ""),
        category: "integration",
        icon: "🔗",
        github_repo: (.github_url // "" | gsub("https://github.com/"; "")),
        github_stars: (.github_stars // 0),
        popularity_score: ((.popularity_score // 0.5) | if . > 1 then 1 elif . < 0 then 0 else . end)
      }
    ]' 2>/dev/null) || {
    echo "   ⚠️  Failed to parse MCP servers"
    return 1
  }

  if [[ -n "$entries" && "$entries" != "null" ]]; then
    count=$(echo "$entries" | jq 'length' 2>/dev/null || echo 0)
    if [[ $count -gt 0 ]]; then
      ALL_ENTRIES=$(echo "$ALL_ENTRIES" | jq --argjson e "$entries" '. + $e' 2>/dev/null || echo "[]")
      echo "   ✓ Added $count MCP servers"
    fi
  fi
}

# 증분 업데이트 (기존 registry와 병합)
merge_incremental() {
  local new_entries="$1"

  # 기존 registry가 없으면 새 데이터 그대로
  [[ ! -f "$REGISTRY_FILE" ]] && { echo "$new_entries"; return; }

  local old_entries
  old_entries=$(cat "$REGISTRY_FILE" 2>/dev/null || echo "[]")

  # jq로 병합: new + old, id로 unique (new가 우선)
  jq -n \
    --argjson old "$old_entries" \
    --argjson new "$new_entries" \
    '($new + $old) | unique_by(.id)' 2>/dev/null || echo "$new_entries"
}

# 메인 로직
main() {
  echo "🔄 Collecting skill registry from curated sources..."
  echo ""

  # 모든 entry 배열 (메모리)
  ALL_ENTRIES="[]"

  # 각 소스에서 수집
  collect_awesome || true
  collect_official || true
  collect_registry || true
  collect_mcp || true

  # 중복 제거 (id 기준)
  ALL_ENTRIES=$(echo "$ALL_ENTRIES" | jq 'unique_by(.id)' 2>/dev/null || echo "[]")

  # 증분 업데이트: 기존 registry와 병합
  NEW_REGISTRY=$(merge_incremental "$ALL_ENTRIES")
  echo "$NEW_REGISTRY" > "$REGISTRY_FILE"

  echo ""
  echo "✅ Registry updated: $REGISTRY_FILE"

  # 통계 출력
  echo ""
  local total
  total=$(echo "$NEW_REGISTRY" | jq 'length' 2>/dev/null || echo 0)

  if [[ $total -gt 0 ]]; then
    echo "📊 Total skills: $total"

    # provider별 통계
    echo "$NEW_REGISTRY" | jq -r '[.[] | .provider] | group_by(.) | map({key: .[0], count: length}) | .[] | "\(.key): \(.count)"' 2>/dev/null | while read -r line; do
      if [[ -n "$line" ]]; then
        echo "   ├─ $line"
      fi
    done

    # popularity 통계
    local avg_pop max_pop
    avg_pop=$(echo "$NEW_REGISTRY" | jq '[.[] | .popularity_score // 0] | add / length | (. * 100 | round) / 100' 2>/dev/null || echo 0)
    max_pop=$(echo "$NEW_REGISTRY" | jq '[.[] | .popularity_score // 0] | max' 2>/dev/null || echo 0)
    echo "   └─ avg popularity: $avg_pop (max: $max_pop)"
  else
    echo "📊 Collected 0 skills (all sources failed)"
  fi
}

# 실행
main
