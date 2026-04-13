---
name: hams-diary
description: |
  마크다운 파일을 임의의 GitHub Pages 레포에 자동 배포.
  타겟 레포는 ~/.claude/hams-diary.json 에 설정. --set-repo 로 변경 가능.
  git worktree 자동 생성/관리, posts.json 수정, HTML 변환을 일괄 처리.
  사용법: /hams-diary {md파일경로} [카테고리명 (옵션)]
         /hams-diary --set-repo {github-repo-url}
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - AskUserQuestion
---

# /hams-diary Skill

## 개요

마크다운 파일을 설정된 GitHub Pages 레포에 자동으로 게시합니다.
타겟 레포는 `~/.claude/hams-diary.json` 에서 관리합니다.

**한 번에 처리되는 작업:**

- ✅ 마크다운 파일을 HTML로 변환
- ✅ 제목, 요약, 태그 자동 추출
- ✅ 카테고리 자동 결정 (기존/신규)
- ✅ posts.json 업데이트
- ✅ git worktree 생성 → 작업 → 푸시 → 정리
- ✅ **자동 PR 생성 & merge** (GitHub Pages 자동 배포)
- ✅ 완료 시 블로그 URL 제공

---

## 사용 방법

```bash
/hams-diary {파일경로} [카테고리명]        # 포스트 배포
/hams-diary --set-repo {github-repo-url}  # 타겟 레포 설정/변경
```

**예시:**

```bash
# 레포 최초 설정
/hams-diary --set-repo https://github.com/myuser/my-blog.git

# 이후 일반 사용
/hams-diary /path/to/post.md
/hams-diary /path/to/post.md Development
```

---

## 동작 순서

### 0️⃣ 설정 파일 확인

**`--set-repo` 플래그가 있는 경우:**

```bash
# JSON 저장
python3 -c "import json; json.dump({'repo': '<입력된 URL>'}, open('$HOME/.claude/hams-diary.json', 'w'))"
```

- URL에서 레포명 추출: `https://github.com/owner/repo.git` → `repo`
- pagesUrl 자동 추론: `https://owner.github.io/repo/`
- 저장 후 종료 (파일 배포 없이)

> **참고:** 커스텀 도메인을 사용할 경우, `~/.claude/hams-diary.json`을 직접 편집하여 `"pagesUrl"` 필드를 추가할 수 있습니다:
> ```json
> {
>   "repo": "https://github.com/owner/repo.git",
>   "pagesUrl": "https://mycustom.domain/"
> }
> ```

출력:
```
✅ 설정 완료!
   레포: https://github.com/owner/repo.git
   블로그: https://owner.github.io/repo/
   
이제 /hams-diary {파일경로} 로 배포할 수 있습니다.
```

**일반 실행인 경우 (`--set-repo` 없음):**

`~/.claude/hams-diary.json` 파일을 읽는다:

```bash
cat ~/.claude/hams-diary.json
REPO_URL=$(python3 -c "import sys,json; print(json.load(open('$HOME/.claude/hams-diary.json'))['repo'])")
# pagesUrl이 있으면 추출 (없으면 빈 문자열)
PAGES_URL_OVERRIDE=$(python3 -c "import sys,json; d=json.load(open('$HOME/.claude/hams-diary.json')); print(d.get('pagesUrl',''))" 2>/dev/null || echo "")
```

파일이 없으면 AskUserQuestion으로 URL을 입력받아 저장 후 계속:

```
설정된 타겟 레포가 없습니다.
배포할 GitHub 레포 URL을 입력해주세요:
(예: https://github.com/myuser/my-blog.git)
```

입력 후:
```bash
python3 -c "import json; json.dump({'repo': '<입력된 URL>'}, open('$HOME/.claude/hams-diary.json', 'w'))"
```

**설정에서 추출하는 값:**

| 변수 | 추출 방법 | 예시 |
|------|-----------|------|
| `REPO_URL` | `repo` 필드 그대로 | `https://github.com/owner/repo.git` |
| `REPO_NAME` | URL에서 마지막 경로 + `.git` 제거 | `repo` |
| `REPO_OWNER` | URL에서 owner 추출 | `owner` |
| `PAGES_URL` | `pagesUrl` 필드 or 자동 추론 | `https://owner.github.io/repo/` |
| `LOCAL_DIR` | `/tmp/{REPO_NAME}` | `/tmp/repo` |
| `WORKTREE_DIR` | `/tmp/{REPO_NAME}-{id}` | `/tmp/repo-my-post` |

**URL 파싱 로직:**

HTTPS: `https://github.com/owner/repo.git`
```bash
REPO_OWNER=$(echo "$REPO_URL" | sed 's|https://github.com/||' | cut -d'/' -f1)
REPO_NAME=$(echo "$REPO_URL" | sed 's|/$||; s|.*/||; s|\.git$||')
```

SSH: `git@github.com:owner/repo.git`
```bash
REPO_OWNER=$(echo "$REPO_URL" | sed 's|git@github.com:||' | cut -d'/' -f1)
REPO_NAME=$(echo "$REPO_URL" | sed 's|/$||; s|.*/||; s|\.git$||')
```

pagesUrl 자동 추론:
```bash
PAGES_URL="https://${REPO_OWNER}.github.io/${REPO_NAME}/"
```
`pagesUrl` 필드가 설정 파일에 있으면 그 값을 우선 사용.

### 1️⃣ 파일 분석

- MD 파일 읽기
- 제목 추출 (첫 번째 h1 마크다운 `# 제목`)
- 요약 추출 (frontmatter 또는 첫 단락)
- 태그 추출 (섹션 헤딩, 코드 블록 키워드)
- **카테고리**: 인자로 받거나 자동 추론

### 2️⃣ 레포 준비

- `/tmp/hamster-diary` 디렉토리 확인
- 없으면: `git clone https://github.com/codingspecialist/hamster-diary.git /tmp/hamster-diary`
- 있으면: `git pull origin master`

### 3️⃣ ID 생성

파일명을 kebab-case로 정규화:

```
SEOLAP_MARKETING_GUIDE.md → seolap-marketing-guide
my-blog-post.md          → my-blog-post
```

### 4️⃣ Git Worktree 생성

```bash
git worktree add -b post-{id} /tmp/hamster-diary-{id}
cd /tmp/hamster-diary-{id}
```

### 5️⃣ posts.json 업데이트

**카테고리 처리:**

- 기존 categories[] 에 없으면 추가
- 있으면 그대로 사용

**포스트 항목 추가 (배열 맨 앞):**

```json
{
  "id": "{id}",
  "title": "{추출된 제목}",
  "date": "2026-04-11",  // 오늘 날짜
  "category": "{카테고리}",
  "summary": "{요약}",
  "filename": "posts/{id}.html",
  "tags": ["{tag1}", "{tag2}", ...]
}
```

### 6️⃣ HTML 변환 & 저장

마크다운을 HTML로 변환하여 `posts/{id}.html` 저장.

변환 규칙:

| Markdown           | HTML                                           |
| ------------------ | ---------------------------------------------- |
| `# 제목`           | `<h1 class="post-title">제목</h1>` (header 내) |
| `## 섹션`          | `<h2>섹션</h2>`                                |
| `### 소제목`       | `<h3>소제목</h3>`                              |
| `**굵게**`         | `<strong>굵게</strong>`                        |
| `_기울임_`         | `<em>기울임</em>`                              |
| `` `인라인코드` `` | `<code>인라인코드</code>`                      |
| ` ```코드블록``` ` | `<pre><code>...</code></pre>`                  |
| `- 항목`           | `<ul><li>항목</li></ul>`                       |
| `1. 항목`          | `<ol><li>항목</li></ol>`                       |
| `> 인용`           | `<blockquote>인용</blockquote>`                |
| `\|표\|`           | `<table><thead><tbody>...`                     |
| `[링크](url)`      | `<a href="url">링크</a>`                       |

**HTML 전체 구조:**

```html
<article>
  <header class="post-header">
    <h1 class="post-title">제목</h1>
    <div class="post-meta">
      <time>2026-04-11</time>
      <span class="category-tag">Category</span>
    </div>
  </header>

  <div class="post-content">
    <!-- 변환된 본문 -->
    <h2>섹션 1</h2>
    <p>내용...</p>
  </div>
</article>
```

### 7️⃣ Commit & Push

```bash
git add -A
git commit -m "feat: {제목} 포스트 추가

- 카테고리: {카테고리}
- 태그: {tag1}, {tag2}, ...
- 요약: {요약 첫 문장}"

git push -u origin post-{id}
```

### 8️⃣ PR 생성 & 자동 merge

**자동 PR 생성:**

```bash
gh pr create \
  --head post-{id} \
  --base master \
  --title "feat: {제목} 포스트 추가" \
  --body "카테고리: {카테고리}
태그: {tag1}, {tag2}, ...
요약: {요약}"
```

**자동 merge & 브랜치 삭제:**

```bash
gh pr merge --squash --delete-branch
```

**로컬 master 동기화:**

```bash
git checkout master
git pull origin master
```

### 9️⃣ Worktree 정리

```bash
git worktree remove /tmp/hamster-diary-{id}
```

### 🔟 결과 출력

```
✅ 게시 완료!

📄 포스트: {제목}
🏷️  카테고리: {카테고리}
🔗 파일: posts/{id}.html
📅 작성일: 2026-04-11

🌐 블로그: https://codingspecialist.github.io/hamster-diary/
⏱️  예상 반영 시간: 1분 내 (GitHub Actions 자동 배포)
```

---

## 실행 시 질문 (필요한 경우)

### 카테고리 확인

파일 내용으로 자동 추론하되, 기존 카테고리와 맞지 않으면:

```
📌 현재 카테고리: "Kubernetes"
   기존 카테고리: ["Kubernetes", "Docker", "Linux", "Git", "Marketing"]

이 포스트의 카테고리는?
1. 기존 카테고리 선택
2. 신규 생성: {입력값}
```

### 요약 확인

자동 추출한 요약이 부족하면:

```
📝 현재 요약: "..."
요약을 수정하거나 그대로 진행할까요?
```

---

## 팁

### 마크다운 작성 시

- **첫 번째 `# 제목`** 이 포스트 제목이 됨 (필수)
- **frontmatter** (선택):
  ```yaml
  ---
  summary: "요약을 여기 써도 자동 인식됩니다"
  tags: ["tag1", "tag2"]
  ---
  ```

### 이미 존재하는 ID

같은 ID로 다시 실행하면:

- posts.json 기존 항목 제거
- HTML 파일 덮어씀
- 새 브랜치로 푸시

### Git 충돌

워크트리 작업 중 main 브랜치가 변경되면:

- 워크트리 안에서 `git pull origin master` 실행
- 충돌 해결 후 다시 진행

---

## 에러 처리

### 레포 Clone 실패

```
❌ Clone 실패: GitHub 인증 확인
  git config user.name / user.email 설정 확인
  SSH 키 또는 Personal Access Token 설정 필요
```

### MD 파일 포맷 오류

```
❌ 포맷 오류: h1 헤딩을 찾을 수 없음
  첫 줄에 # 제목 형식으로 작성하세요
```

### 카테고리 미결정

```
❌ 카테고리 미결정
  /hamster-diary {파일} 카테고리명 으로 명시하세요
```

---

## 내부 구현 (Claude가 따를 체크리스트)

- [ ] 인자 파싱: 파일경로, 카테고리(옵션)
- [ ] MD 파일 Read
- [ ] 제목 추출: `# .*` 정규식으로 첫 h1 찾기
- [ ] 요약 추출: frontmatter → 첫 단락 순서
- [ ] 태그 추출: `##`, `###` 헤딩, 코드 블록 키워드
- [ ] 카테고리 결정: 인자 또는 내용 분석 → 기존/신규
- [ ] /tmp/hamster-diary 확인: clone/pull
- [ ] ID 생성: 파일명 → kebab-case
- [ ] Worktree 생성: `git worktree add -b post-{id} ...`
- [ ] posts.json Read
- [ ] posts.json 수정: categories 추가(신규시), posts 앞에 항목 삽입
- [ ] posts.json Write
- [ ] MD → HTML 변환: 마크다운 파싱 → HTML 생성
- [ ] HTML 파일 Write: `posts/{id}.html`
- [ ] Git commit: `git add -A && git commit -m ...`
- [ ] Git push: `git push -u origin post-{id}`
- [ ] **✨ gh pr create**: 자동 PR 생성 (제목, 본문 포함)
- [ ] **✨ gh pr merge --squash --delete-branch**: 자동 merge + 브랜치 삭제
- [ ] **✨ git checkout master && git pull origin master**: 로컬 master 동기화
- [ ] Worktree 삭제: `git worktree remove`
- [ ] 결과 출력: GitHub Pages URL + 배포 예상 시간

---

## 참고

- **hamster-diary 레포**: https://github.com/codingspecialist/hamster-diary
- **블로그 사이트**: https://codingspecialist.github.io/hamster-diary/
- **로컬 작업 경로**: `/tmp/hamster-diary` (clone), `/tmp/hamster-diary-{id}` (worktree)
