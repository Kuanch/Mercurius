from __future__ import annotations
from typing import Dict, List
from modules.sweeper.schemas.plan import Plan, ActLabel, ActArchive, ActMoveTo, ActMarkRead, ActStar, ActUnstar, ActDraftReply
from core.services.gmail import GmailService
from modules.sweeper.templates.replies import render_template

# 可調整：每次查詢最多採樣數，避免一次抓爆
HARD_CAP = 500

def _flatten_hits(gs: GmailService, plan: Plan):
    hits = []
    for q in plan.queries:
        msgs = gs.search_messages(q.q, max_results=min(q.max_results, HARD_CAP))
        hits.extend(msgs)
    # 去重（以 threadId 去重更穩妥）
    uniq = {}
    for m in hits:
        uniq[m["id"]] = m
    all_msgs = list(uniq.values())
    # 套用上限
    return all_msgs[: plan.limits.max_threads]


def preview_plan(plan: Plan) -> Dict:
    gs = GmailService()
    msgs = _flatten_hits(gs, plan)
    # 只回傳輕量資訊與動作摘要
    preview_items = [{
        "id": m["id"],
        "threadId": m.get("threadId"),
        "from": m["headers"].get("from"),
        "subject": m["headers"].get("subject"),
        "snippet": m.get("snippet")
    } for m in msgs]

    actions = [a.dict() for a in plan.actions]
    return {
        "total_hits": len(msgs),
        "will_apply": actions,
        "sample": preview_items[:10]
    }


def execute_plan(plan: Plan) -> Dict:
    gs = GmailService()
    msgs = _flatten_hits(gs, plan)
    ids = [m["id"] for m in msgs]

    # 安全檢查：白名單
    allowed_labels = set([n.lower() for n in plan.limits.allow_labels])
    for a in plan.actions:
        if isinstance(a, ActLabel) and a.name.lower() not in allowed_labels:
            raise ValueError(f"Label '{a.name}' is not in allowlist")
        if isinstance(a, ActMoveTo):
            raise ValueError("move_to is disabled by default in MVP; use label+archive 取代")

    results = {"modified": len(ids), "drafts": []}

    for a in plan.actions:
        if isinstance(a, ActLabel):
            gs.batch_label(ids, add=[a.name])
        elif isinstance(a, ActArchive):
            gs.batch_archive(ids)
        elif isinstance(a, ActMarkRead):
            gs.batch_mark_read(ids)
        elif isinstance(a, ActStar):
            gs.batch_star(ids)
        elif isinstance(a, ActUnstar):
            gs.batch_unstar(ids)
        elif isinstance(a, ActDraftReply):
            # 依每封建立草稿（受 max_drafts 限制）
            count = 0
            for m in msgs:
                if count >= plan.limits.max_drafts:
                    break
                frm = m["headers"].get("from", "")
                # 簡單擷取郵件位址
                to_addr = frm.split("<")[-1].split(">")[0] if "@" in frm else frm
                subject = m["headers"].get("subject", "")
                body = render_template(a.template_id)
                draft_id = gs.create_draft_reply(m["id"], m.get("threadId"), to_addr, subject, body)
                results["drafts"].append({"messageId": m["id"], "draftId": draft_id})
                count += 1
    return results
