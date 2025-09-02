#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
키워드 기반 구글뉴스 RSS 수집 → HTML 이메일 전송 스크립트
- 환경변수로 설정 (아래 CONFIG 섹션)
- 중복(링크) 제거, 기간 필터, KST 타임존 정렬
"""
import os, ssl, feedparser, html, socket
from datetime import datetime, timedelta
from dateutil import parser as dtparser
from email.message import EmailMessage
import pytz
from urllib.parse import quote_plus

# ========= CONFIG (환경변수) =========
KEYWORDS = [s.strip() for s in os.getenv("NEWS_KEYWORDS", "노동법, 파업, 임금협상").split(",") if s.strip()]
RECENCY_DAYS = int(os.getenv("NEWS_RECENCY_DAYS", "2"))  # 최근 N일 기사만
MAX_ITEMS_PER_KEYWORD = int(os.getenv("NEWS_MAX_PER_KEYWORD", "20"))

SENDER = os.getenv("MAIL_SENDER", "yourname@gmail.com")
RECIPIENTS = [s.strip() for s in os.getenv("MAIL_RECIPIENTS", "yourname@gmail.com").split(",") if s.strip()]

# SMTP (지메일 권장: 앱 비밀번호 사용)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))  # SSL 포트
SMTP_USER = os.getenv("GitHub Actions", SENDER)
SMTP_PASS = os.getenv("cbhtofvijdcrkrak", "")  # Gmail 앱 비밀번호 또는 SMTP 비밀번호

# 메일 제목 프리픽스/브랜드
MAIL_SUBJECT_PREFIX = os.getenv("MAIL_SUBJECT_PREFIX", "[뉴스요약]")

# 한국 시간대
KST = pytz.timezone("Asia/Seoul")

# ========= Helpers =========
def google_news_rss_url(keyword: str, days: int = 2, lang="ko", country="KR"):
    q = f"{keyword} when:{days}d"
    return (
        "https://news.google.com/rss/search?"
        f"q={quote_plus(q)}&hl={lang}&gl={country}&ceid={country}%3A{lang}"
    )

def parse_pubdate(entry):
    for attr in ("published", "updated", "pubDate"):
        val = getattr(entry, attr, None)
        if val:
            try:
                return dtparser.parse(val)
            except Exception:
                continue
    return None

def within_days(dt, days=2):
    if not dt:
        return True
    now = datetime.now(pytz.UTC)
    return (now - dt.astimezone(pytz.UTC)) <= timedelta(days=days)

def collect_news():
    items = []
    seen_links = set()
    for kw in KEYWORDS:
        url = google_news_rss_url(kw, RECENCY_DAYS)
        feed = feedparser.parse(url)
        count = 0
        for e in feed.entries:
            link = getattr(e, "link", "")
            if not link or link in seen_links:
                continue
            pub = parse_pubdate(e)
            if not within_days(pub, RECENCY_DAYS):
                continue
            seen_links.add(link)
            items.append({
                "keyword": kw,
                "title": getattr(e, "title", "").strip(),
                "link": link,
                "published": pub.astimezone(KST).strftime("%Y-%m-%d %H:%M") if pub else "",
                "source": getattr(e, "source", {}).get("title") if hasattr(e, "source") else "",
                "summary": getattr(e, "summary", ""),
            })
            count += 1
            if count >= MAX_ITEMS_PER_KEYWORD:
                break
    items.sort(key=lambda x: x["published"] or "0000-00-00 00:00", reverse=True)
    return items

def build_html(items):
    if not items:
        return "<p>수집된 기사가 없습니다.</p>"
    from collections import defaultdict
    by_kw = defaultdict(list)
    for it in items:
        by_kw[it["keyword"]].append(it)

    parts = []
    parts.append(f"<p>생성 시각 (KST): {datetime.now(KST).strftime('%Y-%m-%d %H:%M')}</p>")
    for kw, rows in by_kw.items():
        parts.append(f"<h2 style='margin:16px 0 8px'>{html.escape(kw)}</h2>")
        parts.append("<ul>")
        for r in rows:
            title = html.escape(r['title'] or "(제목없음)")
            link = html.escape(r['link'])
            meta = f"{r['published']}" + (f" · {html.escape(r['source'])}" if r.get('source') else "")
            parts.append(
                f"<li style='margin:6px 0'>"
                f"<a href='{link}' target='_blank' rel='noopener'>{title}</a>"
                f"<div style='font-size:12px;opacity:0.8'>{meta}</div>"
                f"</li>"
            )
        parts.append("</ul>")
    return "\n".join(parts)

def send_mail(subject, html_body):
    if not SMTP_PASS:
        raise RuntimeError("SMTP_PASS(앱 비밀번호/SMTP 비밀번호)가 설정되지 않았습니다.")
    msg = EmailMessage()
    msg["From"] = SENDER
    msg["To"] = ", ".join(RECIPIENTS)
    msg["Subject"] = subject
    msg.set_content("HTML 메일을 지원하지 않는 클라이언트입니다. 웹메일에서 확인해주세요.")
    msg.add_alternative(html_body, subtype="html")

    context = ssl.create_default_context()
    import smtplib
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context, timeout=30) as smtp:
        smtp.login(SMTP_USER, SMTP_PASS)
        smtp.send_message(msg)

def main():
    items = collect_news()
    html_body = build_html(items)
    subject = f"{MAIL_SUBJECT_PREFIX} {datetime.now(KST).strftime('%Y-%m-%d')}"
    send_mail(subject, html_body)
    print(f"Sent {len(items)} items to {len(RECIPIENTS)} recipient(s).")

if __name__ == "__main__":
    main()
