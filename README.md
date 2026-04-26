# 에이전트 4개 결과 종합

| 시나리오 | 핵심 | 점수 | 핵심 약점 |
|----------|------|------|-----------|
| A. Dashboard-centric | 대시보드로 가시성 해결 | 7/10 | `/hams:context` 수동 실행 — "볼 수 있다"와 "Claude가 안다"가 분리 |
| B. CLAUDE.md 자동 주입 | 새 세션 자동 복구 | 6/10 | 사용자가 볼 창문이 없음, 토큰 누수 |
| C. 멀티 Claude 통합 | 전체 파이프라인 구조 | 7.5/10 | mom MD 집계 주체 불명확, 충돌 감지 없음 |
| D. 최적 종합 | A+B+C 장점 통합 | 9/10 | 의미론적 충돌 감지 정확도 |

---

D의 핵심 원칙 (가장 중요한 발견)

"보이는 것 = 실제 주입되는 것"

- decisions.md → CLAUDE.md 자동 동기화
- 대시보드가 보여주는 것과 Claude가 읽는 것이 동일한 소스
- 수동 /hams:context 불필요

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

# 🔒 후크 활성화 조건 (`/hams:start`)

햄스턴 플러그인을 설치하면 3개의 후크 (`SessionStart`, `UserPromptSubmit`, `Stop`) 가 등록되지만, **프로젝트 루트에 `.hamstern/` 폴더가 있을 때만** 동작한다. 그 외 프로젝트에선 silent exit — 파일 생성·CLAUDE.md 수정·트랜스크립트 파싱 모두 스킵.

> **왜 이렇게?** Claude Code 플러그인 후크는 enable 시 모든 세션에서 발화하는 게 기본 동작 ([공식 docs](https://code.claude.com/docs/en/hooks.md)). 햄스턴과 무관한 프로젝트까지 `.hamstern/baby-hamster/` 같은 폴더가 생겨선 안 된다. 그래서 후크 자체가 self-gate.

## 사용법

| 명령 | 동작 |
|------|------|
| `/hams:start` | 현재 프로젝트에서 햄스턴 활성화 — `.hamstern/{baby,mom,boss}-hamster/` + `config.json` + `README.md` 생성 |
| `/hams:stop` | 일시 비활성 — `.hamstern/.disabled` 마커 생성 (데이터 보존) |
| `rm -rf .hamstern` | 완전 제거 (모든 데이터 삭제) |

```bash
# 새 프로젝트에서 햄스턴 사용 시작
cd ~/my-project
# Claude Code 세션에서:
/hams:start

# 잠깐 끄기 (데이터는 그대로)
/hams:stop

# 다시 켜기
/hams:start
```

## cmux 툴 (macOS) 과의 공존

햄스턴 본 도구 `cmux.app` (macOS) 가 실행 중이면 플러그인 후크는 **자동으로 양보**한다 (`.hamstern/.app-running` 마커 검사, 24시간 자동 만료). 즉:

- macOS 사용자가 cmux + 플러그인 둘 다 설치 — cmux 가 우선, 플러그인은 폴백
- Windows 사용자 — cmux 없으니 플러그인이 100% 처리

데이터·CLAUDE.md 가 두 군데서 동시에 쓰여 충돌하는 일 없음.

---

# /hams:diary — 로컬 마크다운으로 운영하는 개인 블로그

`로컬에서 마크다운으로 글을 쓰고`, 명령 하나로 **GitHub Pages 개인 블로그**에 정리·게시하는 도구. 강사·연구자·개발자가 자기 글을 한 곳에 모아 운영하기 좋다.

> 핵심 가치: **글은 로컬 `.md` 파일에 살아있고, 블로그는 그 출력물**. 자기 글을 자기 컴퓨터에서 통제하면서 GitHub Pages 의 무료 호스팅·CDN·이력 관리만 빌려 쓴다.

## Quick start (3 step)

```bash
# 1. 타겟 레포 한 번만 설정
/hams:diary config repo https://github.com/myuser/my-blog.git

# 2. 첫 글 게시 — 디자인 템플릿 + 블로그 제목을 묻고 빌드
/hams:diary publish ./hello-world.md 일상

# 3. 브라우저가 자동으로 http://localhost:8765 를 열어준다
#    → ✅ 게시 / ✏️ 수정 / ❌ 취소
```

## 3가지 명령

명령은 단순하다 — `publish`(게시) · `edit`(편집) · `config`(설정).

### `publish` — 글 올리기

```bash
/hams:diary publish {input} [category] [flags]
```

| input 형태 | 동작 |
|-----------|------|
| `./post.md` | 마크다운 1개 |
| `./simulator.html` | HTML 1개 (라이트/다크 어댑터 자동 주입) |
| `./drafts/` | 폴더 안 모든 `.md`+`.html` 일괄 (중복 자동 skip) |
| `"*.md"` | 글롭 일괄 |
| `--rebuild all` | 로컬 원본 없이 사이트의 기존 글 재테마 |

**플래그**: `--no-theme` · `--overwrite` · `--draft` · `--preview-port N` · `--rebuild [slug\|all\|--category name]`

### `edit` — 글 고치기

```bash
/hams:diary edit {slug}
#  → 에디터로 _src/{slug}.{ext} 자동 오픈
#  → 미리보기 + 자동 재빌드 watcher
#  → 만족하면 ✅ 게시 / ❌ 취소
```

오타 1개 고치고 게시까지 30초.

### `config` — 설정 한 곳

```bash
/hams:diary config show                       # 현재 설정 보기
/hams:diary config repo {github-url}          # 타겟 레포 (1회 필수)
/hams:diary config template {1-5|name}        # 사이트 디자인 변경
/hams:diary config search {on|off}            # Pagefind 풀텍스트 검색
/hams:diary config comments {on|off}          # giscus 댓글 (on=대화형)
/hams:diary config blog-title "{제목}"        # 블로그 제목 변경
```

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
# 일기/노트 1개 게시
/hams:diary publish ./2026-04-26-회고.md 일상

# 인터랙티브 시뮬레이터 게시 (라이트/다크 어댑터 자동 주입)
/hams:diary publish ./sse-simulator.html 기술

# 폴더 일괄 게시 — 안에 있는 모든 .md/.html
/hams:diary publish ./drafts/ 일상

# 같은 폴더 다시 실행하면 중복은 자동 skip
# 한 개만 갱신하고 싶으면:
/hams:diary publish ./sse-simulator.html 기술 --overwrite

# 디자인을 노트북 스타일로 변경
/hams:diary config template notebook

# 푸시는 안 하고 워크트리만 남겨 직접 손보기
/hams:diary publish ./draft.md 일상 --draft

# ✏️ 기존 포스트 편집 — 에디터 자동 오픈 + 저장하면 즉시 재빌드
/hams:diary edit hello-world

# 검색·댓글 켜기 (opt-in)
/hams:diary config search on
/hams:diary config comments on   # 대화형 — giscus.app 의 4개 값 입력
```

> **편집 모드 전제**: 배포 시점에 원본을 `_src/{slug}.{ext}` 로 백업해 두는 포맷으로 게시된 포스트만 편집 가능. 옛 포맷 포스트는 `publish ... --overwrite` 로 한 번 재배포 후부터.

## 옛 명령어 호환

이전 플래그 형태도 그대로 인식된다 — 점진적 전환 위함.

| 옛 명령 | 새 명령 |
|---|---|
| `/hams:diary {file}` | `/hams:diary publish {file}` |
| `/hams:diary --edit {slug}` | `/hams:diary edit {slug}` |
| `/hams:diary --set-repo {url}` | `/hams:diary config repo {url}` |
| `/hams:diary --set-template {n}` | `/hams:diary config template {n}` |
| `/hams:diary --enable-search` / `--disable-search` | `/hams:diary config search {on\|off}` |
| `/hams:diary --enable-comments` / `--disable-comments` | `/hams:diary config comments {on\|off}` |
| `/hams:diary --rebuild-remote ...` | `/hams:diary publish --rebuild ...` |

## 🔍 검색 · 💬 댓글 (opt-in)

DB·서버 추가 없이 두 가지를 켤 수 있다. 둘 다 기본 OFF.

### 검색 (Pagefind)

빌드 시점에 모든 포스트의 풀텍스트 인덱스를 정적 파일(`pagefind/`)로 출력. 브라우저가 필요한 인덱스 조각만 fetch 해서 검색. **Algolia·Elasticsearch 같은 외부 서비스 불필요**.

```bash
/hams:diary config search on      # Node.js 18+ 필요 (npx pagefind 호출)
/hams:diary publish ./new.md 일상 # 다음 게시부터 모든 글이 인덱싱됨
```

홈 화면에 검색창이 자동으로 생기고, 본문 안 단어로 즉시 결과 매칭.

### 댓글 (giscus)

각 포스트가 GitHub Discussion 1개에 매핑. 학생이 GitHub 계정으로 댓글 달면 곧바로 Discussion 에 글이 쌓임. **Disqus 광고·자체 DB 불필요**.

설정 단계 (1회):
1. GitHub 레포에서 Discussions 활성화 (Settings → Features)
2. https://giscus.app 에서 [giscus app 설치 + 설정](https://giscus.app)
3. 페이지 하단의 `data-repo`, `data-repo-id`, `data-category`, `data-category-id` 4개 값 복사
4. `/hams:diary config comments on` 실행 → 4개 값 입력

이후 모든 포스트 하단에 giscus iframe 자동 임베드. 라이트/다크 토글 시 댓글 영역도 함께 변환.

```bash
/hams:diary config comments on    # 대화형 설정
/hams:diary config comments off   # 끄기 (이미 단 댓글은 GitHub 에 그대로 보존)
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

`~/.claude/hams:diary.json` 한 곳에 모든 설정이 저장된다.

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

---

## 📝 변경 내역 (Changelog)

> 버전 관리는 git commit SHA 로 한다 (`/plugin update hams` 가 매 커밋마다 새 버전으로 인식). 아래는 사용자 관점의 굵직한 변화만 정리.

### 2026-04-26 — 후크 프로젝트 스코핑 + `/hams:start` · `/hams:stop`

- 후크 3종 (`SessionStart`, `UserPromptSubmit`, `Stop`) 가 `.hamstern/` 폴더 있는 프로젝트에서만 동작
- 그 외 프로젝트에선 silent exit — 의도치 않은 `.hamstern/baby-hamster/` 생성 / `CLAUDE.md` 수정 차단
- **`/hams:start`** 신규 — 현재 프로젝트에서 햄스턴 활성화 (`.hamstern/` 트리 + 메타 자동 생성)
- **`/hams:stop`** 신규 — 일시 비활성 (`.disabled` 마커. 데이터 보존)
- `SessionStart` 도 `.app-running` defer 추가 — cmux 툴과 공존 시 decisions.md 이중 주입 방지
- 19개 단위·통합 테스트 추가 (`hooks/test_gate.py`, `hooks/test_all_hooks_gated.py`)

### 2026-04-26 — 명령어 단순화 (3 서브명령 + 개인 블로그 프레이밍)

- 7~8 개 플래그 → **3개 서브명령**: `publish` · `edit` · `config`
  - `--set-repo`, `--set-template`, `--enable-search`, `--disable-search`, `--enable-comments`, `--disable-comments` → `config` 하나로 통합
  - `{file}/{dir}/{glob}` 모드 + `--rebuild-remote` → `publish` 하나로 통합
  - `--edit` → `edit`
- **옛 명령은 그대로 인식** (라우팅) — 점진적 전환 가능
- README · SKILL.md 의 프레이밍을 "강의자료 일괄 배포" → "**개인 블로그 운영**"으로 정정
  · 핵심 사용자: 강사·연구자·개발자가 자기 글을 한 곳에 모으는 것
  · 강의자료 배포는 그중 하나의 use case일 뿐
- 새 예시 블록: 일기/노트/시뮬레이터/검색·댓글 토글 — 강의 색채 줄이고 일반 블로깅 시나리오 강조

### 2026-04-26 — 검색·댓글 통합 (opt-in)

- `--enable-search` / `--disable-search` 추가 — Pagefind 풀텍스트 검색
  ```bash
  /hams:diary --enable-search
  /hams:diary ./new-post.md 강의   # 다음 배포부터 모든 포스트 자동 인덱싱
  ```
  홈에 검색창 자동 생성. Node.js 18+ 필요. DB 0개.
- `--enable-comments` / `--disable-comments` 추가 — giscus(GitHub Discussions) 댓글
  ```bash
  /hams:diary --enable-comments    # 대화형 — giscus.app 의 4개 data-* 값 입력
  ```
  포스트 하단에 자동 임베드. 라이트/다크 토글과 동기화.
- `~/.claude/hams:diary.json` 에 `features` 객체 추가 (`{search, comments}`).

### 2026-04-26 — HTML 시뮬레이터 양방향 톤 변환

- 빌드 시 원본 HTML 의 dominant background 를 자동 감지 (`data-osd-source-theme`)
- 다크 원본 → 라이트 모드, **라이트 원본 → 다크 모드** 모두 자동 변환 (이전엔 다크→라이트만)
- 톤이 같으면 필터를 적용하지 않아 원본 색상 보존

### 2026-04-26 — 편집 모드 (`--edit`)

- `/hams:diary --edit {slug}` 신설 — 기존 포스트 한 글자 고치는 데 30초
  ```bash
  /hams:diary --edit msa-k8s-websocket
  #  → 에디터로 _src/{slug}.{ext} 자동 오픈
  #  → 미리보기 서버 + 브라우저 자동 표시
  #  → 저장할 때마다 watcher 가 자동 재빌드 ([HH:MM:SS] rebuilt 출력)
  #  → 만족하면 ✅ 게시 / ❌ 취소
  ```
- 배포 시 원본을 `_src/{slug}.{ext}` 로 백업 (편집 모드의 진실의 원본)
- `posts.json` 에 `sourcePath` 필드 추가
- `watch_and_rebuild.py` helper 추가 (mtime polling)

### 2026-04-26 — 3가지 배포 모드 + 미리보기 승인 게이트 + 5템플릿 (대규모 재설계)

이전: MD 파일 1개를 즉시 push 하는 단방향 파이프라인.
이후:

- **3가지 입력 모드**: MD 1개 / HTML 시뮬레이터 1개 / 폴더·글롭 일괄
- **목업 → 승인 게이트**: 푸시 전 `python -m http.server 8765` + 브라우저 자동 오픈, ✅게시 / ✏️수정 / ❌취소 선택
- **5가지 디자인 템플릿**: `minimal`, `tech`(default), `lecture`, `notebook`, `magazine` — `--set-template {1-5|name}` 으로 변경
- **중복 자동 제외**: 배치 모드에서 같은 slug 는 skip (`--overwrite` 로 강제)
- **HTML 시뮬레이터 어댑터**: 풀-너비 + 라이트/다크 토글 + 플로팅 네비 바 자동 주입 (`--no-theme` 으로 끄기)
- **새 플래그**: `--no-theme`, `--overwrite`, `--draft`, `--preview-port`
- `inject_html_adapter.py` helper 추가 (HTML 빌드 책임 분리)
- 한글 파일명 처리: PowerShell `Get-ChildItem -LiteralPath` + ASCII slug 임시 복사 폴백

### 그 외

- `marketplace.json` 에 `./skills/diary` 등록 누락 수정
- SKILL.md 의 `name: hams-diary` → `name: diary` 정정 (플러그인 시스템이 자동으로 `hams-` prefix 추가)
- README 가 의사결정 분석 노트뿐이던 상태에서 `/hams:diary` 사용 가이드를 갖춘 본격 README 로 정리

---

## 향후 후보 (백로그)

- **시리즈 그룹핑** — `series` 필드로 강의 주차 묶음 자동 인덱스
- **공개 토글** — `published: false` 로 게시 후 미공개 (선공개 가능)
- **선수 학습 링크** — `prereq: ["slug"]` 로 다른 포스트 참조
- **slide 모드** — `?mode=slide` 발표용 풀스크린 변환
- **자동 ToC** — H2/H3 구조에서 우측 sticky 목차 (notebook 템플릿)
- **진도 추적·퀴즈** — 이 단계가 되면 비로소 Supabase 같은 DB 도입 정당화

자세한 향후 확장 백로그는 [`skills/diary/SKILL.md`](skills/diary/SKILL.md) 의 "강의자료 특화 향후 확장" 섹션 참조.
