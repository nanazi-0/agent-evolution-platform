from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def write_report(report: dict[str, Any], directory: Path) -> tuple[Path, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "evolution-report.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    rows = "".join(
        f"<tr><td>{html.escape(str(item['generation']))}</td><td>{html.escape(item['candidate_id'])}</td>"
        f"<td>{item['score']:.3f}</td><td>{'PASS' if item['policy_passed'] else 'FAIL'}</td>"
        f"<td>{'PASS' if item['evaluation_passed'] else 'FAIL'}</td><td>{html.escape(item['rationale'])}</td></tr>"
        for item in report["candidates"]
    )
    document = f"""<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'><title>RSI Evolution Report</title>
<style>body{{font-family:system-ui;margin:2rem;max-width:1200px}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ddd;padding:.5rem;text-align:left}}code{{background:#eee;padding:.15rem}}</style></head><body>
<h1>受治理 RSI 进化报告</h1><p>Run：<code>{html.escape(report['run_id'])}</code></p>
<p>基线：{report['baseline_score']:.3f}；优胜者：{html.escape(report['champion_id'])}；最终分数：{report['champion_score']:.3f}；状态：<strong>{html.escape(report['status'])}</strong></p>
<table><tr><th>代</th><th>候选</th><th>分数</th><th>策略</th><th>评测</th><th>理由</th></tr>{rows}</table>
<h2>安全边界</h2><p>候选无权访问或修改隐藏评测、策略、评估器、审批规则与质量控制面。发布默认需要具名人工批准。</p></body></html>"""
    html_path = directory / "evolution-report.html"
    html_path.write_text(document, encoding="utf-8")
    return json_path, html_path

