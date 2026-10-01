"""CYBERNEXSUS engine: demo data, company policies and the 7-agent analysis."""
import re

CUSTOMERS = [
    {"id": "C1", "name": "Aarav Mehta", "tier": "Gold", "ltv": 84000, "prior": [{"i": "delivery", "n": 0}], "email": "aarav@example.com"},
    {"id": "C2", "name": "Priya Nair", "tier": "Standard", "ltv": 12500, "prior": [], "email": "priya@example.com"},
    {"id": "C3", "name": "Rohan Verma", "tier": "Platinum", "ltv": 312000, "prior": [{"i": "late", "n": 3}, {"i": "refund", "n": 1}], "email": "rohan@example.com"},
    {"id": "C4", "name": "Sneha Kulkarni", "tier": "Standard", "ltv": 6200, "prior": [{"i": "refund", "n": 1}], "email": "sneha@example.com"},
    {"id": "C5", "name": "Imran Shaikh", "tier": "Gold", "ltv": 67000, "prior": [], "email": "imran@example.com"},
]
ORDERS = [
    {"id": "O-1001", "c": "C1", "item": "Wireless headphones", "amt": 3499, "status": "Delivered", "days": 10, "pay": "Charged twice", "dup": True},
    {"id": "O-1002", "c": "C2", "item": "Kitchen mixer", "amt": 6999, "status": "Delivered", "days": 5, "pay": "Paid", "dup": False},
    {"id": "O-1003", "c": "C3", "item": "Laptop 15-inch", "amt": 58999, "status": "In transit", "days": 12, "pay": "Paid", "dup": False},
    {"id": "O-1004", "c": "C4", "item": "Running shoes", "amt": 1999, "status": "Delivered", "days": 25, "pay": "Paid", "dup": False},
    {"id": "O-1005", "c": "C5", "item": "Smartphone", "amt": 24999, "status": "Delivered", "days": 3, "pay": "Paid", "dup": False},
    {"id": "O-1006", "c": "C1", "item": "Phone case", "amt": 499, "status": "In transit", "days": 9, "pay": "Paid", "dup": False},
]
POLICIES = {
    "dup": {"id": "P1", "title": "Duplicate charge", "text": "Refund the extra charge once the payment gateway confirms it. Auto-approve up to ₹10,000."},
    "damaged": {"id": "P2", "title": "Damaged on arrival", "text": "Replace or refund within 30 days of delivery. Auto-approve up to ₹10,000; above that a human checks photos."},
    "late": {"id": "P3", "title": "Late delivery", "text": "For delays over 7 days give 10% store credit and expedite. Orders over ₹25,000 or 3+ repeat delay tickets go to a human."},
    "refund": {"id": "P4", "title": "Returns and refunds", "text": "Refund within 7 days of delivery. After that, offer an exchange or 20% store credit."},
    "fraud": {"id": "P5", "title": "Fraud and unauthorised payments", "text": "Never decided by AI. Escalate to the Security team immediately and freeze the order."},
    "legal": {"id": "P6", "title": "Legal threats", "text": "Never decided by AI. Escalate to Legal and a senior support lead."},
    "other": {"id": "P7", "title": "Unclear requests", "text": "If the AI is less than 70% confident, a human takes over."},
}
SEED = [
    {"id": "T-101", "c": "C1", "o": "O-1001", "t": "I was charged twice for my headphones. The money left my account two times and I want the extra amount back."},
    {"id": "T-102", "c": "C2", "o": "O-1002", "t": "My mixer arrived broken, the jar is cracked. Please send a replacement."},
    {"id": "T-103", "c": "C3", "o": "O-1003", "t": "This is the THIRD time my order is late! Still waiting 12 days after the promised date. This is unacceptable!!"},
    {"id": "T-104", "c": "C4", "o": "O-1004", "t": "I want a refund for my shoes, I just don't like them any more."},
    {"id": "T-105", "c": "C5", "o": "O-1005", "t": "There is an unauthorized transaction on my card linked to this order. I did not place it. I think my account was hacked."},
    {"id": "T-106", "c": "C1", "o": "O-1006", "t": "Where is my phone case? It is delayed by more than a week."},
]
LABELS = {"dup": "Duplicate charge", "damaged": "Damaged item", "late": "Late delivery", "refund": "Refund / return",
          "fraud": "Suspected fraud", "legal": "Legal threat", "other": "Unclear"}
BASE_SCORE = {"dup": 2, "damaged": 2, "late": 2, "refund": 1, "fraud": 4, "legal": 4, "other": 2}


def cust(cid):
    return next((c for c in CUSTOMERS if c["id"] == cid), None)


def order(oid):
    return next((o for o in ORDERS if o["id"] == oid), None)


def inr(n):
    """Indian digit grouping, e.g. 312000 -> ₹3,12,000"""
    s = str(int(n))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts) + "," + tail
    return "₹" + s


def detect_intent(text):
    x = text.lower()
    if re.search(r"lawyer|legal|consumer court|sue ", x): return "legal"
    if re.search(r"fraud|unauthori[sz]ed|hacked|did not place", x): return "fraud"
    if re.search(r"twice|double|duplicate", x): return "dup"
    if re.search(r"damag|broken|crack|defect", x): return "damaged"
    if re.search(r"late|delay|not arrived|still waiting|where is", x): return "late"
    if re.search(r"refund|return|money back", x): return "refund"
    return "other"


def analyze(ticket):
    c, o, text = cust(ticket["c"]), order(ticket["o"]), ticket["t"]
    steps = []

    # 1. Intent agent
    intent = detect_intent(text)
    angry = len(re.findall(r"!|unacceptable|worst|furious|third time", text, re.I)) + len(re.findall(r"\b[A-Z]{4,}\b", text))
    mood = "Angry" if angry >= 3 else "Frustrated" if angry >= 1 else "Calm"
    steps.append({"a": "Intent agent", "f": f"Classified as “{LABELS[intent]}”. Customer sentiment: {mood}."})

    # 2. Customer history agent
    rep = sum(p["n"] for p in c["prior"] if p["i"] == intent)
    total = sum(p["n"] for p in c["prior"])
    steps.append({"a": "Customer history agent",
                  "f": f"{c['name']} is {c['tier']} tier, lifetime spend {inr(c['ltv'])}. {total} earlier ticket(s), {rep} on the same issue."})

    # 3. Order / transaction agent
    since = "delivery" if o["status"] == "Delivered" else "the promised date"
    steps.append({"a": "Order / transaction agent",
                  "f": f"{o['id']} · {o['item']} · {inr(o['amt'])}. Status: {o['status']}, {o['days']} day(s) since {since}. Payment: {o['pay']}."})

    # 4. Policy / RAG agent
    p = POLICIES[intent]
    steps.append({"a": "Policy / RAG agent", "f": f"Retrieved {p['id']} “{p['title']}”: {p['text']}"})

    # 5. Root cause agent
    conf = 0.92
    cause = ""
    if intent == "dup":
        cause = "Payment gateway captured the order twice (confirmed in the transaction log)." if o["dup"] else "No duplicate found in the transaction log."
        if not o["dup"]: conf = 0.5
    elif intent == "damaged": cause = "Likely packaging or courier damage during transit."
    elif intent == "late": cause = "Repeated courier delay on this customer’s route." if rep >= 3 else "Courier delay beyond the promised date."
    elif intent == "refund": cause = "Change of mind, requested after the 7-day return window." if o["days"] > 7 else "Change of mind inside the return window."
    elif intent == "fraud": cause = "Possible account takeover or card misuse. Needs a security investigation."
    elif intent == "legal": cause = "Customer is considering legal action."
    else:
        cause = "Could not match the complaint to a known category."
        conf = 0.55
    steps.append({"a": "Root cause agent", "f": cause})

    # Escalation rules (decided before the resolution is written)
    reason = None
    if intent in ("fraud", "legal"):
        reason = f"{p['title']} cases are never decided by AI."
    elif intent == "late" and (o["amt"] > 25000 or rep >= 3):
        bits = []
        if o["amt"] > 25000: bits.append(f"High-value order ({inr(o['amt'])})")
        if rep >= 3: bits.append(f"{rep} repeat tickets on the same issue")
        reason = f"{' and '.join(bits)}. Policy {p['id']} requires a human."
    elif intent == "damaged" and o["amt"] > 10000:
        reason = "Refund above ₹10,000 needs photo verification by a human."
    elif intent == "dup" and (o["amt"] > 10000 or not o["dup"]):
        reason = "Duplicate charge could not be verified." if not o["dup"] else "Amount above the auto-approve limit."
    elif conf < 0.7:
        reason = f"Confidence {round(conf * 100)}% is below the 70% threshold."
    elif mood == "Angry" and c["tier"] == "Platinum":
        reason = "Angry Platinum customer – relationship risk."

    # 6. Resolution agent
    action = ""
    if not reason:
        if intent == "dup": action = f"Refund the extra charge of {inr(o['amt'])} to the original payment method (3–5 working days)."
        elif intent == "damaged": action = f"Send a free replacement {o['item'].lower()} with pickup of the damaged one. No cost to customer."
        elif intent == "late": action = f"Credit {inr(round(o['amt'] * 0.1))} (10%) as store credit and mark the shipment as priority."
        elif intent == "refund":
            action = (f"Refund window closed ({o['days']} days). Offer an exchange or {inr(round(o['amt'] * 0.2))} store credit (20%)."
                      if o["days"] > 7 else f"Approve a full refund of {inr(o['amt'])}.")
    steps.append({"a": "Resolution agent",
                  "f": "No safe automatic action. Preparing a handoff summary." if reason else f"Proposed: {action}"})

    # Severity
    score = (BASE_SCORE[intent] + (c["tier"] == "Platinum") + (o["amt"] > 25000) + (mood == "Angry") + (rep >= 3))
    sev = "Critical" if score >= 6 else "High" if score >= 4 else "Medium" if score >= 3 else "Low"

    # 7. Escalation agent
    team = ("Security team" if intent == "fraud" else "Legal" if intent == "legal" else "Support lead") if reason else "AI agent"
    who = "Security team" if intent == "fraud" else "Legal + senior lead" if intent == "legal" else "human support lead"
    steps.append({"a": "Escalation agent",
                  "f": f"ESCALATE to {who}. Reason: {reason}" if reason
                  else f"No escalation needed. Confidence {round(conf * 100)}%. Case closed automatically."})

    dec = {"type": "Escalated" if reason else "Resolved",
           "action": f"Hand over to a human. {reason}" if reason else action,
           "conf": conf, "sev": sev, "cause": cause, "intent": LABELS[intent], "mood": mood, "team": team}
    return {"steps": steps, "dec": dec}
