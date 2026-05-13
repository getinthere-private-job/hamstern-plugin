---
name: diary
description: |
  로컬에서 작성한 마크다운(.md) 혹은 HTML을 GitHub Pages 개인 블로그에 정리하는 도구.
  배포 전 로컬 미리보기 서버로 검수하고 승인 후에만 푸시한다.
  강사·연구자·개발자가 자기 글을 한 곳에 모아 운영하기 좋다.
  사용법:
    /hams:diary publish {file|dir|glob} [category]   # 게시 (단일/일괄 자동 감지)
    /hams:diary edit {slug|id}                        # 편집
    /hams:diary delete {title|id}                     # 삭제 (제목 유사도/숫자 ID)
    /hams:diary config <subcommand>                   # 설정 (프로파일 포함)
    /hams:diary option                                # 한 화면 사용법
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - AskUserQuestion
  - PowerShell
---

# /hams:diary

로컬에서 작성한 마크다운·HTML 파일을 **GitHub Pages 개인 블로그**에 정리·게시하는 도구. 글쓰기는 익숙한 에디터에서 하고, 정리·배포·검수만 자동화한다.

## 핵심 가치

1. **로컬 우선** — 글은 자기 컴퓨터의 `.md` 파일로 살아있고, 블로그는 그 출력물.
2. **목업 후 게시** — 로컬에서 미리보기 서버 → 브라우저 검수 → 승인 → push.
3. **5가지 디자인** — `minimal` / `tech` / `lecture` / `notebook` / `magazine` 중 한 줄 명령으로 변경.
4. **DB 없이 풍부한 기능** — 검색(Pagefind, 기본 ON) · 라이트/다크 자동 변환 · 한글 파일명 안전 처리.
5. **숫자 ID URL** — 각 글은 `/posts/{id}/{slug}.html` (자동 1, 2, 3…) 로 게시돼 짧고 안정적.

---

## 사용 방법

명령은 5개의 서브명령으로 통합되어 있다 — `publish` · `edit` · `delete` · `config` · `option`.

### `publish` — 글 올리기

```bash
/hams:diary publish {input} [category] [flags]

# input 자동 감지
/hams:diary publish ./post.md 일상           # 단일 마크다운
/hams:diary publish ./simulator.html 강의    # 단일 HTML
/hams:diary publish ./drafts/ 일상           # 폴더 일괄 (.md + .html)
/hams:diary publish "*.md" 일상              # 글롭 일괄
/hams:diary publish --rebuild all            # 로컬 원본 없이 사이트 글 재테마

# 플래그
--no-theme                              # HTML 어댑터 주입 끄기 (라이트/다크 변환 OFF, 폭은 native)
--overwrite                             # 기존 동일 글 덮어쓰기 (originalFilename → slug → 제목 매칭)
--draft                                 # 푸시 안 하고 워크트리만 남김
--preview-port N                        # 미리보기 포트 (기본 8765)
--rebuild [slug|all|--category name]    # 사이트 기존 글 재테마/재시그니처
--profile {name}                        # 1회 임시 프로파일 override (active 변경 안 함)
--fit-viewport                          # 시뮬레이터 max-width 풀어서 viewport 채움 (반응형 시뮬레이터 권장)
--scale-up                              # CSS transform: scale 로 viewport 너비에 맞게 확대 (고정폭 시뮬레이터 권장)
```

> **시뮬레이터 폭 정책 (HTML 엔진 전용)** — 디폴트는 시뮬레이터 자체 `max-width` 보존 (가운데 정렬 또는 풀너비). `--fit-viewport` / `--scale-up` 은 상호 배타. 한 번 publish 시 선택한 모드는 `posts.json[].fit` 에 저장돼 다음 `--rebuild` 때 그대로 재현된다.

두 번째 위치 인자는 카테고리 (쉼표 구분 다중 가능). 비어있으면 AskUserQuestion `multiSelect: true` 로 선택받는다.

### `edit` — 글 고치기

```bash
/hams:diary edit {slug|id} [--profile {name}]
# slug 또는 숫자 ID (postId) 모두 가능
# → 에디터에서 _src/{slug}.{ext} 자동 오픈
# → 미리보기 서버 + 브라우저 자동 표시
# → 저장하면 watcher 가 자동 재빌드
# → ✅ 게시 / ❌ 취소
```

### `delete` — 글 삭제

```bash
/hams:diary delete {title|id} [--profile {name}] [--yes]

# 숫자 ID — 정확 매칭
/hams:diary delete 5                    # postId=5 인 글 삭제

# 제목 — 유사도 매칭
/hams:diary delete "MSA Kubernetes"     # title 부분일치/유사도 ≥0.5
                                        # 1건이면 확인 후 삭제
                                        # 다건이면 AskUserQuestion 으로 선택

# 플래그
--yes      # 확인 프롬프트 생략 (스크립트용)
--profile  # 임시 프로파일 override
```

삭제 흐름은 워크트리 → posts.json 에서 entry 제거 → `posts/{id}/{slug}.html` + 디렉토리 + `_src/{slug}.{ext}` 삭제 → pagefind 재빌드 → 미리보기 확인 → 승인 → commit + push. 자세한 흐름은 [🗑 삭제 모드](#-삭제-모드-delete) 참조.

### `config` — 설정 한 곳

```bash
# 활성 프로파일 갱신
/hams:diary config show                       # 활성 + 모든 프로파일 표시
/hams:diary config repo {github-url}          # 활성 프로파일의 타겟 레포
/hams:diary config template {1-5|name}        # 활성 프로파일 사이트 디자인
/hams:diary config search {on|off}            # Pagefind 검색 (기본 on)
/hams:diary config blog-title "{title}"       # 활성 프로파일 블로그 제목

# 프로파일 관리 (멀티 블로그 운영용)
/hams:diary config profile list                       # 등록된 프로파일 목록 + 활성 표시
/hams:diary config profile add {name} {repo-url}      # 신규 프로파일 등록
/hams:diary config profile use {name}                 # 활성 프로파일 전환
/hams:diary config profile remove {name}              # 프로파일 삭제
```

> 다른 톤의 블로그(예: 기술 / 일상 / 강의)는 **별도 프로파일 = 별도 레포**로 운영. 한 사이트 안에 카테고리별 다른 템플릿은 비권장 (시각 일관성·SEO 이유).

### `option` — 사용법 한눈에

```bash
/hams:diary option   # 서브명령·플래그·템플릿·예시·현재 설정을 한 번에 표시 (read-only)
```

`option` 은 어떤 외부 동작(git/clone/server/AskUserQuestion/파일 갱신)도 발생시키지 않는다. 사용법을 빠르게 훑고 싶을 때 호출. 출력 양식은 0-4 참조.

---

## 0️⃣ 인자 해석 & 설정 확인

### 0-1. 설정 파일 스키마 + 자동 마이그레이션

**파일 위치**: `~/.claude/hams-diary.json`

**현재 스키마** (멀티-프로파일):

```json
{
  "active": "default",
  "profiles": {
    "default": {
      "repo": "https://github.com/me/blog.git",
      "template": "tech",
      "blogTitle": "기술 노트",
      "pagesUrl": "https://...",
      "features": { "search": true }
    }
  }
}
```

**자동 마이그레이션** — 어떤 서브명령이든 첫 호출 시 다음 검사:

```python
import json, shutil, os
p = os.path.expanduser('~/.claude/hams-diary.json')
if os.path.exists(p):
    cfg = json.load(open(p, encoding='utf-8'))
    # flat schema {repo, template, ...} → multi-profile
    if 'profiles' not in cfg and ('repo' in cfg or 'template' in cfg):
        shutil.copy(p, p + '.bak')   # 안전 백업
        cfg = {"active": "default", "profiles": {"default": cfg}}
        json.dump(cfg, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    cfg.setdefault('active', 'default')
    cfg.setdefault('profiles', {})
```

**파일이 없는 경우** (publish/edit/delete/config 호출 시): AskUserQuestion으로 첫 프로파일 repo URL 받아 다음으로 초기화:

```json
{ "active": "default", "profiles": { "default": { "repo": "<URL>", "template": "tech", "features": { "search": true } } } }
```

`option` 호출 시에는 파일 없어도 안내만 출력 (초기화 안 함).

### 0-2. 서브명령 라우팅

인자 1번째 토큰으로 분기:

| 토큰 | 분기 |
|---|---|
| `publish` | publish 흐름 (1️⃣~🔟) |
| `edit {slug|id}` | edit 모드 |
| `delete {title|id}` | 0-3.2 — 삭제 (제목 유사도 또는 숫자 ID) |
| `config <sub>` | 0-3 |
| `option` | 0-4 (read-only) |
| 그 외 | "알 수 없는 명령. `/hams:diary option` 으로 사용법을 확인하세요" 안내 후 종료 |

> 옛 표기(`--set-repo`, `--set-template`, `--enable-*`, `--disable-*`, `--edit`, `--rebuild-remote`, `giscus`, `config comments`, 서브명령 없는 단독 파일 인자)는 모두 **폐기됐다**. 받으면 위 "알 수 없는 명령" 분기로 안내 후 종료.

### 0-3. `config` 서브명령 분기

마이그레이션 후 `cfg['profiles'][cfg['active']]` 를 **P** (활성 프로파일) 라고 한다.

| 명령 | 동작 |
|---|---|
| `config show` | `cfg` 전체 + 활성 프로파일 강조해서 보기 좋게 출력 |
| `config repo {url}` | `P['repo'] = url` 갱신 |
| `config template {1-5\|name}` | `TEMPLATES = ['minimal','tech','lecture','notebook','magazine']`. 숫자/이름 검증 후 `P['template']` 갱신 |
| `config search on\|off` | on이면 Node.js (`npx`) 가용성 체크 + `npx -y pagefind --version` 사전 다운로드 → `P['features']['search'] = on/off` |
| `config blog-title "{title}"` | `P['blogTitle'] = title` |
| `config profile list` | `cfg['profiles']` 키 목록 + `cfg['active']` 표시 |
| `config profile add {name} {url}` | 이름 충돌 검사 → `cfg['profiles'][name] = {'repo': url, 'template': 'tech'}` 등록 |
| `config profile use {name}` | 존재 검증 → `cfg['active'] = name` |
| `config profile remove {name}` | 활성이면 다른 프로파일로 자동 전환. 마지막 1개면 거부 |

모든 갱신은 `json.dump(cfg, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)` 로 저장 후 종료. publish/edit는 트리거되지 않는다.

### 0-3.2 `delete` 서브명령 — 글 삭제

**호출 형태**

```bash
/hams:diary delete {target} [--profile {name}] [--yes]
```

**target 해석**

1. `target` 이 **순수 정수** (예: `5`, `12`) → **숫자 ID 모드**
   - `posts[].postId == int(target)` 인 entry 찾기 → 정확 매칭
   - 없으면 "ID {N} 글이 없습니다" 안내 후 종료
2. 그 외 (문자열, 한글, 슬러그 패턴) → **제목 유사도 모드**
   - 후보 = `posts[]` 중 다음 중 하나를 만족하는 entry:
     - `target.lower() in entry['title'].lower()` (부분 일치)
     - `target.lower() in entry['id'].lower()` (slug 부분 일치)
     - `difflib.SequenceMatcher(None, target.lower(), entry['title'].lower()).ratio() >= 0.5`
   - 후보 0건 → "일치하는 글이 없습니다. `/hams:diary delete` 로 ID 입력하세요" 안내 후 종료
   - 후보 1건 → 그 entry 로 진행 (확인 단계로)
   - 후보 2건 이상 → AskUserQuestion 으로 사용자에게 선택받음 (각 옵션: `[#{postId}] {title} (slug={id}, category={cat})`)

**흐름**

1. 활성 프로파일 P 결정 (publish 와 동일 — `--profile` 추출, 0-5 로직).
2. LOCAL_DIR clone/pull → 워크트리 생성 (`BR=delete-${postId}-${TS}`).
3. posts.json 로드 → 위 매칭 로직으로 **삭제 대상 entry 선정**.
4. **삭제 미리보기 출력**:
   ```
   🗑  삭제 대상
      #ID: {postId}
      제목: {title}
      slug: {id}
      카테고리: {category}
      URL: /posts/{postId}/{id}.html
      파일: posts/{postId}/{id}.html, _src/{id}.{ext}
   ```
5. `--yes` 가 없으면 AskUserQuestion: "정말 삭제할까요?"
   - ✅ 삭제 / ❌ 취소
   - 취소 시: 워크트리·브랜치 삭제, push 0회, 종료
6. **파일·entry 삭제**:
   - `os.remove(f"posts/{postId}/{id}.html")`
   - `shutil.rmtree(f"posts/{postId}")` (디렉토리 비면 — 단일 글당 폴더 1개이므로 항상 삭제됨)
   - `os.remove(f"_src/{id}.{ext}")` (존재할 때만)
   - posts.json `posts[]` 에서 해당 entry 제거 (postId 재정렬은 하지 않음 — ID 영구 유지)
   - 글로벌 `categories[]` 재계산: 삭제 후 남은 entry 들의 `categories` 의 union 만 유지 (insertion order)
7. Pagefind 재빌드 (search 활성 시 — 인덱스에 삭제된 페이지가 남으면 안 됨).
8. 미리보기 서버 시작 + `http://localhost:$PORT/` 브라우저 오픈 → 목록에서 사라진 것 확인.
9. AskUserQuestion: "사이트에서 삭제 확인됐습니다. push 할까요?"
   - ✅ → commit (메시지: `delete: {title} (#${postId})`) → push → PR → merge → 워크트리 정리
   - ❌ → 워크트리·브랜치 삭제, push 0회
10. 결과 출력:
    ```
    ✅ 삭제 완료
       · #{postId} {title}
       🌐 {PAGES_URL} 에서 1~2 분 후 반영
    ```

**주의**
- **postId 는 재사용하지 않는다.** 5번 글을 삭제해도 다음 글은 (현재 최대값 + 1) 을 받음. URL stability + 검색엔진 캐시 보호.
- `posts/` 아래 잘못된 빈 디렉토리(예: 옛 빌드 잔재) 정리는 별도 안전장치로 처리 — 삭제 모드는 entry 가 실제로 가리키는 파일만 건드린다.
- 매칭 결과를 표시할 때 한국어 title 우선, slug 보조.

### 0-4. `option` 서브명령 (read-only)

어떤 외부 동작(git/clone/server/AskUserQuestion/파일 갱신)도 발생시키지 않고 다음을 출력하고 종료:

```
🐹 /hams:diary — 로컬 마크다운/HTML → GitHub Pages 개인 블로그

📌 서브명령
  publish {file|dir|glob} [category] [--플래그…]      # 게시 (단일/일괄 자동 감지)
  edit {slug|id} [--profile {name}]                    # 기존 글 편집 (라이브 미리보기)
  delete {title|id} [--yes] [--profile {name}]         # 삭제 (제목 유사도 또는 숫자 ID)
  config <sub>                                          # 설정 (아래)
  option                                                # 이 사용법 표시 (read-only)

🚩 publish 플래그
  --no-theme                           # HTML 어댑터 주입 끄기 (라이트/다크 변환 OFF, 폭은 native)
  --overwrite                          # 같은 글 발견 시 기존 slug에 덮어쓰기 (URL 보존)
  --draft                              # 푸시 안 하고 워크트리만 남김
  --preview-port N                     # 미리보기 포트 (기본 8765)
  --rebuild [slug|all|--category X]    # 사이트 기존 글 재테마
  --profile {name}                     # 1회 임시 프로파일 override (active 변경 안 함)
  --fit-viewport                       # 시뮬레이터 max-width 풀어서 viewport 채움 (반응형 시뮬레이터 권장)
  --scale-up                           # CSS transform: scale 로 viewport 너비에 맞게 확대 (고정폭 시뮬레이터 권장)

🔧 config 서브명령 (활성 프로파일 갱신)
  show                                 # 활성 + 모든 프로파일 표시
  repo {github-url}                    # 활성 프로파일의 타겟 레포
  template {1-5|minimal|tech|lecture|notebook|magazine}
  search {on|off}                      # Pagefind 풀텍스트 검색
  blog-title "{제목}"

👥 프로파일 관리 (멀티 블로그 운영용)
  config profile list                              # 전체 목록 + 활성 표시
  config profile add {name} {repo-url}             # 신규 프로파일 등록
  config profile use {name}                        # 활성 전환
  config profile remove {name}                     # 삭제 (마지막 1개는 거부)

🎨 5가지 템플릿
  minimal   — 흰 배경 · 세리프 · 단일 컬럼 (텍스트 노트, 에세이)
  tech      — 다크 히어로 · 그라데이션 카드 · 카테고리 필터 (시뮬레이터·도구)
  lecture   — 주차/회차 번호 · 사이드 목차 (강의 시리즈)
  notebook  — Jupyter풍 좌측 TOC · monospace 헤딩 (튜토리얼)
  magazine  — 큰 히어로 · 에디토리얼 그리드 · 세리프 (포트폴리오)

💡 예시
  /hams:diary publish ./hello.md 일상
  /hams:diary publish ./hello.md "msa,kafka"                # 다중 카테고리 (쉼표 구분)
  /hams:diary publish ./drafts/ 일상 --overwrite
  /hams:diary publish ./사이트.html 기술 --no-theme
  /hams:diary publish ./post.md 일상 --profile diary        # 1회 임시 override
  /hams:diary edit hello-world
  /hams:diary edit 5                                        # 숫자 ID 도 가능
  /hams:diary delete 5                                      # postId=5 삭제
  /hams:diary delete "MSA Kubernetes"                       # 제목 유사 매칭
  /hams:diary config profile add tech https://github.com/me/tech-blog.git
  /hams:diary config profile use tech
  /hams:diary config search on

📂 현재 설정 (~/.claude/hams-diary.json)
  active: <cfg.active>
  profiles: <N>개
  - <name>  →  <repo>  (<template>)
  - ...

  활성 프로파일 <active> 상세
    repo:        <P.repo>
    template:    <P.template>
    blogTitle:   <P.blogTitle 또는 (미설정)>
    search:      <on|off> (기본 on)

💾 옛 flat 형태({repo, template, ...})는 첫 호출 시 자동으로 default 프로파일로 변환되며 ~/.claude/hams-diary.json.bak 에 백업됩니다.

⚠️  옛 표기(--set-repo / --set-template / --enable-* / --disable-* / --edit / --rebuild-remote / giscus / config comments / 서브명령 없는 단독 파일 인자)는 모두 폐기됐습니다.

📖 더 자세한 spec: skills/diary/SKILL.md
```

설정 파일이 아예 없으면 "📂 현재 설정" 섹션은 "(아직 없음 — `/hams:diary config profile add default <url>` 로 시작)"으로 대체.

### 0-5. 일반 실행 (publish/edit) — 활성 프로파일 추출

`publish` 또는 `edit` 로 라우팅된 경우:

1. 인자에서 `--profile {name}` 추출 → 있으면 그 이름, 없으면 `cfg['active']`
2. `cfg['profiles'][name]` 존재 여부 검증 (없으면 에러 종료: "프로파일 없음. `/hams:diary config profile list` 로 확인")
3. 활성 프로파일 P에서 다음 변수 추출:

| 변수 | 값 |
|---|---|
| `PROFILE_NAME` | 사용 중인 프로파일 이름 |
| `REPO_URL` | `P['repo']` |
| `REPO_OWNER`, `REPO_NAME` | URL 파싱 |
| `PAGES_URL` | `P['pagesUrl']` 또는 `https://${OWNER}.github.io/${NAME}/` |
| `TEMPLATE` | `P['template']` (기본 `tech`) |
| `BLOG_TITLE` | `P['blogTitle']` (없으면 첫 배포 시 AskUserQuestion으로 받아 P에 저장) |
| `FEATURES` | `P['features']` (없으면 `{search: true}` — Pagefind 검색만 ON) |
| `LOCAL_DIR` | `/tmp/${REPO_NAME}-${PROFILE_NAME}` (프로파일별 분리) |
| `WORKTREE_DIR` | `/tmp/${REPO_NAME}-${PROFILE_NAME}-preview-${TS}` |

`P['template']` 필드 없으면 첫 배포 시 AskUserQuestion으로 5개 중 선택받고 P에 저장.

---

## 1️⃣ 입력 분류 & Job 목록 생성

입력 인자를 분석해 **JOBS** 배열을 만든다. 각 job:

```python
{
  "src": "/abs/path/to/file.md",   # 원본 절대경로
  "engine": "md" | "html",          # 처리 엔진
  "slug": "kebab-case-id",
  "title": "추출된 제목",
  "categories": ["msa", "kafka"],  # 항상 배열 (1개여도 ["msa"])
  "tags": [...],
  "summary": "..."
}
```

> **`categories` 입력 규칙**
> - CLI: `/hams:diary publish ./post.md "msa,kafka"` — 쉼표 구분, 공백 trim, 빈 항목 제거.
> - AskUserQuestion: 비어있으면 기존 글로벌 카테고리 목록 + "신규 입력" 으로 `multiSelect: true`. 글로벌이 비면 텍스트 1개 입력.
> - 옛 단일 string `category` 인자도 호환 — 내부적으로 `[category]` 로 변환.

### 모드별 처리

- **`{file.md}`** → 1 job (engine=md)
- **`{file.html}`** → 1 job (engine=html)
- **`{dir/}`** → 디렉토리 안 모든 `.md` + `.html` (재귀 X). 비-ASCII 파일명 처리(아래) 거쳐 N jobs.
- **`"{glob}"`** → glob 매칭한 파일들

### 비-ASCII (한글) 파일명 처리

Windows + Python 조합에서 한글 파일명이 `os.listdir()` 으로 보이지 않는 케이스가 있다. PowerShell 로 우회:

```powershell
Get-ChildItem -LiteralPath $src -Filter *.html | ForEach-Object {
  # ASCII slug 로 임시 디렉토리에 복사
  $slug = ...  # title/길이/순번 기반
  Copy-Item -LiteralPath $_.FullName -Destination "$tmp/$slug.html" -Force
}
```

이후 Python 빌더는 ASCII 임시 디렉토리에서 파일을 읽는다.

### 메타데이터 추출

- **MD**: frontmatter(`---` 사이) 우선, 없으면 첫 H1 → title, 첫 문단 → summary, 헤딩들 → tags
- **HTML**: `<title>` 태그 → title, `<meta name="description">` → summary, 첫 H1 → fallback title, body 안 헤딩들 → tags
- **slug**: 파일명 → kebab-case (한글은 PowerShell 단계에서 ASCII slug 로 변환됨)
- **categories**: CLI 인자 우선 (쉼표 구분 — 위 규칙 참조), 없으면 AskUserQuestion `multiSelect: true` 로 (기존 글로벌 + "신규 입력")

---

## 2️⃣ 레포 준비 + 워크트리 생성

```bash
# Clone (없으면) 또는 pull (있으면)
if [ ! -d "$LOCAL_DIR" ]; then
  git clone "$REPO_URL" "$LOCAL_DIR"
fi
cd "$LOCAL_DIR"
BASE_BRANCH=$(git remote show origin | grep 'HEAD branch' | sed 's/.*: //')
# 빈 레포면 BASE_BRANCH는 main 으로 가정
[ -z "$BASE_BRANCH" ] && BASE_BRANCH=main
git fetch origin || true
git checkout "$BASE_BRANCH" 2>/dev/null || git symbolic-ref HEAD refs/heads/$BASE_BRANCH
git pull origin "$BASE_BRANCH" 2>/dev/null || true

# 워크트리 (배포 단위)
TS=$(date +%Y%m%d-%H%M%S)
BR="post-preview-${TS}"
git worktree add -b "$BR" "$WORKTREE_DIR"
cd "$WORKTREE_DIR"
```

---

## 3️⃣ 첫 배포면 템플릿 복사

워크트리에 `index.html` 이 없거나 `.diary-meta.json` 의 template 이 다르면:

```bash
TEMPLATE_DIR="${PLUGIN_ROOT}/skills/diary/templates/${TEMPLATE}"
cp -R "$TEMPLATE_DIR"/* .
# {{BLOG_TITLE}}, {{BLOG_TAGLINE}}, {{BLOG_HERO_TITLE}}, {{BLOG_ABOUT}}, {{BLOG_YEAR}} 치환
sed -i "s/{{BLOG_TITLE}}/${BLOG_TITLE}/g" index.html
# ... (모든 템플릿 변수 치환)
echo "{\"template\":\"${TEMPLATE}\"}" > .diary-meta.json
touch .nojekyll  # GitHub Pages 가 _underscore 폴더를 무시하지 않도록
```

`{{BLOG_TITLE}}`, `{{BLOG_TAGLINE}}`, `{{BLOG_HERO_TITLE}}`, `{{BLOG_ABOUT}}`, `{{BLOG_YEAR}}` 가 비어있으면 AskUserQuestion 으로 사용자에게 입력받음.

---

## 4️⃣ posts.json 갱신 (메모리상) — 안전한 매칭

```bash
# 기존 posts.json 로드 (없으면 빈 구조)
[ -f posts.json ] && cat posts.json || echo '{"categories":[],"posts":[]}'
```

각 job 에 대해 **3단계 매칭 우선순위** 로 기존 항목을 찾는다 (한글 파일명 → ASCII slug 변환 시 drift 가 있어도 같은 글로 식별 가능하게):

1. **`originalFilename` 일치** (1순위) — `os.path.basename(SRC)` 와 `posts[].originalFilename` 직접 비교. 한글 원본 파일명 그대로 비교하므로 slug 알고리즘이 바뀌어도 면역.
2. **`id == job.slug` 일치** (2순위) — 기존 동작. originalFilename 이 빈 옛 항목 (마이그레이션 전) 호환용.
3. **제목 유사도 ≥ 0.85 + 같은 `engine`** (3순위) — `difflib.SequenceMatcher` 로 비교. 후보가 정확히 1건이면 AskUserQuestion 으로 사용자 확인 ("기존 글 'X' 와 같은 글입니까? 덮어쓸까요 / 신규 추가할까요"). 후보가 2건 이상이면 AskUserQuestion 으로 선택 또는 신규 추가.

매칭 결과 처리:

- **매칭 발견 + `--overwrite` 미설정**: `[skip] {filename} → already exists as id=${existing_slug}` 출력, 이 job 제외
- **매칭 발견 + `--overwrite` 설정**: **기존 slug 재사용** (URL 보존). `posts/{existing_slug}.html` 덮어쓰기, `_src/{existing_slug}.{ext}` 갱신, posts.json 항목 in-place 업데이트. 새 slug 절대 생성 안 함.
- **매칭 없음**: 새 slug 로 신규 삽입.

스키마 (기존 호환 + 신규 필드):
```json
{
  "postId": 1,
  "id": "kebab-slug",
  "title": "...",
  "date": "YYYY-MM-DD",
  "categories": ["msa", "kafka"],
  "summary": "...",
  "filename": "posts/1/kebab-slug.html",
  "tags": ["..."],
  "engine": "md" | "html",
  "themeInjected": true | false,
  "sourcePath": "_src/kebab-slug.{ext}",
  "originalFilename": "원본_파일명.html"
}
```

**`categories` 호환성 규칙**
- 새 entry 는 항상 `categories: [...]` 배열로 저장. 단일이어도 `["msa"]`.
- 옛 entry 가 `category: "msa"` 만 가지고 있으면 다음 publish/edit/--rebuild 시 자동 마이그레이션:
  `entry['categories'] = [entry.pop('category')]`. 정규화 후 글로벌 `categories[]` 도 갱신.
- 사이트 JS (template 의 `script.js`) 는 항상 `entry.categories ?? (entry.category ? [entry.category] : [])` 로 정규화해서 읽음. 첫 카테고리가 라벨/아이콘의 기본값.

**`postId` 부여 규칙**
- 신규 글의 `postId` = `max(p['postId'] for p in posts) + 1` (없으면 1). **재사용 금지** — 삭제된 ID 도 다시 쓰지 않는다 (URL 안정성).
- `filename` 은 항상 `posts/{postId}/{id}.html` 로 통일.
- 옛 스키마 (postId 없음) 항목은 publish/edit/--rebuild 첫 호출 시 자동 마이그레이션 — 현재 배열 순서대로 1, 2, 3 부여 + 파일 이동.

> **`originalFilename` 마이그레이션** — 기존 항목에 이 필드가 없는 경우, 다음 배포·재빌드 시 자동으로 채워진다. 1순위 매칭은 그냥 건너뛰고 2순위(slug)로 폴백되므로 옛 데이터 손상 없음.

**글로벌 `categories[]` 관리** — entry 의 `categories` 의 모든 항목을 글로벌 `categories[]` 에 union (첫 등장 순서 유지). 삭제 시 다른 글에서 더 이상 사용 안 하는 카테고리만 글로벌 배열에서 제거.

---

## 5️⃣ 포스트 HTML 생성 (워크트리에 기록)

### MD 엔진

```bash
# 출력 경로는 항상 posts/{postId}/{slug}.html
mkdir -p "posts/${postId}"

# 마크다운 → HTML 변환 (기존 변환 규칙 그대로, 인라인 Python markdown 또는 정규식)
# 변환된 HTML 을 _post-frame.html 의 {{POST_HTML}} 자리에 치환.
# {{POST_CATEGORY}} 는 categories 의 첫 번째 항목만 표시 (글 본문 헤더는 간결하게).
PRIMARY_CAT="${CATEGORIES[0]:-}"
sed -e "s|{{POST_TITLE}}|${TITLE}|g" \
    -e "s|{{POST_CATEGORY}}|${PRIMARY_CAT}|g" \
    -e "s|{{POST_DATE}}|${DATE}|g" \
    -e "s|{{POST_HTML}}|${BODY_HTML}|g" \
    -e "s|{{BLOG_TITLE}}|${BLOG_TITLE}|g" \
    _post-frame.html > "posts/${postId}/${slug}.html"
```

`_post-frame.html` 자체에는 `../../assets/style.css` 와 `../../index.html` 링크가 들어 있으므로 글이 깊이 2 디렉토리 안에서도 정상 동작.

(실제로는 sed 보다 Python 한 줄로 read+replace+write 하는 게 안전함, 본문에 특수문자 있을 수 있어서)

### HTML 엔진

```bash
# 출력 경로는 항상 posts/{postId}/{slug}.html
mkdir -p "posts/${postId}"

# 폭 모드 — CLI 플래그 또는 (--rebuild 시) posts.json[].fit 에서 결정
#   publish 시: --fit-viewport / --scale-up 인자에서 추출
#   rebuild 시: 기존 entry 의 fit 필드 (없으면 native)
FIT_ARG=""
case "$FIT_MODE" in
  viewport) FIT_ARG="--fit-viewport" ;;
  scale)    FIT_ARG="--scale-up" ;;
  *)        FIT_ARG="" ;;
esac

python3 "${PLUGIN_ROOT}/skills/diary/inject_html_adapter.py" \
  --src "${SRC}" --dst "posts/${postId}/${slug}.html" --title "${TITLE}" \
  ${NO_THEME:+--no-theme} $FIT_ARG

# 결과 fit_mode 를 posts.json 의 해당 entry 에 저장 (재빌드 시 그대로 재현)
#   {"postId":..., "id":..., "fit":"native|viewport|scale", ...}
```

어댑터의 floating bar 안 back-link 는 `../../index.html` 로 emit 된다 (글이 2단 깊이에 있으므로). 배치 모드는 `--map` JSON 으로 한 번에 호출 가능.

> 어댑터는 원본 HTML 의 dominant background 를 자동 감지해 `data-osd-source-theme="light|dark"` 로 표시한다. 사용자가 선택한 블로그 테마와 톤이 다를 때만 invert 필터를 걸어 자동 변환하므로, 라이트 톤 원본(예: 베이지) 도 다크 블로그에서 자연스럽게 보인다. (감지 실패 시 기존 동작인 `dark` 가정.)

### 원본 소스 보존 (`_src/`) + originalFilename 기록

배포 시 원본 파일을 워크트리의 `_src/{slug}.{ext}` 로도 복사한다. 나중에 `edit {slug}` 또는 `publish --rebuild` 시 이 원본을 사용한다.

```bash
mkdir -p _src
cp "${SRC}" "_src/${slug}.${EXT}"   # ext = md or html (변환 전 파일)
```

posts.json 의 두 필드에 기록:
- `sourcePath`: `"_src/{slug}.{ext}"` — 백업 파일 위치
- `originalFilename`: `os.path.basename(SRC)` — **매칭 1순위 키**. 한글 파일명 그대로 (`"Saga 오케스트레이션 _kafka.html"` 같은 형태) 저장. 다음 `--overwrite` 때 slug 가 다르게 나와도 이 필드로 같은 글이라고 식별.

`_src/` 는 GitHub Pages 가 무시하지 않도록 `.nojekyll` 만 있으면 그대로 서빙되지만, 보통 사이트에는 노출되지 않게 `index.html` 의 라우팅 대상 외다 — 그냥 레포에만 보관되는 원본 백업이다.

---

## 5️⃣.5 기능 토글 적용 (검색)

`features` 가 활성화되어 있으면 변수 치환 시 다음 자리표시자도 함께 채운다.

### `{{SEARCH_BLOCK}}` (index.html 안)

`features.search === true`:
```html
<div id="osd-search" class="osd-search"></div>
<link rel="stylesheet" href="pagefind/pagefind-ui.css" />
<script src="pagefind/pagefind-ui.js"></script>
<script>
  window.addEventListener('DOMContentLoaded', function () {
    new PagefindUI({
      element: '#osd-search',
      showSubResults: true,
      translations: { placeholder: '본문 검색…', clear_search: '지우기', no_results: '결과 없음' }
    });
  });
</script>
```

`features.search === false`:
```html
<!-- search disabled -->
```

> 댓글 기능은 지원하지 않는다. 옛 버전의 `{{COMMENTS_BLOCK}}` 자리표시자나 `--comments-*` 어댑터 인자는 모두 폐기됐다.

---

## 6️⃣ 미리보기 서버 + 브라우저 오픈

```bash
PORT=${PREVIEW_PORT:-8765}
cd "$WORKTREE_DIR"
python3 -m http.server $PORT >/tmp/diary-preview.log 2>&1 &
SERVER_PID=$!
sleep 1

# 브라우저 자동 오픈
URL="http://localhost:${PORT}/"
case "$(uname -s)" in
  MINGW*|CYGWIN*|MSYS*) start "$URL" ;;
  Darwin) open "$URL" ;;
  Linux) xdg-open "$URL" >/dev/null 2>&1 || true ;;
esac
```

> Windows Git Bash 에서 `start` 가 안 되면 `cmd //c start "" "$URL"` 또는 PowerShell `Start-Process "$URL"` 로 폴백.

미리보기에서 개별 글은 `http://localhost:${PORT}/posts/{postId}/{slug}.html` 에서 볼 수 있다. 사용자에게 안내 출력 시 첫 N개의 직접 URL 을 함께 표시하면 좋다.

---

## 7️⃣ 승인 게이트

AskUserQuestion 호출:

```
질문: "이 모습으로 게시할까요?"
   ✅ 게시 (Recommended) — push + PR + merge
   ✏️ 수정     — 사용자 피드백 받아 4~5단계 재실행 (또는 워크트리 그대로 두고 사용자가 직접 편집)
   ❌ 취소     — 워크트리 삭제, 0회 push
```

선택 후 처리:

- **✅ 게시** → 9단계로 진행
- **✏️ 수정** → 사용자에게 어떤 부분이 문제인지 묻고, 가능하면 자동으로 수정 후 4~5단계 재실행. 수정 불가능한 경우 워크트리를 그대로 두고 "워크트리 위치: ${WORKTREE_DIR}. 직접 수정 후 다시 실행해 주세요" 안내. 서버는 종료.
- **❌ 취소** → `kill $SERVER_PID; git worktree remove --force "$WORKTREE_DIR"; git branch -D $BR` 후 종료.

---

## 8️⃣.5 Pagefind 인덱스 생성 (검색 활성 시)

`features.search === true` 인 경우, push 직전에 인덱스를 빌드해 같은 commit 에 포함시킨다.

```bash
if [ "$FEATURES_SEARCH" = "true" ]; then
  cd "$WORKTREE_DIR"
  npx -y pagefind --site . --output-path pagefind 2>&1 | tail -5
  # 결과: ./pagefind/ 디렉토리 (UI css/js + 인덱스 조각들)
fi
```

빌드 실패 시 ("Node.js 없음" 등) 사용자에게 안내하고 검색 없이 진행.

## 9️⃣ Commit + Push + PR + Merge

```bash
cd "$WORKTREE_DIR"
git add -A
git commit -m "feat: ${TITLES_SUMMARY}

- 카테고리: ${CATEGORIES}
- 템플릿: ${TEMPLATE}
- 처리 파일 수: ${OK_COUNT}"

git push -u origin "$BR"

# 빈 레포면 PR 안 됨 → 직접 base에 push
if ! git ls-remote --heads origin "$BASE_BRANCH" | grep -q "$BASE_BRANCH"; then
  git push origin "${BR}:${BASE_BRANCH}"
else
  gh pr create --head "$BR" --base "$BASE_BRANCH" \
    --title "feat: ${TITLES_SUMMARY}" \
    --body "${PR_BODY}"
  gh pr merge --squash --delete-branch
fi

git checkout "$BASE_BRANCH"
git pull origin "$BASE_BRANCH"
```

`gh` CLI 가 없으면 `git push origin "${BR}:${BASE_BRANCH}"` 로 직접 푸시 + 사용자에게 GitHub Pages 활성화 가이드 출력.

## 🔟 정리 + 결과 출력

```bash
kill $SERVER_PID 2>/dev/null
git worktree remove --force "$WORKTREE_DIR"
```

```
✅ 게시 완료!

📦 처리한 포스트 (N개):
   · #{postId1} {slug1} — {title1}   → {PAGES_URL}/posts/{postId1}/{slug1}.html
   · #{postId2} {slug2} — {title2}   → {PAGES_URL}/posts/{postId2}/{slug2}.html
   · [skip] {slug3} — already existed (use --overwrite to replace)

🏷️  카테고리: {cat}
🎨 템플릿: {template}
🌐 블로그: {PAGES_URL}
⏱️  반영: 1~2분 후 (GitHub Actions 자동 배포)
```

---

## 5가지 템플릿 한눈에

| name | 톤 | 적합한 콘텐츠 |
|------|-----|------|
| `minimal` | 흰 배경 · 세리프 본문 · 단일 컬럼 | 텍스트 중심 노트, 에세이 |
| `tech` (default) | 다크 히어로 · 그라데이션 카드 · 카테고리 필터 | 시뮬레이터 · 도식 · 도구 |
| `lecture` | 주차/회차 번호 · 사이드 목차 | 정규 강의 시리즈 |
| `notebook` | Jupyter풍 좌측 TOC · monospace 헤딩 | 튜토리얼 · 실습 |
| `magazine` | 큰 히어로 · 에디토리얼 그리드 · 세리프 | 포트폴리오 · 쇼케이스 |

각 템플릿은 `templates/{name}/` 안 4개 파일:
- `index.html` — 홈
- `assets/style.css`
- `assets/script.js`
- `_post-frame.html` — 마크다운 포스트 셸 (HTML 시뮬레이터는 이 셸을 사용하지 않고 어댑터만 주입)

---

## ✏️ 편집 모드 (`edit`)

기존 게시글의 내용·제목·태그를 고치는 가장 빠른 방법. 워크트리·미리보기·자동 재빌드·승인 게이트가 한 번에 묶여 있어 "오타 1개 고치고 게시" 가 30초 안에 끝난다.

### 흐름

```
[1] /hams:diary edit msa-k8s-websocket     (또는 /hams:diary edit 1)
[2] 레포 clone/pull → 워크트리 생성
[3] target 해석:
    - 순수 정수 → posts[].postId 매칭
    - 그 외     → posts[].id (slug) 정확 매칭
    매칭 없음 → "slug / postId 일치 없음" 안내 후 종료
[4] entry 의 sourcePath 확인
    sourcePath 없음 → "_src/ 백업 부재" 안내 후 종료
[5] 기본 에디터로 _src/{slug}.{ext} 열기
[6] python -m http.server $PORT 백그라운드 실행
[7] 브라우저 자동 오픈 → http://localhost:8765/posts/{postId}/{slug}.html
[8] watch_and_rebuild.py 백그라운드 실행
    → _src/{slug}.{ext} mtime 변경 감지 시
    → 적절한 빌더 호출 (md → 변환, html → inject_html_adapter)
    → posts/{postId}/{slug}.html 갱신 + 콘솔에 [HH:MM:SS] rebuilt 출력
[9] 사용자가 에디터에서 저장할 때마다 (6)~(8)의 자동 빌드 발생
    브라우저에서 F5 로 변경 확인
[10] 편집 완료 후 AskUserQuestion: "이 변경을 게시할까요?"
       ✅ 게시 → commit + push + PR + merge (커밋 메시지: "edit: {title}")
       ❌ 취소 → 워크트리/브랜치 삭제, push 0회
[11] watcher 종료 + 서버 종료 + 워크트리 정리
```

### `_src/` 가 없는 기존 포스트

`/hams:diary` v1 시절(즉, `_src/` 백업 도입 이전)에 게시된 포스트는 `posts/{postId}/{slug}.html` 의 빌드 결과만 레포에 있다. 처리 경로:

- **HTML 시뮬레이터**: `publish --rebuild {slug|id}` 가 자동으로 `extract_original_html.py` 를 돌려 어댑터 마커 사이 블록을 제거 → 원본 복원 → `_src/` 에 저장 → 어댑터 재주입. 손에 원본 파일 없어도 됨.
- **MD 였던 포스트**: 역변환 비신뢰 (HTML→MD 손실). 원본 `.md` 가 손에 있다면 `--overwrite` 로 재배포해 `_src/` 백업 생성. 없으면 skip + 경고.

가장 안전한 길: 첫 게시 후엔 원본을 로컬에서 보관하지 말고, 항상 `_src/` 를 진실의 원본으로 사용한다.

### 명령어 호출 예

```bash
# Python watcher 호출 형태 (md)
python3 "${PLUGIN_ROOT}/skills/diary/watch_and_rebuild.py" \
  --src "_src/${slug}.md" --dst "posts/${postId}/${slug}.html" \
  --engine md --frame "_post-frame.html" \
  --title "${TITLE}" --category "${CAT}" \
  --date "${DATE}" --blog-title "${BLOG_TITLE}" &
WATCHER_PID=$!

# Python watcher 호출 형태 (html)
python3 "${PLUGIN_ROOT}/skills/diary/watch_and_rebuild.py" \
  --src "_src/${slug}.html" --dst "posts/${postId}/${slug}.html" \
  --engine html --title "${TITLE}" \
  ${NO_THEME:+--no-theme} &
WATCHER_PID=$!
```

### 메타데이터(제목·요약·카테고리·태그) 편집

본문이 아닌 메타만 바꾸고 싶으면 `_src/` 의 frontmatter(MD) 또는 `<title>`/`<meta>` 태그(HTML)를 수정하면 watcher 가 추출해 posts.json 도 갱신한다 (재빌드 시 메타 추출 로직이 동일하게 돌기 때문).

---

## 🔄 재빌드 모드 (`publish --rebuild`)

**언제 쓰나** — 어댑터 로직이 바뀌었거나 새로운 시그니처/테마/기능 토글을 기존 모든 글에 일괄 적용하고 싶을 때. 로컬에 원본 파일이 있을 필요가 없다 (레포의 `_src/` 또는 `posts/{postId}/{slug}.html` 역추출이 소스가 됨).

### 호출 형태

```bash
/hams:diary publish --rebuild msa-k8s-websocket          # 단일 (slug 또는 postId)
/hams:diary publish --rebuild 5                          # 단일 (숫자 ID)
/hams:diary publish --rebuild all                        # 전체
/hams:diary publish --rebuild --category msa             # 카테고리
```

### 흐름

```
[1] 설정 Read → REPO clone/pull → 워크트리 생성 (BR=rebuild-{TS})
[2] posts.json 로드 → 대상 entries 결정:
    - 순수 정수    : posts[].postId 매칭 단일 entry
    - {slug}      : posts[].id 매칭 단일 entry (없으면 종료)
    - all         : posts[] 전체
    - --category X: posts[].category == X 인 것들
[3] **postId 마이그레이션 검사** — entry 에 `postId` 가 없으면 현재 배열 순서대로 부여
    (이미 부여된 항목의 postId 는 절대 재배정 안 함)
[4] 첫 배포 판단 (index.html 부재 / 템플릿 변경) → 템플릿 다시 입힘
[5] 각 entry 에 대해 SOURCE 결정 (우선순위):
    a. _src/{slug}.{ext} 존재 → 그대로 사용
    b. engine == html, _src/ 없음:
       extract_original_html.py --src <기존 filename> --dst _src/{slug}.html
       → 원본 복원 후 (a) 와 같이 사용. _src/ 없는 옛날 글의 자가치유.
    c. engine == md, _src/ 없음 → skip + 경고 ("MD 역변환 비신뢰; 원본 .md 로 --overwrite 재배포 필요")
[6] 출력 경로 변경:
    OLD_FILENAME = entry['filename']             # 옛 경로
    NEW_FILENAME = f"posts/{postId}/{slug}.html" # 새 경로
    mkdir -p posts/{postId}/
    빌더 호출:
      - md  → markdown→html 변환 → _post-frame.html 치환 → NEW_FILENAME
      - html → inject_html_adapter.py --src _src/{slug}.html --dst NEW_FILENAME --title "{title}"
    OLD_FILENAME != NEW_FILENAME 이면 OLD_FILENAME 삭제 + 빈 부모 dir 정리
[7] posts.json 갱신: filename ← NEW_FILENAME, postId 채움, themeInjected/sourcePath/originalFilename(없으면 채움)
[8] 미리보기 서버 + 브라우저 오픈 → 첫 N개 (3개 권장) URL 안내
[9] AskUserQuestion 승인 게이트:
    ✅ 게시 → commit + push + PR + merge (메시지: "rebuild: re-apply adapter to N posts")
    ✏️ 수정 → 워크트리 두고 안내 후 종료 (사용자 직접 수정)
    ❌ 취소 → 워크트리/브랜치 삭제, push 0회
[10] 워크트리 정리
```

### 명령어 호출 예

```bash
# extract (HTML 역추출)
python3 "${PLUGIN_ROOT}/skills/diary/extract_original_html.py" \
  --src "${OLD_FILENAME}" --dst "_src/${slug}.html"

# 그 후 평소처럼 inject
python3 "${PLUGIN_ROOT}/skills/diary/inject_html_adapter.py" \
  --src "_src/${slug}.html" --dst "posts/${postId}/${slug}.html" \
  --title "${TITLE}" ${NO_THEME:+--no-theme}
```

### 안전장치

- 변경 없는 entry (재빌드 후 새 `posts/{postId}/{slug}.html` 바이트가 동일하고 경로도 동일) 는 commit 에서 자동 제외 (`git diff --quiet`)
- `all` 모드는 처리 전 AskUserQuestion 로 "총 N개 재빌드합니다. 계속?" 확인
- MD entry skip 시 결과 출력에서 `[skip] {slug} (MD, _src/ 없음)` 로 명시
- postId 마이그레이션 (옛 → 새 URL) 은 1회만 발생. 다음 rebuild 부터는 위 안전장치가 정상 동작

---

## 🗑 삭제 모드 (`delete`)

**언제 쓰나** — 잘못 올린 글, 더 이상 보여주기 싫은 글을 사이트에서 빼고 싶을 때. 파일 + posts.json entry + pagefind 인덱스가 한 번에 정리된다.

### 호출 형태 (다시)

```bash
/hams:diary delete 5                    # postId=5
/hams:diary delete "MSA Kubernetes"     # 제목 유사도
/hams:diary delete msa-k8s-websocket    # slug 정확/유사
/hams:diary delete 5 --yes              # 확인 생략 (스크립트용)
```

### 흐름 (요약)

```
[1] 활성 프로파일 결정 (--profile override 가능)
[2] REPO clone/pull → 워크트리 (BR=delete-{postId}-{TS})
[3] posts.json 로드 → 0-3.2 매칭 로직으로 entry 선정
    · 정수 → postId 정확 매칭
    · 문자열 → title 부분일치 / slug 부분일치 / SequenceMatcher 유사도 ≥0.5
    · 후보 다건 → AskUserQuestion 으로 선택
[4] 삭제 미리보기 출력 + (--yes 없으면) AskUserQuestion 확인
[5] 파일 삭제:
    - posts/{postId}/{slug}.html
    - posts/{postId}/  디렉토리 (안 비면 경고 — 정상 시 비어있다)
    - _src/{slug}.{ext}
    - posts.json posts[] 에서 entry pop
    - 해당 entry 가 유일한 사용자였던 카테고리는 categories[] 에서 제거
[6] Pagefind 재빌드 (search === true 일 때) — 인덱스에 삭제된 페이지 잔여 방지
[7] 미리보기 서버 + 브라우저 → 목록에서 사라짐 확인
[8] AskUserQuestion 승인 → ✅ commit/push/PR/merge (메시지: "delete: {title} (#{postId})") | ❌ 취소
[9] 워크트리 정리
```

### 명령어 호출 예

```bash
# entry 결정 후 파일 정리
rm -f "posts/${postId}/${slug}.html"
rmdir "posts/${postId}" 2>/dev/null    # 비어있으면 제거 (정상)
rm -f "_src/${slug}.html"

# posts.json 갱신 (Python 한 줄)
python3 -c "
import json, sys
p = 'posts.json'
d = json.load(open(p, encoding='utf-8'))
d['posts'] = [x for x in d['posts'] if x.get('postId') != ${postId}]
# 카테고리 정리 (categories 배열 union, insertion order)
def cats_of(x):
    if isinstance(x.get('categories'), list): return x['categories']
    return [x['category']] if x.get('category') else []
used, seen = [], set()
for x in d['posts']:
    for c in cats_of(x):
        if c not in seen:
            seen.add(c); used.append(c)
d['categories'] = used
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
"

# pagefind 재빌드 (검색 활성 시)
[ "$FEATURES_SEARCH" = "true" ] && npx -y pagefind --site . --output-path pagefind
```

### 안전장치

- **postId 재사용 금지** — 5번을 삭제해도 다음 신규 글은 (현재 최대값 + 1) 받음. 이건 강한 규칙이다.
- 매칭 다건 시 사용자가 선택할 때까지 파일은 1바이트도 안 건드림.
- `--yes` 없으면 항상 확인 프롬프트 1회 + push 직전 승인 1회 = 2단계 안전장치.
- 파일은 있는데 entry 없는 (또는 그 반대) 비정상 상태는 1회 경고 출력하고 가능한 만큼 정리.

---

## 강의자료 특화 향후 확장 (미구현)

다음은 본 스킬에는 포함되어 있지 않지만 강의자료 운영에 유용한 기능들. 백로그.

1. **시리즈 그룹핑** — `series` 필드로 "MSA 강의 1주차" 같은 묶음 자동 생성
2. **공개 토글** — `published: false` 로 게시는 했지만 목록에서 숨김
3. **선수 학습 링크** — `prereq: ["msa-k8s-websocket"]`
4. **slide 모드** — `?mode=slide` 로 발표용 풀스크린 변환
5. **자동 ToC** — H2/H3 구조에서 우측 sticky ToC

필요해지면 별도 phase 로 추가.

---

## 에러 처리

| 케이스 | 처리 |
|------|-----|
| 설정 파일 없음 | AskUserQuestion 으로 URL 받기 → 저장 후 계속 |
| Clone 실패 | git config user.name/email · PAT/SSH 안내 |
| 한글 파일명 안 보임 | PowerShell `Get-ChildItem -LiteralPath` 폴백 |
| 빈 레포 | 첫 배포는 BR 을 직접 BASE_BRANCH 로 push |
| 미리보기 서버 포트 점유 | `--preview-port` 로 변경 또는 자동 incrementー 8765→8766→… |
| 브라우저 자동 오픈 실패 | URL 출력 후 사용자에게 직접 열도록 안내 |
| 사용자 ❌ 선택 | 워크트리/브랜치 삭제, push 0회, 깨끗하게 종료 |

---

## 내부 구현 체크리스트 (Claude 가 따를 순서)

### 공통 (모든 서브명령 진입 시)

- [ ] **인자 토큰 분류** — `publish` / `edit` / `delete` / `config <sub>` / `option` / 그 외
- [ ] **설정 자동 마이그레이션** — `~/.claude/hams-diary.json` Read → flat schema(`{repo, template, ...}`)면 `.bak` 백업 후 `{active, profiles}` 로 변환 (0-1 로직)
- [ ] 그 외 토큰이면 "알 수 없는 명령. `/hams:diary option` 으로 사용법을 확인하세요" 출력 후 종료

### `option` 분기

- [ ] 0-4의 출력 양식 그대로 출력. 어떤 외부 동작도 안 함. 종료.

### `config` 분기

- [ ] `cfg['profiles'][cfg['active']]` 를 P로 가져옴 (없으면 P = {})
- [ ] 0-3 표대로 처리:
  - `show` → cfg 보기 좋게 출력
  - `repo` / `template` / `search` / `blog-title` → P 갱신
  - `profile list` / `profile add` / `profile use` / `profile remove` → cfg 직접 갱신
  - 옛 `comments` 서브명령은 폐기 — 받으면 "지원하지 않는 명령" 안내 후 종료
- [ ] `json.dump(cfg, p, ensure_ascii=False, indent=2)` 저장
- [ ] 종료 (publish/edit/delete 안 트리거)

### `publish` 분기

- [ ] 인자에서 `--profile {name}` 추출 → 없으면 `cfg['active']`
- [ ] `cfg['profiles'][name]` 검증 (없으면 에러 종료: "프로파일 없음. /hams:diary config profile list 로 확인")
- [ ] 활성 프로파일에서 PROFILE_NAME, REPO_URL, OWNER, NAME, PAGES_URL, TEMPLATE, BLOG_TITLE, FEATURES, LOCAL_DIR, WORKTREE_DIR 결정 (0-5)
- [ ] **JOBS 배열 구성** — 단일/디렉토리/글롭 분기, 한글 파일명 PowerShell 폴백
- [ ] 각 job 메타 추출 (title/summary/tags/slug/categories, **originalFilename**)
- [ ] **categories 정규화** — CLI 인자 (쉼표 구분 → 배열), 단일 string 도 호환. 비어있으면 AskUserQuestion `multiSelect: true` 로 기존 + "신규 입력"
- [ ] LOCAL_DIR clone/pull
- [ ] WORKTREE_DIR worktree add (`BR=post-preview-${TS}`)
- [ ] 첫 배포 판단 (index.html 부재 또는 .diary-meta.json template 다름) → 템플릿 복사 + {{BLOG_*}} 치환 + .nojekyll
- [ ] BLOG_TITLE 등 미설정시 AskUserQuestion → P에 저장
- [ ] posts.json 로드 (없으면 빈 구조)
- [ ] **postId 마이그레이션** — 기존 entry 에 postId 없으면 현재 배열 순서대로 1, 2, 3... 부여 (이미 부여된 ID 는 보존)
- [ ] **categories 마이그레이션** — 기존 entry 에 옛 단일 `category` 만 있으면 `entry['categories'] = [entry.pop('category')]` 로 변환
- [ ] **각 job: 3단계 매칭** (originalFilename → slug → 제목 유사도 ≥0.85+같은 engine), 매칭 발견 시 기존 postId/slug 재사용. `--overwrite` 미설정이면 skip, 설정이면 in-place 교체 (categories 갱신). 매칭 없음이면 `max(postId)+1` 부여 후 신규 삽입.
- [ ] **글로벌 categories[] 갱신** — entry.categories 의 모든 항목을 글로벌 `categories[]` 에 union (insertion order)
- [ ] posts.json 워크트리에 Write
- [ ] **각 job 실행**:
  - `mkdir -p posts/{postId}/`
  - md → 인라인 변환 또는 markdown 라이브러리 → `_post-frame.html` 치환 → `posts/{postId}/{slug}.html` 기록
  - html → `inject_html_adapter.py --src --dst posts/{postId}/{slug}.html --title [--no-theme]` 호출
  - **원본 백업**: `cp ${SRC} _src/${slug}.${EXT}` + posts.json 에 `postId`, `sourcePath`, `originalFilename`, `filename` 필드 기록
- [ ] **미리보기 서버 시작** — `python3 -m http.server $PORT &` (PID 저장)
- [ ] **브라우저 자동 오픈** — OS별 분기 (start/open/xdg-open)
- [ ] **AskUserQuestion 승인 게이트** — ✅게시 / ✏️수정 / ❌취소
- [ ] 사용자 응답 처리:
  - ✅: commit + push + PR (gh 없으면 직접 push) + merge → 워크트리 정리
  - ✏️: 사용자 피드백 받아 재빌드 또는 워크트리 그대로 두고 안내 후 종료
  - ❌: kill server, worktree remove, branch delete, 종료
- [ ] **결과 출력** — 성공한 포스트 목록, skip된 항목, 블로그 URL, 반영 예상 시간
- [ ] (`--draft` 케이스) push 건너뛰고 워크트리 보존, 위치 안내

### `publish --rebuild` 분기 (재빌드 모드)

- [ ] 활성/`--profile` 프로파일 결정 (위와 동일)
- [ ] 워크트리 생성 (`BR=rebuild-${TS}`)
- [ ] posts.json 로드 → 대상 entries 결정 (slug / postId / all / `--category X`)
  - 빈 결과 → "대상 없음" 안내 후 종료
- [ ] **postId 마이그레이션** — 기존 entry 에 postId 없으면 현재 배열 순서대로 부여
- [ ] **categories 마이그레이션** — 옛 `category` 만 있으면 `categories: [category]` 로 변환 + 글로벌 `categories[]` union
- [ ] `all` 모드면 AskUserQuestion 으로 "총 N개 재빌드합니다. 계속?" 확인
- [ ] 첫 배포 판단 → 템플릿 다시 입힘
- [ ] **각 entry 처리**:
  - SOURCE 결정: (a) `_src/{slug}.{ext}` → (b) html+없음→`extract_original_html.py` (src=현재 `entry['filename']`) → (c) md+없음→skip+경고
  - `mkdir -p posts/{postId}/`
  - 빌더 호출: md→마크다운 변환+`_post-frame.html` 치환 → `posts/{postId}/{slug}.html` / html→`inject_html_adapter.py --dst posts/{postId}/{slug}.html`
  - `entry['filename']` 갱신 → `posts/{postId}/{slug}.html`
  - 기존 파일이 새 경로와 다르면 옛 경로 + 빈 부모 dir 삭제 (URL 변경 마이그레이션 1회)
  - `originalFilename` 비어있으면 entry 의 `id`/`title` 으로 추정해 채우기 (마이그레이션)
  - posts.json 의 `themeInjected`/`sourcePath` 갱신
- [ ] posts.json Write
- [ ] 미리보기 서버 시작 + 첫 3개 URL 안내
- [ ] **AskUserQuestion 승인 게이트** — ✅게시 / ✏️수정 / ❌취소
- [ ] ✅: `git diff --quiet` 인 entry 는 자동 제외 → commit (메시지: "rebuild: re-apply adapter to N posts") + push + PR + merge → 워크트리 정리
- [ ] ✏️: 워크트리 두고 안내 후 종료
- [ ] ❌: 서버 종료 → 워크트리·브랜치 삭제

### `edit` 분기

- [ ] 활성/`--profile` 프로파일 결정
- [ ] 설정 Read + REPO clone/pull
- [ ] 워크트리 생성 (`BR=edit-${slug}-${TS}`)
- [ ] target 해석:
  - 순수 정수 → `posts[].postId == int(target)` 으로 entry 검색
  - 그 외 → `posts[].id == target` 으로 entry 검색
  - 없음 → "slug / postId 일치 없음" 안내 후 종료
  - 있음 + sourcePath 없음 → "원본 백업 부재" 안내 후 종료
- [ ] entry 의 postId/slug 추출 → 새 path = `posts/{postId}/{slug}.html`
- [ ] 메타(title, category, date, blog_title) 추출 → watcher 인자로 전달
- [ ] 기본 에디터로 `_src/{slug}.{ext}` 오픈 (Windows: `start ""`, mac: `open`, linux: `xdg-open`)
- [ ] `python -m http.server $PORT` 백그라운드 시작 → 브라우저 자동 오픈 (`http://localhost:$PORT/posts/{postId}/{slug}.html`)
- [ ] `watch_and_rebuild.py` 백그라운드 시작 (engine = entry.engine, 인자 전달, --dst = posts/{postId}/{slug}.html)
- [ ] **사용자 편집 대기** — "편집 완료 후 답변하세요"
- [ ] AskUserQuestion: "이 변경을 게시할까요?" (✅게시 / ❌취소)
- [ ] ✅: watcher·서버 종료 → commit + push + PR + merge → 워크트리 정리
- [ ] ❌: watcher·서버 종료 → 워크트리·브랜치 삭제 → push 0회로 종료

### `delete` 분기

- [ ] 활성/`--profile` 프로파일 결정
- [ ] 설정 Read + REPO clone/pull
- [ ] 워크트리 생성 (`BR=delete-${TS}` — entry 확정 후 `delete-${postId}-${TS}` 로 rename 도 가능)
- [ ] posts.json 로드
- [ ] target 해석 (0-3.2 로직):
  - 순수 정수 → postId 정확 매칭
  - 그 외 → 제목 부분일치 / slug 부분일치 / SequenceMatcher 유사도 ≥0.5
- [ ] 후보 0건 → "일치 없음" 안내 후 종료
- [ ] 후보 다건 → AskUserQuestion 으로 선택 (옵션 라벨: `[#{postId}] {title} (slug={id})`)
- [ ] 삭제 미리보기 출력
- [ ] `--yes` 없으면 AskUserQuestion: "정말 삭제?" (✅/❌). ❌이면 워크트리/브랜치 삭제 후 종료
- [ ] **파일·entry 정리**:
  - `os.remove(f'posts/{postId}/{slug}.html')`
  - `os.rmdir(f'posts/{postId}')` (실패하면 경고만 — 다른 파일 남아있는 비정상)
  - `os.remove(f'_src/{slug}.{ext}')` (있을 때만)
  - posts.json `posts[]` 에서 entry pop
  - 카테고리 정리 (위 코드 예 참조)
- [ ] Pagefind 재빌드 (search 활성 시)
- [ ] 미리보기 서버 시작 + 브라우저 오픈 → 목록에서 사라진 것 확인
- [ ] AskUserQuestion: "push 할까요?" (✅/❌)
- [ ] ✅: commit (메시지: `delete: {title} (#${postId})`) → push → PR → merge → 워크트리 정리
- [ ] ❌: 워크트리·브랜치 삭제, push 0회

---

## 참고

- 설정: `~/.claude/hams-diary.json` — 스키마 `{active, profiles: {<name>: {repo, template, blogTitle?, pagesUrl?, features?}}}`. 옛 flat 형태(`{repo, template, ...}`)는 첫 호출 시 `default` 프로파일로 자동 마이그레이션 (`.bak` 백업 후).
- 템플릿: `${PLUGIN_ROOT}/skills/diary/templates/{minimal|tech|lecture|notebook|magazine}/`
- HTML 어댑터 빌더: `${PLUGIN_ROOT}/skills/diary/inject_html_adapter.py`
- HTML 어댑터 역추출: `${PLUGIN_ROOT}/skills/diary/extract_original_html.py` (재빌드 모드 fallback)
- 편집 모드 워처: `${PLUGIN_ROOT}/skills/diary/watch_and_rebuild.py`
- 레포 메타: `{REPO}/.diary-meta.json` (현재 적용된 템플릿 기록)
- 원본 백업: `{REPO}/_src/{slug}.{md|html}` (편집·재빌드 모드용)
