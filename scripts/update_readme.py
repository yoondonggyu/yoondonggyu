#!/usr/bin/env python3
"""
GitHub Profile README 자동 업데이트 스크립트
- study_log.json을 읽어서 README.md의 Weekly Study Log 섹션을 자동 업데이트
- 현재 달은 표시, 이전 달은 토글로 숨김
"""

import json
from datetime import datetime
from collections import defaultdict
from pathlib import Path


def load_study_log(file_path: str = "study_log.json") -> dict:
    """study_log.json 파일 로드"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_date(date_str: str) -> datetime:
    """날짜 문자열을 datetime으로 변환"""
    return datetime.strptime(date_str, "%Y-%m-%d")


def format_date_range(start: str, end: str) -> str:
    """날짜 범위를 포맷팅 (MM/DD 형식)"""
    start_dt = parse_date(start)
    end_dt = parse_date(end)
    return f"{start_dt.month:02d}/{start_dt.day:02d}(월) ~ {end_dt.month:02d}/{end_dt.day:02d}(일)"


def format_hours(hours: int, minutes: int) -> str:
    """시간을 포맷팅"""
    return f"**{hours}h {minutes:02d}m**"


def get_month_key(date_str: str) -> tuple:
    """날짜에서 (년, 월) 튜플 추출"""
    dt = parse_date(date_str)
    return (dt.year, dt.month)


def group_by_month(records: list) -> dict:
    """기록을 월별로 그룹화"""
    grouped = defaultdict(list)
    for record in records:
        # end_date 기준으로 월 결정
        month_key = get_month_key(record["end_date"])
        grouped[month_key].append(record)
    return grouped


def calculate_total_time(records: list) -> tuple:
    """총 공부 시간 계산"""
    total_minutes = sum(r["hours"] * 60 + r["minutes"] for r in records)
    total_hours = total_minutes // 60
    return total_hours, len(records)


def generate_month_table(records: list, show_header: bool = True) -> str:
    """월별 테이블 생성"""
    lines = []
    if show_header:
        lines.append("| 기간 | 공부 시간 | 주요 학습 내용 |")
        lines.append("|:---:|:---:|:---|")
    
    # 최신순으로 정렬
    sorted_records = sorted(records, key=lambda x: x["end_date"], reverse=True)
    
    for record in sorted_records:
        date_range = format_date_range(record["start_date"], record["end_date"])
        hours = format_hours(record["hours"], record["minutes"])
        topics = record["topics"]
        lines.append(f"| {date_range} | {hours} | {topics} |")
    
    return "\n".join(lines)


def generate_study_log_section(records: list) -> str:
    """Weekly Study Log 섹션 전체 생성"""
    # 현재 날짜 기준
    now = datetime.now()
    current_month = (now.year, now.month)
    
    # 월별 그룹화
    grouped = group_by_month(records)
    sorted_months = sorted(grouped.keys(), reverse=True)
    
    # 총 시간 계산
    total_hours, total_weeks = calculate_total_time(records)
    avg_hours = total_hours // total_weeks if total_weeks > 0 else 0
    
    lines = [
        "## ⏱️ Weekly Study Log",
        "",
        "<div align=\"center\">",
        "",
        "<!-- 총 누적 공부 시간 -->",
        f"![Total Study Time](https://img.shields.io/badge/Total_Study_Time-{total_hours}+_hours-FF6B6B?style=for-the-badge&logo=clockify&logoColor=white)",
        f"![Average Per Week](https://img.shields.io/badge/Avg_Per_Week-{avg_hours}_hours-4ECDC4?style=for-the-badge&logo=clock&logoColor=white)",
        "",
        "</div>",
        "",
    ]
    
    # 현재 달과 바로 이전 달은 표시, 나머지는 토글
    for i, month_key in enumerate(sorted_months):
        year, month = month_key
        month_records = grouped[month_key]
        
        # 현재 달 또는 가장 최신 달
        if i == 0:
            lines.append(f"### 📅 {year}년 {month}월")
            lines.append("")
            lines.append(generate_month_table(month_records))
            lines.append("")
        else:
            # 이전 달은 토글로 숨김
            lines.append("<details>")
            lines.append(f"<summary><b>📆 {year}년 {month}월 기록 보기</b></summary>")
            lines.append("")
            lines.append(generate_month_table(month_records))
            lines.append("")
            lines.append("</details>")
            lines.append("")
    
    # 마무리 메시지
    lines.append(f"> 🔥 **{total_weeks}주간 총 {total_hours}시간+ 학습!** 매주 평균 {avg_hours}시간 투자 중!")
    
    return "\n".join(lines)


def update_readme(readme_path: str, study_log_section: str) -> str:
    """README.md 파일 업데이트"""
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Weekly Study Log 섹션 찾기 및 교체
    start_marker = "## ⏱️ Weekly Study Log"
    end_marker = "---\n\n<div align=\"center\">\n\n### 💬 Random Dev Quote"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        print("Warning: Could not find study log section markers")
        return content
    
    # 새로운 내용으로 교체
    new_content = (
        content[:start_idx] +
        study_log_section +
        "\n\n---\n\n<div align=\"center\">\n\n### 💬 Random Dev Quote" +
        content[end_idx + len(end_marker):]
    )
    
    return new_content


def main():
    """메인 함수"""
    # 파일 경로 설정
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    study_log_path = repo_root / "study_log.json"
    readme_path = repo_root / "README.md"
    
    print(f"📖 Loading study log from: {study_log_path}")
    
    # 데이터 로드
    data = load_study_log(study_log_path)
    records = data["records"]
    
    print(f"📊 Found {len(records)} study records")
    
    # Study Log 섹션 생성
    study_log_section = generate_study_log_section(records)
    
    # README 업데이트
    print(f"📝 Updating README: {readme_path}")
    new_readme = update_readme(readme_path, study_log_section)
    
    # 파일 저장
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_readme)
    
    print("✅ README updated successfully!")
    
    # 총 시간 출력
    total_hours, total_weeks = calculate_total_time(records)
    print(f"📈 Total: {total_hours}+ hours over {total_weeks} weeks")


if __name__ == "__main__":
    main()

