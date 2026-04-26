---
name: diary
description: |
  로컬에서 작성한 마크다운(.md) 혹은 HTML을 GitHub Pages 개인 블로그에 정리하는 도구.
  배포 전 로컬 미리보기 서버로 검수하고 승인 후에만 푸시한다.
  강사·연구자·개발자가 자기 글을 한 곳에 모아 운영하기 좋다.
  사용법:
    /hams:diary publish {file|dir|glob} [category]   # 게시 (단일/일괄 자동 감지)
    /hams:diary edit {slug}                           # 편집
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
4. **DB 없이 풍부한 기능** — 검색(Pagefind, 기본 ON) · 댓글(giscus, `/hams:diary giscus` 한 번 실행으로 셋업) · 라이트/다크 자동 변환 · 한글 파일명 안전 처리.

---

## 사용 방법

명령은 4개의 서브명령으로 통합되어 있다 — `publish` · `edit` · `config` · `option`.

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

`category` 가 비어있으면 AskUserQuestion 으로 선택받는다.

### `edit` — 글 고치기

```bash
/hams:diary edit {slug} [--profile {name}]
# → 에디터에서 _src/{slug}.{ext} 자동 오픈
# → 미리보기 서버 + 브라우저 자동 표시
# → 저장하면 watcher 가 자동 재빌드
# → ✅ 게시 / ❌ 취소
```

### `config` — 설정 한 곳

```bash
# 활성 프로파일 갱신
/hams:diary config show                       # 활성 + 모든 프로파일 표시
/hams:diary config repo {github-url}          # 활성 프로파일의 타겟 레포
/hams:diary config template {1-5|name}        # 활성 프로파일 사이트 디자인
/hams:diary config search {on|off}            # Pagefind 검색 (기본 on)
/hams:diary config comments off               # 댓글 끄기 (켜기는 `/hams:diary giscus` 별도 진입점)
/hams:diary config blog-title "{title}"       # 활성 프로파일 블로그 제목

# 댓글 셋업 (별도 진입점 — 디폴트 OFF, 필요할 때만 한 번 실행)
/hams:diary giscus                            # Discussions 활성화 + giscus app install + 4값 자동/반자동 추출 → 저장

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
      "features": { "search": true, "comments": { "enabled": false } }
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

**파일이 없는 경우** (publish/edit/config 호출 시): AskUserQuestion으로 첫 프로파일 repo URL 받아 다음으로 초기화:

```json
{ "active": "default", "profiles": { "default": { "repo": "<URL>", "template": "tech", "features": { "search": true, "comments": { "enabled": false } } } } }
```

`option` 호출 시에는 파일 없어도 안내만 출력 (초기화 안 함).

### 0-2. 서브명령 라우팅

인자 1번째 토큰으로 분기:

| 토큰 | 분기 |
|---|---|
| `publish` | publish 흐름 (1️⃣~🔟) |
| `edit {slug}` | edit 모드 |
| `config <sub>` | 0-3 |
| `giscus` | 0-3.1 — 댓글(giscus) 셋업 마법사 (검사·자동·1 클릭·저장) |
| `option` | 0-4 (read-only) |
| 그 외 | "알 수 없는 명령. `/hams:diary option` 으로 사용법을 확인하세요" 안내 후 종료 |

> 옛 표기(`--set-repo`, `--set-template`, `--enable-*`, `--disable-*`, `--edit`, `--rebuild-remote`, 서브명령 없는 단독 파일 인자)는 모두 **폐기됐다**. 받으면 위 "알 수 없는 명령" 분기로 안내 후 종료.

### 0-3. `config` 서브명령 분기

마이그레이션 후 `cfg['profiles'][cfg['active']]` 를 **P** (활성 프로파일) 라고 한다.

| 명령 | 동작 |
|---|---|
| `config show` | `cfg` 전체 + 활성 프로파일 강조해서 보기 좋게 출력 |
| `config repo {url}` | `P['repo'] = url` 갱신 |
| `config template {1-5\|name}` | `TEMPLATES = ['minimal','tech','lecture','notebook','magazine']`. 숫자/이름 검증 후 `P['template']` 갱신 |
| `config search on\|off` | on이면 Node.js (`npx`) 가용성 체크 + `npx -y pagefind --version` 사전 다운로드 → `P['features']['search'] = on/off` |
| `config comments on\|off` | off는 `P['features']['comments']['enabled']=false`. on은 `giscus` 서브명령(0-3.1)을 그대로 위임 호출 — 댓글은 한 진입점만 두기 위함 |
| `config blog-title "{title}"` | `P['blogTitle'] = title` |
| `config profile list` | `cfg['profiles']` 키 목록 + `cfg['active']` 표시 |
| `config profile add {name} {url}` | 이름 충돌 검사 → `cfg['profiles'][name] = {'repo': url, 'template': 'tech'}` 등록 |
| `config profile use {name}` | 존재 검증 → `cfg['active'] = name` |
| `config profile remove {name}` | 활성이면 다른 프로파일로 자동 전환. 마지막 1개면 거부 |

모든 갱신은 `json.dump(cfg, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)` 로 저장 후 종료. publish/edit는 트리거되지 않는다.

### 0-3.1 `giscus` 서브명령 — 댓글 셋업 마법사

**왜 별도 진입점인가**
- 댓글은 발행 흐름에 끼우면 사용자가 "예" 한 후 줄줄이 이어지는 외부 단계 (Discussions 활성화 + giscus app install + 4 값) 에 부담 느끼고 그냥 포기하는 경우가 흔함.
- 그래서 publish/edit 첫 호출 시 묻지 않는다 — `features.comments.enabled` **디폴트 false**.
- 댓글이 필요한 사용자만 한 번 `/hams:diary giscus` 실행 → 마법사가 자동/안내 섞어 셋업 → 다음 publish/rebuild 부터 자동 적용.

**흐름 (Claude 가 따를 순서)**

1. **활성 프로파일 P 로드.** `repo` 없으면 "먼저 `/hams:diary config repo {url}` 로 레포 등록하세요" 안내 후 종료.
2. **사용자에게 통합 안내 출력 (한 번)**:
   ```
   💬 giscus 댓글 셋업 — 약 1 분
   
   필요한 작업:
   ① 레포의 GitHub Discussions 활성화 (1 클릭)
   ② giscus GitHub App 설치 (1 클릭)
   ③ 4 개 data-* 값 — 가능한 만큼 자동, 안 되면 1 회 복사
   
   GitHub PAT 가 환경변수 GH_TOKEN / GITHUB_TOKEN 또는 gh auth 에 있으면 ①·③ 모두 자동.
   없으면 직접 링크 클릭 + 1 값 복사.
   ```
3. **PAT 감지** — `os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')`, 없으면 `gh auth token` 시도 (gh 설치돼 있을 때만).
4. **Discussions 활성화 확인 + 시도**
   - `GET https://api.github.com/repos/{owner}/{repo}` → `has_discussions` 확인
   - false 면:
     - PAT 있으면: `PATCH /repos/{owner}/{repo}` `{"has_discussions": true}` → 200 확인
     - PAT 없으면: `https://github.com/{owner}/{repo}/settings#features` 링크 출력 + AskUserQuestion("활성화 끝났으면 OK")
5. **giscus app 설치 안내 (항상 1 클릭 필수 — GitHub 정책)**
   ```
   👇 다음 링크 한 번 클릭 → "Install" 또는 "Configure" 버튼만 누르면 끝
   https://github.com/apps/giscus/installations/select_target
   ```
   AskUserQuestion("Install 끝났으면 OK / 이미 설치돼 있음 / 건너뛰기")
6. **4 개 값 추출**
   - `data-repo` = `{owner}/{repo}` (config 에서 파생, 항상 확보)
   - `data-repo-id` = `GET /repos/{owner}/{repo}` 응답의 `node_id` (공개 레포는 인증 없이도 OK)
   - `data-category` = "Announcements" (Discussions 활성화 시 자동 생성됨)
   - `data-category-id`:
     - PAT 있으면: GraphQL `repository(owner,name) { discussionCategories(first:10) { nodes { id name } } }` 에서 `name == "Announcements"` 노드의 id
     - PAT 없으면: `https://giscus.app` 링크 안내 + AskUserQuestion 으로 한 값 복사 받기
7. **저장**: `P['features']['comments'] = { enabled: true, repo, repoId, category, categoryId, mapping: 'pathname', theme: 'preferred_color_scheme', lang: 'ko' }`
8. **즉시 반영 옵션**: AskUserQuestion: "기존 글에 댓글 영역 즉시 추가 (publish --rebuild all)?"
   - Yes → publish 흐름의 `--rebuild all` 분기로 위임 (어댑터에 `--comments-*` 인자 전달됨, 5️⃣ 참조)
   - No → "다음 publish/edit 부터 자동 적용됩니다" 안내 후 종료

**오류 처리**
- 4 단계 PATCH 401 → "PAT 권한 부족 — `repo` scope 필요" 안내
- 5 단계 사용자 "건너뛰기" → `enabled: false` 로 저장하고 종료 (다시 실행 가능)
- 6 단계 GraphQL 401 → 6단계 PAT 없음 분기로 폴백
- repo 가 private 인데 PAT 없으면 → "private 레포는 PAT 필수" 안내 후 종료

**참고 — `/hams:diary config comments on` 도 위 마법사를 그대로 실행** (별칭 관계). `off` 만 별도: `P['features']['comments']['enabled'] = false` 저장 후 종료.

옛 `config comments on` 시 데이터 없을 때 안내문 (호환용):
```
1. https://giscus.app 방문
2. Repository 입력 (예: owner/blog)
3. Discussion category 선택 (Announcements 권장)
4. 페이지 하단의 data-* 4개 값(repo / repo-id / category / category-id) 복사
5. /hams:diary giscus 다시 실행해 입력
```

### 0-4. `option` 서브명령 (read-only)

어떤 외부 동작(git/clone/server/AskUserQuestion/파일 갱신)도 발생시키지 않고 다음을 출력하고 종료:

```
🐹 /hams:diary — 로컬 마크다운/HTML → GitHub Pages 개인 블로그

📌 서브명령
  publish {file|dir|glob} [category] [--플래그…]      # 게시 (단일/일괄 자동 감지)
  edit {slug} [--profile {name}]                       # 기존 글 편집 (라이브 미리보기)
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
  comments {on|off}                    # giscus 댓글 (on은 대화형, 4개 data-* 값 입력)
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
  /hams:diary publish ./drafts/ 일상 --overwrite
  /hams:diary publish ./사이트.html 기술 --no-theme
  /hams:diary publish ./post.md 일상 --profile diary       # 1회 임시 override
  /hams:diary edit hello-world
  /hams:diary edit hello-world --profile diary
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
    comments:    <on|off> (기본 off — `/hams:diary giscus` 한 번 실행으로 셋업)

💾 옛 flat 형태({repo, template, ...})는 첫 호출 시 자동으로 default 프로파일로 변환되며 ~/.claude/hams-diary.json.bak 에 백업됩니다.

⚠️  옛 표기(--set-repo / --set-template / --enable-* / --disable-* / --edit / --rebuild-remote / 서브명령 없는 단독 파일 인자)는 모두 폐기됐습니다.

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
| `FEATURES` | `P['features']` (없으면 `{search: true, comments: {enabled: false}}` — 검색만 ON, 댓글은 `/hams:diary giscus` 로 별도 셋업) |
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
  "category": "<인자 또는 추론>",
  "tags": [...],
  "summary": "..."
}
```

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
- **category**: CLI 인자 우선, 없으면 AskUserQuestion 으로 사용자에게 묻기 (기존 카테고리 + 신규)

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
  "id": "kebab-slug",
  "title": "...",
  "date": "YYYY-MM-DD",
  "category": "...",
  "summary": "...",
  "filename": "posts/{slug}.html",
  "tags": ["..."],
  "engine": "md" | "html",
  "themeInjected": true | false,
  "sourcePath": "_src/{slug}.{ext}",
  "originalFilename": "원본_파일명.html"
}
```

> **`originalFilename` 마이그레이션** — 기존 항목에 이 필드가 없는 경우, 다음 배포·재빌드 시 자동으로 채워진다. 1순위 매칭은 그냥 건너뛰고 2순위(slug)로 폴백되므로 옛 데이터 손상 없음.

`category` 가 `categories[]` 에 없으면 추가.

---

## 5️⃣ 포스트 HTML 생성 (워크트리에 기록)

### MD 엔진

```bash
# 마크다운 → HTML 변환 (기존 변환 규칙 그대로, 인라인 Python markdown 또는 정규식)
# 변환된 HTML 을 _post-frame.html 의 {{POST_HTML}} 자리에 치환
sed -e "s|{{POST_TITLE}}|${TITLE}|g" \
    -e "s|{{POST_CATEGORY}}|${CAT}|g" \
    -e "s|{{POST_DATE}}|${DATE}|g" \
    -e "s|{{POST_HTML}}|${BODY_HTML}|g" \
    -e "s|{{BLOG_TITLE}}|${BLOG_TITLE}|g" \
    _post-frame.html > posts/${slug}.html
```

(실제로는 sed 보다 Python 한 줄로 read+replace+write 하는 게 안전함, 본문에 특수문자 있을 수 있어서)

### HTML 엔진

```bash
# inject_html_adapter.py 호출
# 1) features.comments.enabled === true 이고 4개 값이 모두 있으면 --comments-* 인자 전달
COMMENTS_ARGS=""
if [ "$FEATURES_COMMENTS_ENABLED" = "true" ] \
   && [ -n "$COMMENTS_REPO" ] && [ -n "$COMMENTS_REPO_ID" ] \
   && [ -n "$COMMENTS_CATEGORY" ] && [ -n "$COMMENTS_CATEGORY_ID" ]; then
  COMMENTS_ARGS="--comments-repo $COMMENTS_REPO --comments-repo-id $COMMENTS_REPO_ID --comments-category $COMMENTS_CATEGORY --comments-category-id $COMMENTS_CATEGORY_ID"
fi

# 2) 폭 모드 — CLI 플래그 또는 (--rebuild 시) posts.json[].fit 에서 결정
#    publish 시: --fit-viewport / --scale-up 인자에서 추출
#    rebuild 시: 기존 entry 의 fit 필드 (없으면 native)
FIT_ARG=""
case "$FIT_MODE" in
  viewport) FIT_ARG="--fit-viewport" ;;
  scale)    FIT_ARG="--scale-up" ;;
  *)        FIT_ARG="" ;;
esac

python3 "${PLUGIN_ROOT}/skills/diary/inject_html_adapter.py" \
  --src "${SRC}" --dst "posts/${slug}.html" --title "${TITLE}" \
  ${NO_THEME:+--no-theme} $COMMENTS_ARGS $FIT_ARG

# 3) 결과 fit_mode 를 posts.json 의 해당 entry 에 저장 (재빌드 시 그대로 재현)
#    {"id":..., "fit":"native|viewport|scale", ...}
```

배치 모드는 `--map` JSON 으로 한 번에 호출 가능.

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

## 5️⃣.5 기능 토글 적용 (검색·댓글)

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

### `{{COMMENTS_BLOCK}}` (_post-frame.html — MD 엔진) / `inject_html_adapter.py --comments-*` (HTML 엔진)

조건: `features.comments.enabled === true` **AND** 4 개 data-* 값 (`repo`, `repoId`, `category`, `categoryId`) 이 모두 채워져 있을 때만 giscus 블록 emit.

- **디폴트는 `enabled: false`** — 댓글이 필요한 사용자만 한 번 `/hams:diary giscus` 실행해서 셋업 (마법사 흐름은 0-3.1 참조)
- 셋업 후엔 publish/edit/--rebuild 모두 자동으로 댓글 블록 포함
- 4 개 값 중 하나라도 비면: emit 안 하고 빌드 로그에 1 회 안내 ("`/hams:diary giscus` 로 셋업하세요")

**MD 엔진**: `_post-frame.html` 의 `{{COMMENTS_BLOCK}}` 자리에 치환.
**HTML 엔진**: 어댑터의 `--comments-repo / --repo-id / --category / --category-id` 인자로 전달 → `</body>` 직전 `<!-- hamstern:comments:start --> ... :end -->` 마커 블록으로 주입 (idempotent).

조건 충족 시 emit 되는 블록 형태 (디자인: 옵션 C — 간소 헤더 + border-top + 다크/라이트 톤 패널):
```html
<style id="osd-comments-style">
  .osd-comments { max-width: 800px; margin: 56px auto 40px; padding: 28px 24px 32px;
                  border-top: 1px solid rgba(127,127,127,0.18); border-radius: 8px; }
  html[data-osd-theme="light"] .osd-comments { background: rgba(0,0,0,0.025); border-top-color: rgba(0,0,0,0.10); }
  html[data-osd-theme="dark"]  .osd-comments,
  html:not([data-osd-theme])   .osd-comments { background: rgba(255,255,255,0.03); border-top-color: rgba(255,255,255,0.08); }
  .osd-comments__h { font: 600 13px/1.4 -apple-system, ...; letter-spacing: 1.2px;
                     text-transform: uppercase; margin: 0 0 16px; color: rgba(127,127,127,0.85); }
</style>
<section class="osd-comments" aria-label="comments">
  <h4 class="osd-comments__h">토론</h4>
  <div id="osd-giscus-mount"></div>
</section>
<script>
(function(){
  function getTheme(){
    try { return localStorage.getItem('blog-theme')
              || document.documentElement.getAttribute('data-osd-theme')
              || 'dark'; } catch(e){ return 'dark'; }
  }
  function emit(t){
    var iframe = document.querySelector('iframe.giscus-frame');
    if (iframe && iframe.contentWindow) {
      iframe.contentWindow.postMessage(
        { giscus: { setConfig: { theme: t === 'dark' ? 'dark' : 'light' } } },
        'https://giscus.app'
      );
    }
  }
  // (1) script 동적 생성 — 첫 페인트부터 블로그 테마 적용 (OS 무시)
  var s = document.createElement('script');
  s.src = 'https://giscus.app/client.js';
  s.setAttribute('data-repo', '{{COMMENTS_REPO}}');
  s.setAttribute('data-repo-id', '{{COMMENTS_REPO_ID}}');
  s.setAttribute('data-category', '{{COMMENTS_CATEGORY}}');
  s.setAttribute('data-category-id', '{{COMMENTS_CATEGORY_ID}}');
  s.setAttribute('data-mapping', 'pathname');
  s.setAttribute('data-strict', '0');
  s.setAttribute('data-reactions-enabled', '1');
  s.setAttribute('data-emit-metadata', '0');
  s.setAttribute('data-input-position', 'bottom');
  s.setAttribute('data-theme', getTheme() === 'light' ? 'light' : 'dark');
  s.setAttribute('data-lang', 'ko');
  s.crossOrigin = 'anonymous';
  s.async = true;
  document.getElementById('osd-giscus-mount').appendChild(s);

  // (2) iframe ready 시 한번 더 동기화 (보호장치)
  window.addEventListener('message', function(e){
    if (e.origin !== 'https://giscus.app') return;
    emit(getTheme());
  });

  // (3) 블로그 테마 토글 시 동기화
  var orig = window.__osdSetTheme || function(){};
  window.__osdSetTheme = function(t){ orig(t); emit(t); };
})();
</script>
```

**테마 동기화 정책**: `data-theme` 을 빌드 시 고정하지 않고 페이지 로드 시점에 `localStorage('blog-theme')` 우선, 없으면 `data-osd-theme` attribute → 'dark' 폴백. **OS prefers-color-scheme 무시** — 블로그 토글이 진실의 소스. (3) 단계로 toggle 즉시 반영, (2) 단계로 iframe ready 시 한번 더 보장.

조건 미충족 (`enabled === false` 또는 4 개 값 중 하나라도 비어있음):
```html
<!-- comments disabled -->
```

각 템플릿의 기존 테마 토글 핸들러는 `if (window.__osdSetTheme) window.__osdSetTheme(next);` 한 줄을 추가해 giscus 동기화 hook 을 호출하도록 한다 (이 줄이 있으면 댓글 비활성 시에도 무해).

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
   · {slug1} — {title1}
   · {slug2} — {title2}
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
[1] /hams:diary edit msa-k8s-websocket
[2] 레포 clone/pull → 워크트리 생성
[3] posts.json 에서 slug 검색 → sourcePath 확인
    sourcePath 없음 → "이 포스트는 _src/ 백업이 없습니다.
                       원본 파일을 다시 /hams:diary publish {file} --overwrite 로
                       배포해 주세요." 안내 후 종료
[4] 기본 에디터로 _src/{slug}.{ext} 열기
[5] python -m http.server $PORT 백그라운드 실행
[6] 브라우저 자동 오픈 → http://localhost:8765/posts/{slug}.html
[7] watch_and_rebuild.py 백그라운드 실행
    → _src/{slug}.{ext} mtime 변경 감지 시
    → 적절한 빌더 호출 (md → 변환, html → inject_html_adapter)
    → posts/{slug}.html 갱신 + 콘솔에 [HH:MM:SS] rebuilt 출력
[8] 사용자가 에디터에서 저장할 때마다 (5)~(7)의 자동 빌드 발생
    브라우저에서 F5 로 변경 확인
[9] 편집 완료 후 AskUserQuestion: "이 변경을 게시할까요?"
       ✅ 게시 → commit + push + PR + merge (커밋 메시지: "edit: {title}")
       ❌ 취소 → 워크트리/브랜치 삭제, push 0회
[10] watcher 종료 + 서버 종료 + 워크트리 정리
```

### `_src/` 가 없는 기존 포스트

`/hams:diary` v1 시절(즉, `_src/` 백업 도입 이전)에 게시된 포스트는 `posts/{slug}.html` 의 빌드 결과만 레포에 있다. 처리 경로:

- **HTML 시뮬레이터**: `publish --rebuild {slug}` 가 자동으로 `extract_original_html.py` 를 돌려 어댑터 마커 사이 블록을 제거 → 원본 복원 → `_src/` 에 저장 → 어댑터 재주입. 손에 원본 파일 없어도 됨.
- **MD 였던 포스트**: 역변환 비신뢰 (HTML→MD 손실). 원본 `.md` 가 손에 있다면 `--overwrite` 로 재배포해 `_src/` 백업 생성. 없으면 skip + 경고.

가장 안전한 길: 첫 게시 후엔 원본을 로컬에서 보관하지 말고, 항상 `_src/` 를 진실의 원본으로 사용한다.

### 명령어 호출 예

```bash
# Python watcher 호출 형태 (md)
python3 "${PLUGIN_ROOT}/skills/diary/watch_and_rebuild.py" \
  --src "_src/${slug}.md" --dst "posts/${slug}.html" \
  --engine md --frame "_post-frame.html" \
  --title "${TITLE}" --category "${CAT}" \
  --date "${DATE}" --blog-title "${BLOG_TITLE}" &
WATCHER_PID=$!

# Python watcher 호출 형태 (html)
python3 "${PLUGIN_ROOT}/skills/diary/watch_and_rebuild.py" \
  --src "_src/${slug}.html" --dst "posts/${slug}.html" \
  --engine html --title "${TITLE}" \
  ${NO_THEME:+--no-theme} &
WATCHER_PID=$!
```

### 메타데이터(제목·요약·카테고리·태그) 편집

본문이 아닌 메타만 바꾸고 싶으면 `_src/` 의 frontmatter(MD) 또는 `<title>`/`<meta>` 태그(HTML)를 수정하면 watcher 가 추출해 posts.json 도 갱신한다 (재빌드 시 메타 추출 로직이 동일하게 돌기 때문).

---

## 🔄 재빌드 모드 (`publish --rebuild`)

**언제 쓰나** — 어댑터 로직이 바뀌었거나 새로운 시그니처/테마/기능 토글을 기존 모든 글에 일괄 적용하고 싶을 때. 로컬에 원본 파일이 있을 필요가 없다 (레포의 `_src/` 또는 `posts/{slug}.html` 역추출이 소스가 됨).

### 호출 형태

```bash
/hams:diary publish --rebuild msa-k8s-websocket          # 단일
/hams:diary publish --rebuild all                        # 전체
/hams:diary publish --rebuild --category msa             # 카테고리
```

### 흐름

```
[1] 설정 Read → REPO clone/pull → 워크트리 생성 (BR=rebuild-{TS})
[2] posts.json 로드 → 대상 entries 결정:
    - {slug}      : 단일 entry (없으면 종료)
    - all         : posts[] 전체
    - --category X: posts[].category == X 인 것들
[3] 첫 배포 판단 (index.html 부재 / 템플릿 변경) → 템플릿 다시 입힘
[4] 각 entry 에 대해 SOURCE 결정 (우선순위):
    a. _src/{slug}.{ext} 존재 → 그대로 사용
    b. engine == html, _src/ 없음:
       extract_original_html.py --src posts/{slug}.html --dst _src/{slug}.html
       → 원본 복원 후 (a) 와 같이 사용. _src/ 없는 옛날 글의 자가치유.
    c. engine == md, _src/ 없음 → skip + 경고 ("MD 역변환 비신뢰; 원본 .md 로 --overwrite 재배포 필요")
[5] SOURCE 로 빌더 재호출:
    - md  → markdown→html 변환 → _post-frame.html 치환 → posts/{slug}.html
    - html → inject_html_adapter.py --src _src/{slug}.html --dst posts/{slug}.html --title "{title}"
[6] posts.json 의 themeInjected/sourcePath/originalFilename(없으면 채움) 갱신
[7] 미리보기 서버 + 브라우저 오픈 → 첫 N개 (3개 권장) URL 안내
[8] AskUserQuestion 승인 게이트:
    ✅ 게시 → commit + push + PR + merge (메시지: "rebuild: re-apply adapter to N posts")
    ✏️ 수정 → 워크트리 두고 안내 후 종료 (사용자 직접 수정)
    ❌ 취소 → 워크트리/브랜치 삭제, push 0회
[9] 워크트리 정리
```

### 명령어 호출 예

```bash
# extract (HTML 역추출)
python3 "${PLUGIN_ROOT}/skills/diary/extract_original_html.py" \
  --src "posts/${slug}.html" --dst "_src/${slug}.html"

# 그 후 평소처럼 inject
python3 "${PLUGIN_ROOT}/skills/diary/inject_html_adapter.py" \
  --src "_src/${slug}.html" --dst "posts/${slug}.html" \
  --title "${TITLE}" ${NO_THEME:+--no-theme}
```

### 안전장치

- 변경 없는 entry (재빌드 후 `posts/{slug}.html` 바이트가 동일) 는 commit 에서 자동 제외 (`git diff --quiet`)
- `all` 모드는 처리 전 AskUserQuestion 로 "총 N개 재빌드합니다. 계속?" 확인
- MD entry skip 시 결과 출력에서 `[skip] {slug} (MD, _src/ 없음)` 로 명시

---

## 강의자료 특화 향후 확장 (미구현)

다음은 본 스킬에는 포함되어 있지 않지만 강의자료 운영에 유용한 기능들. 백로그.

1. **시리즈 그룹핑** — `series` 필드로 "MSA 강의 1주차" 같은 묶음 자동 생성
2. **공개 토글** — `published: false` 로 게시는 했지만 목록에서 숨김
3. **선수 학습 링크** — `prereq: ["msa-k8s-websocket"]`
4. **slide 모드** — `?mode=slide` 로 발표용 풀스크린 변환
5. **자동 ToC** — H2/H3 구조에서 우측 sticky ToC
6. **댓글/Q&A** — utterances·giscus 임베드

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

- [ ] **인자 토큰 분류** — `publish` / `edit` / `config <sub>` / `option` / 그 외
- [ ] **설정 자동 마이그레이션** — `~/.claude/hams-diary.json` Read → flat schema(`{repo, template, ...}`)면 `.bak` 백업 후 `{active, profiles}` 로 변환 (0-1 로직)
- [ ] 그 외 토큰이면 "알 수 없는 명령. `/hams:diary option` 으로 사용법을 확인하세요" 출력 후 종료

### `option` 분기

- [ ] 0-4의 출력 양식 그대로 출력. 어떤 외부 동작도 안 함. 종료.

### `config` 분기

- [ ] `cfg['profiles'][cfg['active']]` 를 P로 가져옴 (없으면 P = {})
- [ ] 0-3 표대로 처리:
  - `show` → cfg 보기 좋게 출력
  - `repo` / `template` / `search` / `comments` / `blog-title` → P 갱신
  - `profile list` / `profile add` / `profile use` / `profile remove` → cfg 직접 갱신
- [ ] `json.dump(cfg, p, ensure_ascii=False, indent=2)` 저장
- [ ] 종료 (publish/edit 안 트리거)

### `publish` 분기

- [ ] 인자에서 `--profile {name}` 추출 → 없으면 `cfg['active']`
- [ ] `cfg['profiles'][name]` 검증 (없으면 에러 종료: "프로파일 없음. /hams:diary config profile list 로 확인")
- [ ] 활성 프로파일에서 PROFILE_NAME, REPO_URL, OWNER, NAME, PAGES_URL, TEMPLATE, BLOG_TITLE, FEATURES, LOCAL_DIR, WORKTREE_DIR 결정 (0-5)
- [ ] **JOBS 배열 구성** — 단일/디렉토리/글롭 분기, 한글 파일명 PowerShell 폴백
- [ ] 각 job 메타 추출 (title/summary/tags/slug/category, **originalFilename**)
- [ ] category 미결정시 AskUserQuestion
- [ ] LOCAL_DIR clone/pull
- [ ] WORKTREE_DIR worktree add (`BR=post-preview-${TS}`)
- [ ] 첫 배포 판단 (index.html 부재 또는 .diary-meta.json template 다름) → 템플릿 복사 + {{BLOG_*}} 치환 + .nojekyll
- [ ] BLOG_TITLE 등 미설정시 AskUserQuestion → P에 저장
- [ ] posts.json 로드 (없으면 빈 구조)
- [ ] **각 job: 3단계 매칭** (originalFilename → slug → 제목 유사도 ≥0.85+같은 engine), 매칭 발견 시 기존 slug 재사용. `--overwrite` 미설정이면 skip, 설정이면 in-place 교체. 매칭 없음이면 신규 삽입.
- [ ] posts.json 워크트리에 Write
- [ ] **각 job 실행**:
  - md → 인라인 변환 또는 markdown 라이브러리 → `_post-frame.html` 치환 → `posts/{slug}.html` 기록
  - html → `inject_html_adapter.py --src --dst --title [--no-theme]` 호출
  - **원본 백업**: `cp ${SRC} _src/${slug}.${EXT}` + posts.json 에 `sourcePath` 와 **`originalFilename`** 필드 기록
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
- [ ] posts.json 로드 → 대상 entries 결정 (slug / all / `--category X`)
  - 빈 결과 → "대상 없음" 안내 후 종료
- [ ] `all` 모드면 AskUserQuestion 으로 "총 N개 재빌드합니다. 계속?" 확인
- [ ] 첫 배포 판단 → 템플릿 다시 입힘
- [ ] **각 entry 처리**:
  - SOURCE 결정: (a) `_src/{slug}.{ext}` → (b) html+없음→`extract_original_html.py` → (c) md+없음→skip+경고
  - 빌더 호출: md→마크다운 변환+`_post-frame.html` 치환 / html→`inject_html_adapter.py`
  - `originalFilename` 비어있으면 entry 의 `filename`/`title` 으로 추정해 채우기 (마이그레이션)
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
- [ ] posts.json 에서 `id == slug` 검색 → entry 추출
  - 없음 → "slug 일치 없음" 안내 후 종료
  - 있음 + sourcePath 없음 → "원본 백업 부재" 안내 후 종료
- [ ] 메타(title, category, date, blog_title) 추출 → watcher 인자로 전달
- [ ] 기본 에디터로 `_src/{slug}.{ext}` 오픈 (Windows: `start ""`, mac: `open`, linux: `xdg-open`)
- [ ] `python -m http.server $PORT` 백그라운드 시작 → 브라우저 자동 오픈 (`http://localhost:$PORT/posts/{slug}.html`)
- [ ] `watch_and_rebuild.py` 백그라운드 시작 (engine = entry.engine, 인자 전달)
- [ ] **사용자 편집 대기** — "편집 완료 후 답변하세요"
- [ ] AskUserQuestion: "이 변경을 게시할까요?" (✅게시 / ❌취소)
- [ ] ✅: watcher·서버 종료 → commit + push + PR + merge → 워크트리 정리
- [ ] ❌: watcher·서버 종료 → 워크트리·브랜치 삭제 → push 0회로 종료

---

## 참고

- 설정: `~/.claude/hams-diary.json` — 스키마 `{active, profiles: {<name>: {repo, template, blogTitle?, pagesUrl?, features?}}}`. 옛 flat 형태(`{repo, template, ...}`)는 첫 호출 시 `default` 프로파일로 자동 마이그레이션 (`.bak` 백업 후).
- 템플릿: `${PLUGIN_ROOT}/skills/diary/templates/{minimal|tech|lecture|notebook|magazine}/`
- HTML 어댑터 빌더: `${PLUGIN_ROOT}/skills/diary/inject_html_adapter.py`
- HTML 어댑터 역추출: `${PLUGIN_ROOT}/skills/diary/extract_original_html.py` (재빌드 모드 fallback)
- 편집 모드 워처: `${PLUGIN_ROOT}/skills/diary/watch_and_rebuild.py`
- 레포 메타: `{REPO}/.diary-meta.json` (현재 적용된 템플릿 기록)
- 원본 백업: `{REPO}/_src/{slug}.{md|html}` (편집·재빌드 모드용)
