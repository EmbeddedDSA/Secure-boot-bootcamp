#!/usr/bin/env python3
"""Score log and spaced-repetition queue for the course.

Rules (CLAUDE.md, Rule 5):
  * every graded answer is appended to progress/scores.json
  * a topic scoring below 3 enters the queue, due 3 days later
  * each later review: a 3 advances it to the next interval (10, then 30 days);
    anything below 3 resets it to the 3-day interval
  * a topic leaves the queue after two 3s in a row

Usage:
  srs.py log --module 1 --topic "fuse holds key hash" --kind recall \
             --score 2 --question "..." [--model-answer "..."] [--date YYYY-MM-DD]
  srs.py due [--date YYYY-MM-DD]      list queue items due on or before date
  srs.py queue                        list the whole queue
  srs.py avg                          grill average per module
"""
import argparse
import datetime as dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCORES = os.path.join(ROOT, "progress", "scores.json")
KINDS = ("recall", "mechanism", "flaw", "scenario", "ceiling", "repetition", "oral", "mock")


def load():
    with open(SCORES) as f:
        return json.load(f)


def save(data):
    tmp = SCORES + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    os.replace(tmp, SCORES)


def parse_date(s):
    return dt.date.fromisoformat(s) if s else dt.date.today()


def update_queue(data, module, topic, question, score, day):
    intervals = data["repetition_intervals_days"]
    queue = data["repetition_queue"]
    item = next((q for q in queue if q["topic"] == topic and q["module"] == module), None)

    if item is None:
        if score >= 3:
            return "not in queue; nothing to do"
        queue.append({
            "module": module, "topic": topic, "question": question,
            "added": day.isoformat(), "stage": 0, "streak": 0,
            "next_due": (day + dt.timedelta(days=intervals[0])).isoformat(),
        })
        return f"queued, due {queue[-1]['next_due']}"

    item["question"] = question
    if score >= 3:
        item["streak"] += 1
        if item["streak"] >= 2:
            queue.remove(item)
            return "two 3s in a row: removed from queue"
        item["stage"] = min(item["stage"] + 1, len(intervals) - 1)
    else:
        item["streak"] = 0
        item["stage"] = 0
    item["next_due"] = (day + dt.timedelta(days=intervals[item["stage"]])).isoformat()
    return f"rescheduled, due {item['next_due']} (streak {item['streak']})"


def cmd_log(a):
    if not 0 <= a.score <= 3:
        sys.exit("score must be 0..3")
    data = load()
    day = parse_date(a.date)
    data["entries"].append({
        "date": day.isoformat(), "module": a.module, "topic": a.topic,
        "kind": a.kind, "question": a.question, "score": a.score,
        "model_answer": a.model_answer or "",
    })
    msg = update_queue(data, a.module, a.topic, a.question, a.score, day)
    save(data)
    print(f"logged score {a.score} for '{a.topic}': {msg}")


def cmd_due(a):
    day = parse_date(a.date)
    due = [q for q in load()["repetition_queue"] if dt.date.fromisoformat(q["next_due"]) <= day]
    if not due:
        print("nothing due")
    for q in sorted(due, key=lambda q: q["next_due"]):
        print(f"[M{q['module']:02d}] due {q['next_due']}  {q['topic']}\n        Q: {q['question']}")


def cmd_queue(_):
    q = load()["repetition_queue"]
    if not q:
        print("queue empty")
    for i in sorted(q, key=lambda q: q["next_due"]):
        print(f"[M{i['module']:02d}] {i['next_due']}  streak={i['streak']}  {i['topic']}")


def cmd_avg(_):
    by = {}
    for e in load()["entries"]:
        if e["kind"] in ("oral", "mock", "repetition"):
            continue
        by.setdefault(e["module"], []).append(e["score"])
    if not by:
        print("no scores yet")
    for m in sorted(by):
        s = by[m]
        print(f"M{m:02d}: {sum(s)/len(s):.2f} over {len(s)} answers")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    lg = sub.add_parser("log")
    lg.add_argument("--module", type=int, required=True)
    lg.add_argument("--topic", required=True)
    lg.add_argument("--kind", choices=KINDS, required=True)
    lg.add_argument("--score", type=int, required=True)
    lg.add_argument("--question", required=True)
    lg.add_argument("--model-answer")
    lg.add_argument("--date")
    lg.set_defaults(fn=cmd_log)
    d = sub.add_parser("due")
    d.add_argument("--date")
    d.set_defaults(fn=cmd_due)
    sub.add_parser("queue").set_defaults(fn=cmd_queue)
    sub.add_parser("avg").set_defaults(fn=cmd_avg)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
