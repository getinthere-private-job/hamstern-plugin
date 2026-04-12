#!/usr/bin/env bash
set -euo pipefail

# hamstern Dashboard スキル
# cmux dashboard --port <포트> --open 실행

PORT=${1:-7777}
NO_OPEN=${NO_OPEN:-}

# 포트 파싱
while [[ $# -gt 0 ]]; do
  case "$1" in
    --port)
      PORT="$2"
      shift 2
      ;;
    --no-open)
      NO_OPEN=1
      shift
      ;;
    *)
      shift
      ;;
  esac
done

echo "🚀 Starting Hamstern Dashboard on port $PORT..."

# cmux 바이너리 찾기
CMUX_BIN=""
if [[ -x "/Applications/cmux.app/Contents/Resources/bin/hamstern" ]]; then
  CMUX_BIN="/Applications/cmux.app/Contents/Resources/bin/hamstern"
elif [[ -x "/Applications/cmux.app/Contents/Resources/bin/cmux" ]]; then
  CMUX_BIN="/Applications/cmux.app/Contents/Resources/bin/cmux"
elif command -v cmux &>/dev/null; then
  CMUX_BIN="cmux"
else
  echo "❌ Error: cmux binary not found"
  echo "Make sure hamstern app is installed in /Applications/cmux.app"
  exit 1
fi

echo "📦 Using: $CMUX_BIN"

# 포트 빈 상태 확인
if netstat -an 2>/dev/null | grep -q "\.${PORT}\s.*LISTEN"; then
  echo "❌ Error: Port $PORT is already in use"
  echo "Try a different port: --port 8080"
  exit 1
fi

# 대시보드 서버 시작
if [[ -z "$NO_OPEN" ]]; then
  echo "🌐 Opening http://localhost:$PORT in browser..."
  "$CMUX_BIN" dashboard --port "$PORT" --open
else
  echo "✅ Dashboard running at http://localhost:$PORT"
  echo "   (not opening browser with --no-open)"
  "$CMUX_BIN" dashboard --port "$PORT"
fi
