#!/usr/bin/env python3
"""
export.py v2.1 - NotebookLM Studio inspired output formats.
New: mindmap (HTML), flashcard, table, report
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
from collections import Counter

DEFAULT_INSP_FILE  = Path.home() / ".workbuddy" / "memory" / "inspirations" / "inspirations.json"
DEFAULT_TASKS_FILE = Path.home() / ".workbuddy" / "memory" / "tasks.json"
DEFAULT_WORKFLOW_FILE = Path.home() / ".workbuddy" / "memory" / "inspirations" / "workflow-state.json"

TYPE_EMOJIS = {
    "paper": "\U0001f4c4", "url": "\U0001f517", "idea": "\U0001f4a1",
    "decision": "\u2705",  "blocker": "\u26a0", "milestone": "\U0001f3c6",
}

def ensure_dirs(p):
    p.mkdir(parents=True, exist_ok=True)

def load_json_file(fp, default):
    if not fp.exists(): return default
    with open(fp, "r", encoding="utf-8") as f: return json.load(f)

def load_inspirations(fp):
    if not fp.exists():
        print("Error: not found: " + str(fp), file=sys.stderr); sys.exit(1)
    with open(fp, "r", encoding="utf-8") as f: return json.load(f)

def filter_entries(data, task_id=None, include_archived=False):
    es = data.get("entries", [])
    if not include_archived:
        es = [e for e in es if e.get("status") != "archived"]
    if task_id:
        es = [e for e in es if e.get("task_id") == task_id]
    return es

# --- markdown ---
def export_markdown(data, output_file, task_id=None):
    entries = filter_entries(data, task_id)
    TYPE_NAMES = {
        "paper":     "\U0001f4c4 " + "\u8bba\u6587",
        "url":       "\U0001f517 " + "\u94fe\u63a5",
        "idea":      "\U0001f4a1 " + "\u7075\u611f",
        "decision":  "\u2705 "     + "\u51b3\u7b56",
        "blocker":   "\u26a0 "     + "\u56f0\u96be",
        "milestone": "\U0001f3c6 " + "\u91cc\u7a0b\u7891",
    }
    with open(output_file, "w", encoding="utf-8") as f:
        now = datetime.now()
        f.write("# " + "\u77e5\u8bc6\u5e93\u5bfc\u51fa" + " - " + now.strftime("%Y-%m-%d") + "\n\n")
        f.write("> " + "\u5bfc\u51fa\u65f6\u95f4" + ": " + now.isoformat() + "\n")
        f.write("> " + "\u77e5\u8bc6\u603b\u6570" + ": " + str(len(entries)) + "\n\n---\n\n")
        groups = {}
        for e in entries: groups.setdefault(e.get("type","idea"), []).append(e)
        for t, items in groups.items():
            f.write("\n## " + TYPE_NAMES.get(t,t) + " (" + str(len(items)) + ")\n\n")
            for e in items:
                f.write("### [" + e["created_at"][:10] + "] " + e["title"] + "\n\n")
                f.write(e["content"] + "\n\n")
                if e.get("tags"):
                    f.write("\u6807\u7b7e: " + " ".join("#"+tg for tg in e["tags"]) + "\n\n")
                if e.get("source_url"):
                    f.write("\u6765\u6e90: " + e["source_url"] + "\n\n")
                f.write("---\n\n")
    print("OK markdown: " + str(output_file))

# --- json ---
def export_json_fmt(data, output_file):
    with open(output_file, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)
    print("OK json: " + str(output_file))

# --- mermaid ---
def export_mermaid(data, output_file, task_id=None):
    entries = filter_entries(data, task_id)
    colors = ["#ffeaa7","#dfe6e9","#fab1a0","#a29bfe","#81ecec","#74b9ff"]
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# " + "\u77e5\u8bc6\u56fe\u8c31" + "\n\n```mermaid\ngraph TD\n")
        for e in entries:
            nid = e["id"].replace("_","").replace("-","")
            title = e["title"][:25].replace('"',"'")
            f.write('    {}["{}"]\n'.format(nid, title))
        for e in entries:
            nid = e["id"].replace("_","").replace("-","")
            for rid in e.get("related",[]):
                f.write("    {} --> {}\n".format(nid, rid.replace("_","").replace("-","")))
        tg = {}
        for e in entries:
            for tag in e.get("tags",[]): tg.setdefault(tag,[]).append(e["id"])
        for i,(_,eids) in enumerate(tg.items()):
            c = colors[i%len(colors)]
            for eid in eids:
                f.write("    style {} fill:{},stroke:#636e72\n".format(eid.replace("_","").replace("-",""), c))
        f.write("```\n")
    print("OK mermaid: " + str(output_file))

# --- mindmap (HTML) - NotebookLM inspired ---
def export_mindmap(data, output_file, task_id=None):
    entries = filter_entries(data, task_id)
    tg = {}
    for e in entries:
        for tag in e.get("tags",[]): tg.setdefault(tag,[]).append(e)
    pal = ["#ff6b6b","#ffd93d","#6bcb77","#4d96ff","#c77dff","#ff9f1c","#2ec4b6","#e71d36","#ff8fab","#48cae4"]
    branches = ""
    for i,(tag,tes) in enumerate(list(tg.items())[:12]):
        c = pal[i%len(pal)]
        leaves = ""
        for e in tes[:6]:
            ico = TYPE_EMOJIS.get(e.get("type","idea"),"")
            t = e["title"][:40].replace('"',"&quot;").replace("'","&#39;")
            ct = e["content"][:180].replace('"',"&quot;").replace("'","&#39;").replace("\n"," ")
            leaves += '<div class="leaf" onclick="sd(this)" data-content="{}" data-date="{}" data-type="{}">{} {}</div>'.format(
                ct, e["created_at"][:10], e.get("type","idea"), ico, t)
        branches += '<div class="branch" style="--c:{}">' \
                    '<div class="btag">#{}</div>' \
                    '<div class="leaves">{}</div>' \
                    '</div>'.format(c, tag, leaves)
    st = Counter(e.get("type","idea") for e in entries)
    shtml = "".join('<div class="stat"><div class="n">{}</div><div class="l">{} {}</div></div>'.format(
        st.get(k,0), TYPE_EMOJIS.get(k,""), k) for k in ["idea","paper","decision","url"])
    html = (
        "<!DOCTYPE html><html lang='zh'><head><meta charset='UTF-8'>"
        "<title>Mind Map - " + datetime.now().strftime("%Y-%m-%d") + "</title>"
        "<style>"
        "*{box-sizing:border-box;margin:0;padding:0}"
        "body{font-family:-apple-system,sans-serif;background:#1a1a2e;color:#eee;padding:20px}"
        "h1{text-align:center;padding:16px 0 6px;font-size:1.5em;background:linear-gradient(135deg,#6bcb77,#4d96ff);"
        "-webkit-background-clip:text;-webkit-text-fill-color:transparent}"
        ".meta{text-align:center;color:#888;font-size:.82em;margin-bottom:18px}"
        ".stats{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-bottom:20px}"
        ".stat{background:#16213e;border-radius:8px;padding:10px 16px;text-align:center}"
        ".stat .n{font-size:1.4em;font-weight:700;color:#4d96ff}"
        ".stat .l{font-size:.72em;color:#888;margin-top:2px}"
        ".cn{width:120px;height:120px;border-radius:50%;margin:0 auto 24px;"
        "background:linear-gradient(135deg,#4d96ff,#c77dff);display:flex;align-items:center;"
        "justify-content:center;font-weight:700;font-size:.95em;text-align:center;"
        "box-shadow:0 0 28px rgba(77,150,255,.45);padding:10px;line-height:1.4}"
        ".branches{display:flex;flex-wrap:wrap;gap:12px;justify-content:center}"
        ".branch{background:#16213e;border-radius:10px;padding:12px;width:240px;"
        "border-top:3px solid var(--c);transition:transform .2s,box-shadow .2s}"
        ".branch:hover{transform:translateY(-3px);box-shadow:0 6px 20px rgba(0,0,0,.4)}"
        ".btag{font-weight:700;color:var(--c);margin-bottom:8px;font-size:.9em}"
        ".leaf{background:#0f3460;border-radius:6px;padding:6px 9px;margin:4px 0;font-size:.78em;"
        "cursor:pointer;border-left:3px solid var(--c);line-height:1.4;transition:background .15s}"
        ".leaf:hover{background:#1a4a7a}"
        ".dp{position:fixed;right:14px;top:14px;width:280px;background:#16213e;border-radius:10px;"
        "padding:16px;border:1px solid #4d96ff;display:none;z-index:99;box-shadow:0 6px 28px rgba(0,0,0,.6)}"
        ".dp h3{color:#4d96ff;margin-bottom:6px;font-size:.88em}"
        ".dp p{font-size:.78em;line-height:1.6;color:#ccc}"
        ".dc{float:right;cursor:pointer;color:#888;font-size:1em}"
        "</style></head><body>"
        "<h1>Knowledge Mind Map</h1>"
        '<p class="meta">Generated: ' + datetime.now().strftime("%Y-%m-%d %H:%M") + " | " + str(len(entries)) + " entries</p>"
        '<div class="stats">' + shtml + '<div class="stat"><div class="n">' + str(len(tg)) + '</div><div class="l">Tags</div></div></div>'
        '<div class="cn">Knowledge<br>Base</div>'
        '<div class="branches">' + branches + "</div>"
        '<div class="dp" id="dp">'
        '<span class="dc" onclick="document.getElementById(\'dp\').style.display=\'none\'">x</span>'
        '<h3 id="dp-t"></h3><p id="dp-c"></p>'
        '<p style="margin-top:6px;color:#888;font-size:.7em" id="dp-m"></p>'
        "</div>"
        "<script>"
        "function sd(el){"
        "var d=document.getElementById('dp');d.style.display='block';"
        "document.getElementById('dp-t').textContent=el.textContent.trim();"
        "document.getElementById('dp-c').textContent=el.dataset.content;"
        "document.getElementById('dp-m').textContent=el.dataset.date+' - '+el.dataset.type;"
        "}"
        "</script></body></html>"
    )
    with open(output_file, "w", encoding="utf-8") as f: f.write(html)
    print("OK mindmap HTML: " + str(output_file))

# --- flashcard ---
def export_flashcard(data, output_file, task_id=None):
    entries = filter_entries(data, task_id)
    cards = [e for e in entries if e.get("type") in {"idea","paper","decision"}]
    qs = {
        "idea":     "What is the core insight? How to implement?",
        "paper":    "What is the main contribution of this paper?",
        "decision": "Why was this decision made? What were the trade-offs?",
    }
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Flashcards - " + datetime.now().strftime("%Y-%m-%d") + "\n\n")
        f.write("> " + str(len(cards)) + " cards | auto-generated\n\n---\n\n")
        for i,e in enumerate(cards,1):
            tags = " ".join("`{}`".format(t) for t in e.get("tags",[]))
            f.write("## Card {:02d} | {}\n\n".format(i, e["title"]))
            f.write("**Tags**: {}  \n**Date**: {}  \n**Type**: {}\n\n".format(
                tags, e["created_at"][:10], e.get("type","idea")))
            f.write("### Question\n\n" + qs.get(e.get("type","idea"),"Key points?") + "\n\n")
            f.write("<details>\n<summary>Show Answer</summary>\n\n")
            f.write(e["content"] + "\n\n")
            if e.get("source_url"): f.write("Source: " + e["source_url"] + "\n\n")
            f.write("</details>\n\n---\n\n")
    print("OK flashcards ({} cards): {}".format(len(cards), output_file))

# --- table ---
def export_table(data, output_file, task_id=None):
    entries = filter_entries(data, task_id)
    cnt = Counter(e.get("type","idea") for e in entries)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Knowledge Table - " + datetime.now().strftime("%Y-%m-%d") + "\n\n")
        f.write("> " + str(len(entries)) + " entries\n\n## Stats\n\n| Type | Count |\n|---|---|\n")
        for t,n in cnt.most_common():
            f.write("| {} {} | {} |\n".format(TYPE_EMOJIS.get(t,""), t, n))
        f.write("\n## Entries\n\n| # | Type | Title | Tags | Date | Summary |\n|---|---|---|---|---|---|\n")
        for i,e in enumerate(entries,1):
            ico = TYPE_EMOJIS.get(e.get("type","idea"),"")
            title = e["title"][:28].replace("|","I")
            tags = ", ".join(e.get("tags",[])[:3])
            summary = e["content"][:46].replace("\n"," ").replace("|","I") + "..."
            f.write("| {} | {} | {} | {} | {} | {} |\n".format(
                i, ico, title, tags, e["created_at"][:10], summary))
    print("OK table: " + str(output_file))

# --- report ---
def export_report(data, tasks_data, output_file, task_id=None):
    entries = filter_entries(data, task_id)
    tasks = tasks_data.get("tasks",[])
    if task_id: tasks = [t for t in tasks if t["id"]==task_id]
    active_id = tasks_data.get("active_task_id")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Task Knowledge Report\n\n")
        f.write("> Generated: {}  \n> Entries: {}  \n> Tasks: {}\n\n---\n\n".format(
            datetime.now().strftime("%Y-%m-%d %H:%M"), len(entries), len(tasks)))
        for task in tasks:
            star = " (ACTIVE)" if task["id"]==active_id else ""
            pct = task.get("progress",0)
            bar = "#"*(pct//5) + "."*(20-pct//5)
            f.write("## {}{}\n\n".format(task["name"], star))
            f.write("**Progress**: {}%  \n**Status**: {}\n\n```\n[{}] {}%\n```\n\n".format(
                pct, task.get("status","active"), bar, pct))
            for h in task.get("history",[]):
                f.write("- `{}` {} (->{}%)\n".format(h["timestamp"][:10], h["action"], h.get("progress",0)))
            if task.get("blockers"):
                f.write("\n### Blockers\n\n")
                for b in task["blockers"]:
                    f.write("- {}\n".format(b.get("content",b) if isinstance(b,dict) else b))
            task_es = [e for e in entries if e.get("task_id")==task["id"]]
            if task_es:
                f.write("\n### Knowledge ({} entries)\n\n".format(len(task_es)))
                by_type = {}
                for e in task_es: by_type.setdefault(e.get("type","idea"),[]).append(e)
                for t,items in by_type.items():
                    titles = ", ".join(e["title"][:20] for e in items[:5])
                    if len(items)>5: titles += " ... ({} total)".format(len(items))
                    f.write("- {} **{}**: {}\n".format(TYPE_EMOJIS.get(t,""), t, titles))
            if task.get("next_steps"):
                f.write("\n### Next Steps\n\n")
                for ns in task["next_steps"]: f.write("- {}\n".format(ns))
            f.write("\n---\n\n")
        global_es = [e for e in entries if not e.get("task_id")]
        if global_es:
            f.write("## Global Knowledge\n\n")
            for e in global_es:
                f.write("- {} **{}** `{}`\n".format(TYPE_EMOJIS.get(e.get("type","idea"),""), e["title"], e["created_at"][:10]))
    print("OK report: " + str(output_file))

def export_workflow_report(wf, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Workflow Report - " + datetime.now().strftime("%Y-%m-%d") + "\n\n")
        f.write("**Task**: {}  \n**Progress**: {}%\n\n".format(wf.get("current_task","N/A"), wf.get("progress",0)))
        f.write("## History\n\n")
        for h in wf.get("history",[])[-10:]:
            f.write("- [{}] {} ({}%)\n".format(h["timestamp"][:10], h["action"], h.get("progress",0)))
        f.write("\n## Blockers\n\n")
        for b in wf.get("blockers",[]): f.write("- {}\n".format(b))
        f.write("\n## Next Steps\n\n")
        for ns in wf.get("next_steps",[]): f.write("- {}\n".format(ns))
    print("OK workflow report: " + str(output_file))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", default=str(DEFAULT_INSP_FILE))
    p.add_argument("--tasks-file", default=str(DEFAULT_TASKS_FILE))
    p.add_argument("--workflow", action="store_true")
    p.add_argument("--task-id", default=None)
    p.add_argument("--format", choices=["markdown","json","mermaid","mindmap","flashcard","table","report"], default="markdown")
    p.add_argument("--output", required=True)
    p.add_argument("--all", action="store_true")
    args = p.parse_args()
    out = Path(args.output)
    ensure_dirs(out.parent)
    if args.workflow:
        export_workflow_report(load_json_file(DEFAULT_WORKFLOW_FILE,{}), out); return
    data = load_inspirations(Path(args.file))
    if not args.all:
        data["entries"] = [e for e in data["entries"] if e.get("status")!="archived"]
    fmt, tid = args.format, args.task_id
    if fmt=="markdown":   export_markdown(data, out, tid)
    elif fmt=="json":     export_json_fmt(data, out)
    elif fmt=="mermaid":  export_mermaid(data, out, tid)
    elif fmt=="mindmap":  export_mindmap(data, out, tid)
    elif fmt=="flashcard":export_flashcard(data, out, tid)
    elif fmt=="table":    export_table(data, out, tid)
    elif fmt=="report":
        td = load_json_file(Path(args.tasks_file),{"tasks":[],"active_task_id":None})
        export_report(data, td, out, tid)

if __name__=="__main__":
    main()
