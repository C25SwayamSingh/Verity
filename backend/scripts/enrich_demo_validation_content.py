"""One-time helper: add analyzable `content` to Phase 3.10 validation creator posts."""
import json
from pathlib import Path

CONTENT: dict[str, str] = {
    # creator-001 — Nova Rivera (tech_ai)
    "post-001-a": (
        "This segment summarizes the EU AI Act using the official EUR-Lex text and reporting from "
        "MIT Technology Review. The law classifies artificial intelligence systems into four risk tiers: "
        "unacceptable, high, limited, and minimal. High-risk systems require conformity assessments before "
        "deployment in the European Union. European Parliament materials state that real-time biometric "
        "surveillance in public spaces is prohibited except for narrow law-enforcement exceptions. "
        "This is explanatory journalism about AI regulation, not legal advice."
    ),
    "post-001-b": (
        "We're reviewing a new code-generation model described in an ArXiv preprint and benchmarked by "
        "The Verge. The model reportedly scores 87% on HumanEval, above the prior published benchmark leader. "
        "I think most software engineers could become redundant within two years — that's my prediction, not "
        "a consensus forecast. Independent testers note the system still struggles with multi-file reasoning "
        "across large codebases. Viewers should treat employment impact claims as speculation."
    ),
    "post-001-c": (
        "Federated learning trains models without centralizing raw user data, according to Google's AI blog "
        "and peer-reviewed work in Nature AI. In typical designs, raw data stays on the device while only "
        "model updates are shared. Google documents federated learning for Gboard keyboard suggestions. "
        "Security researchers at USENIX have shown gradient inversion attacks can partially reconstruct "
        "training data under certain assumptions. This explainer focuses on privacy architecture tradeoffs."
    ),
    "post-001-d": (
        "Today's debate compares open-weight and proprietary large language models. I previously said "
        "open-source AI models are consistently safer than proprietary ones — that was an oversimplification. "
        "Meta's Llama 3 release notes and Anthropic safety evaluations suggest benchmark outcomes vary by "
        "harm category and evaluation setup. Policy discussion should separate access, transparency, and "
        "documented red-team results rather than a single safety ranking."
    ),
    "post-001-e": (
        "Transformer self-attention lets each token attend to other tokens in a sequence, as described in "
        "Vaswani et al., Attention Is All You Need (2017), and visualized in The Illustrated Transformer. "
        "The 2017 paper introduced the architecture that later scaled to modern large language models. "
        "This episode is a technical explainer on machine learning fundamentals for a general audience."
    ),
    # creator-002 — Marcus Webb (domestic_us / politics)
    "post-002-a": (
        "This newsletter walks through a proposed federal voting rights bill using the Congressional Record "
        "and GovTrack sponsor data. Section 4 would require at least 15 days of early voting in federal elections "
        "under the draft text. As of publication, GovTrack lists 42 House co-sponsors. The ACLU's summary notes "
        "preemption questions over state election administration. I'm summarizing legislative text, not endorsing "
        "the bill."
    ),
    "post-002-b": (
        "The Office of Management and Budget released discretionary spending tables compared with last fiscal year. "
        "POLITICO reports defense spending would rise about 4.2% in the proposal. Congressional Budget Office "
        "tables show environmental protection accounts facing an 18% reduction relative to the prior baseline. "
        "In my view, this budget could stall meaningful federal climate policy for years — that is analysis, not "
        "a scored forecast from the CBO."
    ),
    "post-002-c": (
        "A federal agency published a regulatory notice in the Federal Register at 5:47 p.m. on Friday. "
        "Some commentators argue late-Friday releases reduce news coverage; I suggested the administration "
        "deliberately timed this announcement to suppress voter turnout. I have not cited internal planning "
        "documents proving intent. This thread mixes a verifiable publication timestamp with unattributed "
        "motivation claims."
    ),
    "post-002-d": (
        "Using TV Eyes monitoring, Media Matters counted no primetime segments on this policy topic across five "
        "major cable networks in the past week. I also claimed corporate media is coordinating talking points on "
        "the issue without providing emails, contracts, or editorial directives. The observation about airtime "
        "may be checkable; the coordination claim needs stronger sourcing."
    ),
    "post-002-e": (
        "Gerrymandering metrics and court precedent explained with materials from the Princeton Gerrymandering "
        "Project and the Brennan Center. The efficiency gap measures wasted votes between parties in district maps. "
        "In Rucho v. Common Cause, the Supreme Court held federal courts cannot adjudicate partisan gerrymandering "
        "claims. This piece is a civics explainer on redistricting litigation in the United States."
    ),
    # creator-004 — DataDave (markets_stocks / finance)
    "post-004-a": (
        "Earnings season basics using the SEC investor guide and Bloomberg education materials. Earnings per share "
        "equals net income divided by shares outstanding. Academic summaries cited by Bloomberg note companies that "
        "beat consensus EPS estimates often see positive short-term price reactions on average, though outcomes vary "
        "by sector and macro conditions. This is general market education, not a buy or sell recommendation."
    ),
    "post-004-b": (
        "I'm long this ticker and sharing a cup-and-handle chart from TradingView. I said the stock is guaranteed to "
        "double in 90 days based on the pattern — that certainty goes beyond what technical analysis literature "
        "supports. Some sector studies find cup-and-handle breakouts precede rallies in subsets of historical data, "
        "but patterns fail often. Disclosure: personal position; not investment advice."
    ),
    "post-004-c": (
        "This short video questions U.S. inflation data. I claimed the Federal Reserve is lying about inflation to "
        "protect Wall Street without citing BLS methodology audits. The Bureau of Labor Statistics documents "
        "substitution effects in CPI construction, which can lower reported inflation when consumers switch goods. "
        "Skepticism about measurement is not the same as documented fraud."
    ),
    "post-004-d": (
        "Thread on banks and market crashes. I alleged every major bank knew a crash was coming and shorted clients "
        "without court filings or trading records attached. The SEC's 2010 Goldman Sachs Abacus enforcement release "
        "documents a specific CDO marketing case — that is not proof of a universal pre-crash strategy. Mixing one "
        "enforcement example with a broad accusation weakens source alignment."
    ),
    "post-004-e": (
        "Federal Reserve explainer using official Fed communications and Bureau of Labor Statistics releases. "
        "Congress assigned the Fed a dual mandate: maximum employment and stable prices. Policymakers reference a "
        "2% inflation objective using the personal consumption expenditures price index. This video summarizes "
        "mainstream macro reporting on interest rates and inflation in the United States economy."
    ),
}

TARGET_CREATORS = {"creator-001", "creator-002", "creator-004"}


def main() -> None:
    path = Path(__file__).resolve().parents[1] / "app/providers/fixtures/creator_posts.json"
    posts = json.loads(path.read_text())
    updated = 0
    for post in posts:
        pid = post["post_id"]
        if post["creator_id"] in TARGET_CREATORS and pid in CONTENT:
            post["content"] = CONTENT[pid]
            updated += 1
    path.write_text(json.dumps(posts, indent=2) + "\n")
    print(f"Updated {updated} posts in {path}")


if __name__ == "__main__":
    main()
