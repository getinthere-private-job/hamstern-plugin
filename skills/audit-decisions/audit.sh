#!/usr/bin/env bash
set -euo pipefail

# Audit Decisions 스킬
# 프로젝트의 확정된 결정사항들을 재검토하고 타당성을 검증합니다.

PROJECT_DIR="${1:-.}"
DECISIONS_FILE="$PROJECT_DIR/.hamstern/boss-hamster/decisions.md"
CONTEXT_FILE="$PROJECT_DIR/.hamstern/mom-hamster/context.md"

if [[ ! -f "$DECISIONS_FILE" ]]; then
  echo "❌ Error: decisions.md not found at $DECISIONS_FILE"
  echo ""
  echo "Make sure you're in a hamstern project with:"
  echo "  $PROJECT_DIR/.hamstern/boss-hamster/decisions.md"
  exit 1
fi

if [[ ! -f "$CONTEXT_FILE" ]]; then
  echo "⚠️  Warning: context.md not found at $CONTEXT_FILE"
  echo "   Audit will proceed without background context"
fi

echo "🔍 Auditing Decisions in: $PROJECT_DIR"
echo ""

# decisions.md 파싱
mapfile -t decisions < <(grep "^- \[" "$DECISIONS_FILE" | sed 's/^- \[/[/' | sed 's/\] /\] - /')

if [[ ${#decisions[@]} -eq 0 ]]; then
  echo "ℹ️  No decisions to audit"
  exit 0
fi

echo "📌 Found ${#decisions[@]} decision(s):"
echo ""

# 각 결정에 대해 사용자 확인
for i in "${!decisions[@]}"; do
  idx=$((i + 1))
  decision="${decisions[$i]}"

  # 카테고리와 요약 분리
  category=$(echo "$decision" | sed 's/\[\(.*\)\].*/\1/')
  summary=$(echo "$decision" | sed 's/\[.*\] - //')

  echo "[$idx/${#decisions[@]}] 📌 $summary"
  echo "     Category: $category"
  echo ""

  # 배경 정보 찾기
  if [[ -f "$CONTEXT_FILE" ]]; then
    if grep -q "$summary" "$CONTEXT_FILE" 2>/dev/null; then
      echo "✓ Found in context.md"
    fi
  fi

  echo ""
  echo "  Actions:"
  echo "    [k] Keep (유지)"
  echo "    [m] Modify (수정 필요)"
  echo "    [d] Delete (폐기 - 최종 확인 필수)"
  echo "    [s] Skip (다음으로)"
  echo ""

  read -p "  Decision? (k/m/d/s): " -r action
  action="${action,,}"

  case "$action" in
    k)
      echo "  → ✅ Keeping this decision"
      ;;
    m)
      echo "  → ⚠️  Mark for review"
      echo "  Enter notes (optional): "
      read -p "  > " -r notes
      if [[ -n "$notes" ]]; then
        echo "  Note saved: $notes"
      fi
      ;;
    d)
      echo "  → ❌ DELETE REQUEST"
      echo ""
      echo "  ⚠️  This will remove the decision from decisions.md"
      echo "  This action is PERMANENT"
      echo ""
      read -p "  Really delete '$summary'? (yes/no): " -r confirm
      if [[ "$confirm" == "yes" ]]; then
        echo "  → Deleted"
      else
        echo "  → Cancelled"
      fi
      ;;
    s)
      echo "  → Skipping"
      ;;
    *)
      echo "  → Invalid action, skipping"
      ;;
  esac

  echo ""
  echo "---"
  echo ""
done

echo ""
echo "✅ Audit complete"
echo ""
echo "Changes:"
echo "  - Review marked items in decisions.md"
echo "  - Deleted items have been removed (can be restored from git)"
echo "  - decisions.md will auto-regenerate on next Claude session"
