# News Mailer (GitHub Actions 버전)

키워드로 구글뉴스를 검색해 HTML 메일로 보내는 자동화입니다. **무료**로 매일 실행됩니다.

## 빠른 시작
1. 이 리포지토리 파일을 그대로 업로드(push)합니다.
2. 깃허브 저장소 → **Settings → Secrets and variables → Actions → New repository secret**에서  
   - `SMTP_PASS` 추가 (지메일 앱 비밀번호 또는 SMTP 비밀번호)
3. `.github/workflows/News Mailer` 워크플로우에서 **Run workflow**로 수동 테스트.
4. 정상 동작 확인 후, 스케줄(UTC)로 매일 실행됩니다.

> KST 08:30에 보내려면, 워크플로우의 cron을 `30 23 * * *`로 설정합니다. (UTC 기준)

## 환경변수(워크플로우에서 수정)
- `NEWS_KEYWORDS`: "노조법, 파업" 같이 쉼표로 구분
- `NEWS_RECENCY_DAYS`: 최근 N일
- `MAIL_SENDER`: 보내는 주소 (지메일 권장)
- `MAIL_RECIPIENTS`: 받는 주소 여러 개면 쉼표로 구분
- `SMTP_HOST`: smtp.gmail.com
- `SMTP_PORT`: 465
- `SMTP_USER`: 로그인 ID(일반적으로 보내는 주소와 동일)
- `SMTP_PASS`: **GitHub Secrets**에 저장된 비밀번호 참조
- `MAIL_SUBJECT_PREFIX`: 메일 제목 접두사

## Gmail 보안 팁
- 구글 계정 → 보안 → 2단계 인증 활성화 후 **앱 비밀번호**를 만들고, 그 값을 `SMTP_PASS` secret으로 등록하세요.
