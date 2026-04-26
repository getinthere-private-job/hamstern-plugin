# 에이전트 4개 결과 종합

| 시나리오 | 핵심 | 점수 | 핵심 약점 |
|----------|------|------|-----------|
| A. Dashboard-centric | 대시보드로 가시성 해결 | 7/10 | `/hams-context` 수동 실행 — "볼 수 있다"와 "Claude가 안다"가 분리 |
| B. CLAUDE.md 자동 주입 | 새 세션 자동 복구 | 6/10 | 사용자가 볼 창문이 없음, 토큰 누수 |
| C. 멀티 Claude 통합 | 전체 파이프라인 구조 | 7.5/10 | mom MD 집계 주체 불명확, 충돌 감지 없음 |
| D. 최적 종합 | A+B+C 장점 통합 | 9/10 | 의미론적 충돌 감지 정확도 |

---

D의 핵심 원칙 (가장 중요한 발견)

"보이는 것 = 실제 주입되는 것"

- decisions.md → CLAUDE.md 자동 동기화
- 대시보드가 보여주는 것과 Claude가 읽는 것이 동일한 소스
- 수동 /hams-context 불필요

구현 순서:

1. decisions.md → CLAUDE.md 자동 동기화 ← 이것만 해도 문제 1 해결
2. 대시보드 기본 뷰
3. 멀티 Claude 집계 + 충돌 UI

---

E (Claude 네이티브 멀티에이전트 비교) 완료되면 바로 드립니다.

● Agent "시나리오 E: Claude 멀티에이전트 공유 메모리와 비교" completed

● E도 완료됐습니다. 전체 결과 종합합니다.  
 --- E: Claude 네이티브 멀티에이전트 vs Hamstern

| 기준 | Hamstern | Claude 네이티브 |
|------|----------|-----------------|
| 지식 가시성 | 높음 (파일로 존재) | 낮음 (세션 내에만) |
| Compact 저항성 | 완전함 (파일시스템) | 없음 (세션 끝나면 사라짐) |
| 멀티 Claude 통합 | 비동기 가능 | 동시 실행 중에만 |
| 사용자 제어권 | 핀/제외로 명시적 | 오케스트레이터가 자동 결정 |
| 확장성 | 선형 (baby MD 하나 추가) | 오케스트레이터 병목 |

핵심 발견:

▎ Claude 네이티브는 "세션 내 협력" 문제를 풀고, Hamstern은 "세션 간 생존" 문제를 푼다.

경쟁이 아닙니다. Claude 팀즈로는 Hamstern이 해결하려는 문제를 대체할 수 없습니다. Claude는 자신의 컨텍스트 창 밖을 스스로 관리할 수 없기 때문입니다.

Anthropic이 왜 이 기능을 안 만들었나 — 부정적 시각:

1. 토큰 소비가 줄어들면 수익이 줄어든다  
   사용자가 매 세션마다 컨텍스트를 다시 설명하는 게 Anthropic 입장에서는 반복 과금입니다. 완벽한 프로젝트 메모리는 토큰 낭비를 제거하는데, 그게 곧 매출 감소입니다.

2. API 회사이지 개발 도구 회사가 아니다
   Claude Code는 부업입니다. 메인은 API 판매. 개발자 워크플로우 세밀한 부분은 "MCP 써서 니가 만들어라"로 책임을 생태계에 떠넘겼습니다.

3. Compact 자체가 비용 관리 도구다
   Compact는 "사용자 편의를 위한 기능"으로 포장됐지만, 본질은 무한정 늘어나는 컨텍스트 비용을 강제로 끊는 장치입니다. 여기에 영구 메모리를 붙이면 이 비용 통제가 무너집니다.

4. 멀티 Claude 시나리오는 설계 자체가 없다
   여러 Claude가 동시에 같은 프로젝트에서 일하는 시나리오를 Anthropic은 상상조차 안 했습니다. 그들의 멀티에이전트는 "오케스트레이터 1개 + 서브에이전트" 구조이고, 독립 인스턴스 간 지식 공유는 사각지대입니다.

결론: 클로드 팀즈는 "오케스트레이터가 살아있는 동안만" 공유라서, 세션 간 영구 생존 문제는 여전히 못 풀죠. Hamstern이 존재해야 하는 이유가 여기 있습니다.

---

# /hams-diary

로컬 마크다운(`.md`) 또는 인터랙티브 HTML 시뮬레이터(`.html`)를 GitHub Pages 블로그에 배포한다. 푸시 전에 로컬 미리보기 서버를 띄워 브라우저로 검수하고 사용자가 승인한 후에만 commit·push·merge 한다. **강의자료 일괄 배포에 최적화**.

## Quick start (3 step)

```bash
# 1. 타겟 레포 한 번만 설정
/hams-diary --set-repo https://github.com/myuser/my-blog.git

# 2. 첫 배포 — 디자인 템플릿(5개 중 선택) + 블로그 제목/소개를 묻고 빌드
/hams-diary ./lecture-week1.md 강의

# 3. 브라우저가 자동으로 http://localhost:8765 를 열어준다
#    → ✅ 게시 / ✏️ 수정 / ❌ 취소 중 선택
```

## 명령어

| 명령 | 동작 |
|------|------|
| `/hams-diary --set-repo {url}` | 타겟 GitHub Pages 레포 설정 (1회) |
| `/hams-diary --set-template {1-5\|name}` | 사이트 디자인 템플릿 변경 |
| `/hams-diary {file.md} [category]` | 마크다운 1개 배포 |
| `/hams-diary {file.html} [category]` | HTML 시뮬레이터 1개 배포 |
| `/hams-diary {dir/} [category]` | 폴더 일괄 배포 (`.md` + `.html`, 중복 자동 제외) |
| `/hams-diary "{glob}" [category]` | 글롭 일괄 배포 (예: `"*.html"`) |
| `/hams-diary --edit {slug}` | 기존 포스트 편집 — 에디터 자동 오픈 + 저장 시 자동 재빌드 |
| `/hams-diary --enable-search` | Pagefind 풀텍스트 검색 켜기 (opt-in) |
| `/hams-diary --disable-search` | 검색 끄기 |
| `/hams-diary --enable-comments` | giscus 댓글 켜기 — 대화형 설정 (opt-in) |
| `/hams-diary --disable-comments` | 댓글 끄기 |

## 플래그

| 플래그 | 효과 |
|--------|------|
| `--no-theme` | HTML 모드의 라이트/다크 어댑터 주입 끄기 (기본 ON) |
| `--overwrite` | 이미 존재하는 동일 slug 포스트 덮어쓰기 (기본 skip) |
| `--draft` | push 하지 않고 워크트리만 남겨 두기 |
| `--preview-port N` | 미리보기 서버 포트 변경 (기본 `8765`) |

## 5가지 사이트 디자인 템플릿

| # | name | 톤 | 적합한 콘텐츠 |
|---|------|-----|---------------|
| 1 | `minimal` | 흰 배경 · 세리프 · 단일 컬럼 | 텍스트 노트, 에세이 |
| 2 | `tech` (default) | 다크 히어로 · 그라데이션 카드 · 카테고리 필터 | 시뮬레이터 · 도식 · 도구 |
| 3 | `lecture` | 주차/회차 번호 · 사이드 목차 | 정규 강의 시리즈 |
| 4 | `notebook` | Jupyter풍 좌측 TOC · monospace 헤딩 | 튜토리얼 · 실습 |
| 5 | `magazine` | 큰 히어로 · 에디토리얼 그리드 · 세리프 | 포트폴리오 · 쇼케이스 |

## 동작 흐름

```
인자 파싱
   ↓
레포 clone/pull → 워크트리 생성
   ↓
(첫 배포면) 템플릿 복사 + {{BLOG_*}} 치환
   ↓
posts.json 갱신 (중복은 skip / --overwrite 면 교체)
   ↓
MD → HTML 변환  /  HTML → 어댑터 주입
   ↓
─────────────  여기까지 로컬, push 0회  ─────────────
   ↓
python -m http.server 8765 (백그라운드)
   ↓
기본 브라우저 자동 오픈 → http://localhost:8765
   ↓
"이 모습으로 게시할까요?"
   ✅ 게시 → commit · push · PR · squash merge → 워크트리 정리
   ✏️ 수정 → 피드백 받아 재빌드 (또는 워크트리 안내 후 종료)
   ❌ 취소 → 서버 종료 + 워크트리·브랜치 삭제 + 종료
```

## 자주 쓰이는 예시

```bash
# 강의 노트 1개 게시 (마크다운)
/hams-diary ./MSA-1주차.md MSA강의

# 인터랙티브 시뮬레이터 1개 게시 (라이트/다크 어댑터 자동 주입)
/hams-diary ./sse-simulator.html 분산시스템

# 강의자료 폴더 일괄 게시 — 7개 시뮬레이터를 한 번에
/hams-diary "C:/Users/me/lecture-files/" MSA강의

# 같은 폴더를 다시 실행하면 중복은 자동 skip
# 한 개만 갱신하고 싶으면 --overwrite + 단일 파일
/hams-diary ./sse-simulator.html 분산시스템 --overwrite

# 디자인 템플릿을 강의용으로 변경
/hams-diary --set-template lecture

# 푸시는 안 하고 워크트리만 남겨 직접 손보기
/hams-diary ./draft.md 강의 --draft

# ✏️ 기존 포스트 편집 — 에디터로 자동 오픈, 저장하면 즉시 재빌드
/hams-diary --edit msa-k8s-websocket
#  → 기본 에디터에서 _src/msa-k8s-websocket.html 열림
#  → 브라우저는 http://localhost:8765/posts/msa-k8s-websocket.html 자동 표시
#  → 에디터에서 저장할 때마다 watcher 가 재빌드 ([HH:MM:SS] rebuilt 출력)
#  → F5 로 변경 확인 → 만족하면 ✅ 게시 / ❌ 취소
```

> **편집 모드 전제**: 배포 시점에 원본을 `_src/{slug}.{ext}` 로 백업해 두는 v2+ 포맷으로 게시된 포스트만 편집 가능하다. v1 시절(이전) 포스트는 `--overwrite` 로 한 번 재배포 후부터 편집 모드 사용 가능.

## 🔍 검색 · 💬 댓글 (opt-in)

DB·서버 추가 없이 두 가지를 켤 수 있다. 둘 다 기본 OFF.

### 검색 (Pagefind)

빌드 시점에 모든 포스트의 풀텍스트 인덱스를 정적 파일(`pagefind/`)로 출력. 브라우저가 필요한 인덱스 조각만 fetch 해서 검색. **Algolia·Elasticsearch 같은 외부 서비스 불필요**.

```bash
/hams-diary --enable-search   # Node.js 18+ 필요 (npx pagefind 호출)
/hams-diary ./new-post.md 강의   # 다음 배포부터 모든 포스트가 인덱싱됨
```

홈 화면에 검색창이 자동으로 생기고, 본문 안 단어로 즉시 결과 매칭.

### 댓글 (giscus)

각 포스트가 GitHub Discussion 1개에 매핑. 학생이 GitHub 계정으로 댓글 달면 곧바로 Discussion 에 글이 쌓임. **Disqus 광고·자체 DB 불필요**.

설정 단계 (1회):
1. GitHub 레포에서 Discussions 활성화 (Settings → Features)
2. https://giscus.app 에서 [giscus app 설치 + 설정](https://giscus.app)
3. 페이지 하단의 `data-repo`, `data-repo-id`, `data-category`, `data-category-id` 4개 값 복사
4. `/hams-diary --enable-comments` 실행 → 4개 값 입력

이후 모든 포스트 하단에 giscus iframe 자동 임베드. 라이트/다크 토글 시 댓글 영역도 함께 변환.

```bash
/hams-diary --enable-comments       # 대화형 설정
/hams-diary --disable-comments      # 끄기 (이미 단 댓글은 GitHub 에 그대로 보존)
```

### 의존성 한눈에

| 기능 | 추가 필요 |
|------|-----------|
| 검색 | Node.js 18+ (브라우저 측은 0 dep) |
| 댓글 | GitHub Discussions 활성화 + giscus 앱 설치 |

## HTML 시뮬레이터에 주입되는 것

다크 전용으로 작성된 HTML 시뮬레이터도 그대로 던져넣으면 다음이 자동 처리된다.

- **풀 너비** — `max-width` 제약 제거 → 시뮬레이션이 화면 전체 사용
- **라이트/다크 토글** — `localStorage('blog-theme')` 으로 블로그 테마와 동기화
- **원본 톤 자동 감지** — 빌드 시점에 원본 HTML 의 dominant background 를 보고 `light` / `dark` 로 분류 (`data-osd-source-theme`). 라이트 톤 원본(예: 베이지)도 자동 인식
- **양방향 변환** — 원본 톤과 사용자 선택 테마가 다를 때만 `filter: invert + hue-rotate` 적용. 다크 원본 ↔ 라이트 모드, 라이트 원본 ↔ 다크 모드 모두 자동 변환되고, 톤이 같으면 원본 색상 그대로 유지 (이미지/SVG/캔버스는 역-필터로 원색 유지)
- **상단 플로팅 바** — `← 목록`, `테마` 토글 버튼 (`z-index: 2147483647`)

원본 그대로 배포하고 싶다면 `--no-theme` 사용.

## 설정 파일

`~/.claude/hams-diary.json` 한 곳에 모든 설정이 저장된다.

```json
{
  "repo": "https://github.com/myuser/my-blog.git",
  "template": "tech",
  "pagesUrl": "https://mycustom.domain/"
}
```

`pagesUrl` 은 선택 — 비워두면 `https://{owner}.github.io/{repo}/` 로 자동 추론.

## 더 자세한 동작·확장 백로그

전체 내부 체크리스트, 에러 처리, 강의자료 향후 확장 항목(시리즈 그룹핑·공개 토글·선수 학습 링크·slide 모드·자동 ToC·댓글) 은 [`skills/diary/SKILL.md`](skills/diary/SKILL.md) 참조.
