---
name: diary
description: |
  로컬에서 작성한 마크다운(.md) 혹은 HTML을 GitHub Pages 개인 블로그에 정리하는 도구.
  배포 전 로컬 미리보기 서버로 검수하고 승인 후에만 푸시한다.
  강사·연구자·개발자가 자기 글을 한 곳에 모아 운영하기 좋다.
  사용법:
    /hams:diary publish {file|dir|glob} [category]   # 게시 (단일/일괄 자동 감지)
    /hams:diary edit {slug}                           # 편집
    /hams:diary config <subcommand>                   # 설정
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
4. **DB 없이 풍부한 기능** — opt-in 검색(Pagefind) · 댓글(giscus) · 라이트/다크 자동 변환 · 한글 파일명 안전 처리.

---

## 사용 방법

명령은 3개의 서브명령으로 통합되어 있다.

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
--no-theme         # HTML 어댑터 주입 끄기
--overwrite        # 기존 동일 글 덮어쓰기 (originalFilename → slug → 제목 매칭)
--draft            # 푸시 안 하고 워크트리만 남김
--preview-port N   # 미리보기 포트 (기본 8765)
--rebuild [slug|all|--category name]   # 사이트 기존 글 재테마/재시그니처
```

`category` 가 비어있으면 AskUserQuestion 으로 선택받는다.

### `edit` — 글 고치기

```bash
/hams:diary edit {slug}
# → 에디터에서 _src/{slug}.{ext} 자동 오픈
# → 미리보기 서버 + 브라우저 자동 표시
# → 저장하면 watcher 가 자동 재빌드
# → ✅ 게시 / ❌ 취소
```

### `config` — 설정 한 곳

```bash
/hams:diary config show                       # 현재 설정 표시
/hams:diary config repo {github-url}          # 타겟 레포 (1회 필수)
/hams:diary config template {1-5|name}        # 사이트 디자인 변경
/hams:diary config search {on|off}            # Pagefind 풀텍스트 검색
/hams:diary config comments {on|off}          # giscus 댓글 (on 은 대화형)
/hams:diary config blog-title "{title}"       # 블로그 제목 변경
```

---

## 하위호환 (구 명령어)

이전 플래그 형태도 그대로 인식되어 동등한 신 명령으로 라우팅된다 — 점진적 전환을 위함.

| 구 명령 | 신 명령 |
|---|---|
| `/hams:diary {file} [cat]` (서브명령 없음) | `/hams:diary publish {file} [cat]` |
| `/hams:diary --edit {slug}` | `/hams:diary edit {slug}` |
| `/hams:diary --set-repo {url}` | `/hams:diary config repo {url}` |
| `/hams:diary --set-template {n}` | `/hams:diary config template {n}` |
| `/hams:diary --enable-search` / `--disable-search` | `/hams:diary config search {on\|off}` |
| `/hams:diary --enable-comments` / `--disable-comments` | `/hams:diary config comments {on\|off}` |
| `/hams:diary --rebuild-remote ...` | `/hams:diary publish --rebuild ...` |

내부 동작은 동일하므로 기존 워크플로우는 그대로 작동한다. README/문서는 신 명령 기준으로 작성한다.

# 기능 토글 (opt-in)
/hams:diary --enable-search                     # Pagefind 풀텍스트 검색 켜기
/hams:diary --disable-search                    # 검색 끄기
/hams:diary --enable-comments                   # giscus 댓글 켜기 (대화형)
/hams:diary --disable-comments                  # 댓글 끄기
```

---

## 0️⃣ 인자 해석 & 설정 확인

### `--set-repo {url}` 분기

```bash
python3 -c "import json; d={'repo':'<URL>','template':'tech'}; \
  json.dump(d, open('$HOME/.claude/hams-diary.json','w'))"
```
저장 후 종료. URL 파싱은 기존과 동일 (`https://github.com/owner/repo.git` → owner/repo).

### `--set-template {value}` 분기

```bash
# 1-5 숫자 또는 이름(minimal/tech/lecture/notebook/magazine) 입력 허용
TEMPLATES = ['minimal','tech','lecture','notebook','magazine']
# 사용자 입력 검증 → ~/.claude/hams-diary.json 의 template 필드만 업데이트
```

저장 후 종료.

### `--enable-search` / `--disable-search` 분기

```bash
# 1) Node.js 가용성 체크 (활성화 시에만)
if ! command -v npx >/dev/null 2>&1; then
  echo "❌ Node.js 18+ 가 필요합니다. https://nodejs.org 에서 설치 후 재시도하세요."
  exit 1
fi
npx -y pagefind --version 2>/dev/null   # 사전 다운로드(첫 실행만 시간 걸림)

# 2) features.search 토글
python3 -c "import json; p='$HOME/.claude/hams-diary.json'; \
  d=json.load(open(p)); d.setdefault('features',{}); \
  d['features']['search']=$ENABLE; json.dump(d, open(p,'w'))"
```

저장 후 종료. `$ENABLE` 은 enable=true / disable=false.

### `--enable-comments` / `--disable-comments` 분기

`--disable-comments`: `features.comments.enabled=false` 만 갱신 후 종료.

`--enable-comments`:
1. AskUserQuestion: "giscus 설정값이 있나요?"
   - 없음 → 안내 출력 후 종료:
     ```
     1. https://giscus.app 방문
     2. Repository 입력 (예: owner/blog)
     3. Discussion category 선택 (Announcements 권장)
     4. 페이지 하단의 data-* 4개 값(repo / repo-id / category / category-id)을 복사
     5. /hams:diary --enable-comments 다시 실행해 입력
     ```
   - 있음 → AskUserQuestion 4번 (data-repo, data-repo-id, data-category, data-category-id)
2. `features.comments` 객체에 저장:
   ```json
   { "enabled": true, "repo": "...", "repoId": "...",
     "category": "...", "categoryId": "...",
     "mapping": "pathname", "theme": "preferred_color_scheme" }
   ```
3. 저장 후 종료. 다음 배포부터 모든 포스트에 giscus 임베드.

### 일반 실행

`~/.claude/hams-diary.json` Read:
```json
{
  "repo": "...",
  "template": "tech",
  "pagesUrl": "...",
  "features": {
    "search": false,
    "comments": { "enabled": false }
  }
}
```

파일 없으면 AskUserQuestion 으로 URL 입력받고 저장 → 계속.
`template` 필드 없으면 첫 배포 시 AskUserQuestion 으로 5개 중 선택받고 저장.

추출 변수:
| 변수 | 값 |
|---|---|
| `REPO_URL` | `repo` 필드 |
| `REPO_OWNER`, `REPO_NAME` | URL 파싱 |
| `PAGES_URL` | `pagesUrl` 필드 또는 `https://${OWNER}.github.io/${NAME}/` |
| `TEMPLATE` | `template` 필드 (기본 `tech`) |
| `LOCAL_DIR` | `/tmp/${REPO_NAME}` |
| `WORKTREE_DIR` | `/tmp/${REPO_NAME}-preview-${TS}` (배포마다 새로 생성) |

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
python3 "${PLUGIN_ROOT}/skills/diary/inject_html_adapter.py" \
  --src "${SRC}" --dst "posts/${slug}.html" --title "${TITLE}" \
  ${NO_THEME:+--no-theme}
```

배치 모드는 `--map` JSON 으로 한 번에 호출 가능.

> 어댑터는 원본 HTML 의 dominant background 를 자동 감지해 `data-osd-source-theme="light|dark"` 로 표시한다. 사용자가 선택한 블로그 테마와 톤이 다를 때만 invert 필터를 걸어 자동 변환하므로, 라이트 톤 원본(예: 베이지) 도 다크 블로그에서 자연스럽게 보인다. (감지 실패 시 기존 동작인 `dark` 가정.)

### 원본 소스 보존 (`_src/`) + originalFilename 기록

배포 시 원본 파일을 워크트리의 `_src/{slug}.{ext}` 로도 복사한다. 나중에 `--edit {slug}` 또는 `--rebuild-remote` 시 이 원본을 사용한다.

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

### `{{COMMENTS_BLOCK}}` (_post-frame.html 안, 본문 직후)

`features.comments.enabled === true`:
```html
<section class="comments">
  <h3>💬 토론</h3>
  <script src="https://giscus.app/client.js"
          data-repo="{{COMMENTS_REPO}}"
          data-repo-id="{{COMMENTS_REPO_ID}}"
          data-category="{{COMMENTS_CATEGORY}}"
          data-category-id="{{COMMENTS_CATEGORY_ID}}"
          data-mapping="pathname" data-strict="0"
          data-reactions-enabled="1" data-emit-metadata="0"
          data-input-position="bottom"
          data-theme="preferred_color_scheme" data-lang="ko"
          crossorigin="anonymous" async></script>
</section>
<script>
  // 블로그 테마 토글 시 giscus iframe 도 동기화
  (function(){
    var orig = window.__osdSetTheme || function(){};
    window.__osdSetTheme = function(t){
      orig(t);
      var iframe = document.querySelector('iframe.giscus-frame');
      if (iframe) iframe.contentWindow.postMessage(
        { giscus: { setConfig: { theme: t === 'dark' ? 'dark' : 'light' } } },
        'https://giscus.app'
      );
    };
  })();
</script>
```

`features.comments.enabled === false`:
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

## ✏️ 편집 모드 (`--edit {slug}`)

기존 게시글의 내용·제목·태그를 고치는 가장 빠른 방법. 워크트리·미리보기·자동 재빌드·승인 게이트가 한 번에 묶여 있어 "오타 1개 고치고 게시" 가 30초 안에 끝난다.

### 흐름

```
[1] /hams:diary --edit msa-k8s-websocket
[2] 레포 clone/pull → 워크트리 생성
[3] posts.json 에서 slug 검색 → sourcePath 확인
    sourcePath 없음 → "이 포스트는 _src/ 백업이 없습니다.
                       원본 파일을 다시 /hams:diary {file} --overwrite 로
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

- **HTML 시뮬레이터**: `--rebuild-remote {slug}` 가 자동으로 `extract_original_html.py` 를 돌려 어댑터 마커 사이 블록을 제거 → 원본 복원 → `_src/` 에 저장 → 어댑터 재주입. 손에 원본 파일 없어도 됨.
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

## 🔄 재빌드 모드 (`--rebuild-remote`)

**언제 쓰나** — 어댑터 로직이 바뀌었거나 새로운 시그니처/테마/기능 토글을 기존 모든 글에 일괄 적용하고 싶을 때. 로컬에 원본 파일이 있을 필요가 없다 (레포의 `_src/` 또는 `posts/{slug}.html` 역추출이 소스가 됨).

### 호출 형태

```bash
/hams:diary --rebuild-remote msa-k8s-websocket          # 단일
/hams:diary --rebuild-remote all                        # 전체
/hams:diary --rebuild-remote --category msa             # 카테고리
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

- [ ] **인자 파싱** — `--set-repo`, `--set-template`, `--edit`, `--rebuild-remote`, `--no-theme`, `--overwrite`, `--draft`, `--preview-port`, 위치 인자(파일/디렉토리/글롭, 카테고리)
- [ ] `--set-repo` 분기 — JSON 저장 후 종료
- [ ] `--set-template` 분기 — JSON 갱신 후 종료
- [ ] `--edit {slug}` 분기 — 편집 모드 흐름(아래 별도 섹션)으로 진입
- [ ] `--rebuild-remote {slug|all|--category X}` 분기 — 재빌드 모드 흐름(아래 별도 섹션)으로 진입
- [ ] `~/.claude/hams-diary.json` Read (없으면 AskUserQuestion)
- [ ] REPO_URL, OWNER, NAME, PAGES_URL, TEMPLATE, LOCAL_DIR, WORKTREE_DIR, BASE_BRANCH 결정
- [ ] **JOBS 배열 구성** — 단일/디렉토리/글롭 분기, 한글 파일명 PowerShell 폴백
- [ ] 각 job 메타 추출 (title/summary/tags/slug/category, **originalFilename**)
- [ ] category 미결정시 AskUserQuestion
- [ ] LOCAL_DIR clone/pull
- [ ] WORKTREE_DIR worktree add
- [ ] 첫 배포 판단 (index.html 부재 또는 .diary-meta.json template 다름) → 템플릿 복사 + {{BLOG_*}} 치환 + .nojekyll
- [ ] BLOG_TITLE 등 미설정시 AskUserQuestion
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
  - ✅: 9단계 (commit/push/PR/merge)
  - ✏️: 사용자 피드백 받아 재빌드 또는 워크트리 그대로 두고 안내 후 종료
  - ❌: kill server, worktree remove, branch delete, 종료
- [ ] (✅ 케이스) commit + push + PR (gh 없으면 직접 push) + merge
- [ ] (✅ 케이스) 워크트리/브랜치 정리
- [ ] **결과 출력** — 성공한 포스트 목록, skip된 항목, 블로그 URL, 반영 예상 시간
- [ ] (--draft 케이스) push 건너뛰고 워크트리 보존, 위치 안내

### `--edit {slug}` 모드 체크리스트

- [ ] 설정 Read + REPO clone/pull (위와 동일)
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

### `--rebuild-remote` 모드 체크리스트

- [ ] 설정 Read + REPO clone/pull (위와 동일)
- [ ] 워크트리 생성 (`BR=rebuild-${TS}`)
- [ ] posts.json 로드 → 대상 entries 결정 (slug / all / --category)
  - 빈 결과 → "대상 없음" 안내 후 종료
- [ ] `all` 모드면 AskUserQuestion 으로 "총 N개 재빌드합니다. 계속?" 확인
- [ ] 첫 배포 판단 (index.html 부재 / 템플릿 변경) → 템플릿 다시 입힘
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

---

## 참고

- 설정: `~/.claude/hams-diary.json` (`{repo, template, pagesUrl?, features?}`)
- 템플릿: `${PLUGIN_ROOT}/skills/diary/templates/{minimal|tech|lecture|notebook|magazine}/`
- HTML 어댑터 빌더: `${PLUGIN_ROOT}/skills/diary/inject_html_adapter.py`
- HTML 어댑터 역추출: `${PLUGIN_ROOT}/skills/diary/extract_original_html.py` (재빌드 모드 fallback)
- 편집 모드 워처: `${PLUGIN_ROOT}/skills/diary/watch_and_rebuild.py`
- 레포 메타: `{REPO}/.diary-meta.json` (현재 적용된 템플릿 기록)
- 원본 백업: `{REPO}/_src/{slug}.{md|html}` (편집·재빌드 모드용)
