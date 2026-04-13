---
name: hams-dashboard
description: Hamstern 대시보드 웹 UI 실행 (Decisions, History)
---

# Hamstern Dashboard

hamstern 프로젝트 관리 대시보드를 웹 브라우저에서 엽니다.

## 기능

- **Home** — 프로젝트 선택
- **Decisions** — 현재 프로젝트의 확정된 결정사항 (decisions.md)
- **History** — 누적 컨텍스트 히스토리

## 동작

```bash
/hams-dashboard [--port <번호>] [--no-open]
```

**기본 포트:** 7777
**기본 동작:** 브라우저 자동 열기 (macOS에서 `open` 사용)

## 실행 예

```bash
# 기본 포트(7777)로 실행, 브라우저 자동 열기
/hams-dashboard

# 커스텀 포트
/hams-dashboard --port 8080

# 브라우저 안 열고 HTTP 서버만 시작
/hams-dashboard --no-open
```

## 접근 경로

브라우저: `http://localhost:7777`

## 데이터 소스

- **Decisions:** `{project}/.hamstern/boss-hamster/decisions.md`

---

## 기술 세부사항

### HTTP 서버

`cmux dashboard --port <포트>` 명령으로 HTTP 서버 시작:

- `GET /` — HTML 대시보드 UI
- `GET /api/baby` — 터미널별 회의록
- `GET /api/mom` — 프로젝트 컨텍스트
- `GET /api/boss` — 핀된 결정사항
- `POST /api/pin` — 결정사항 핀 추가
- `POST /api/unpin` — 결정사항 핀 제거

### UI 탭

1. **Home**
   - 프로젝트 목록 (`.hamstern/boss-hamster/` 있는 디렉토리)
   - 프로젝트 선택 → 다른 탭 데이터 로드

2. **Decisions**
   - decisions.md 내용 표시
   - 마크다운 포맷 + 핀 제거 버튼

3. **History**
   - 카테고리별 결정사항 그룹핑
   - ML 추천 점수 표시 (✨)
   - [핀 추가] 버튼 → boss-hamster/decisions.md 추가

---

## 참고

- 대시보드는 로컬 localhost에만 바인딩 (보안)
- 자동 새로고침은 없음 (필요시 F5)
- 편집 후 결과는 파일에 즉시 반영 (별도 저장 필요 없음)
