# Notes for SEC-registered investment advisers and similar firms

**Not legal advice.** This is a plain-language summary of primary sources, written for people
choosing local AI tools. It is not a substitute for a securities lawyer or compliance consultant.
Rules, dates and enforcement priorities change; check current status before relying on anything
here. Everything was read on 2026-09-24.

**How sources are marked.** Regulatory statements point to sec.gov. Three sec.gov PDFs (the
Regulation S-P final rule, the withdrawal notice and the FY2026 exam priorities) could not be
text-extracted reliably in the research session, so points that rest on them were cross-checked
against law-firm summaries and are marked `[UNVERIFIED against primary text]`. Open the PDFs to
confirm. Links that are not sec.gov are labeled as such.

## 1. Regulation S-P, as amended in 2024

Covers "covered institutions," including SEC-registered investment advisers, broker-dealers,
investment companies and transfer agents.

- Final rule: [Release No. 34-100155](https://www.sec.gov/files/rules/final/2024/34-100155.pdf).
- [Small entity compliance guide](https://www.sec.gov/files/rules/final/2024/regulation-s-p-small-entity-compliance-guide.pdf).
- Adopted May 2024, effective August 2, 2024. [UNVERIFIED against primary text; effective date comes from
  law-firm reporting.]

What changed:

- **Incident response program.** Written policies and procedures reasonably designed to detect,
  respond to and recover from unauthorized access to or use of customer information, including
  assessing the nature and scope of an incident and containing it.
- **Customer notice within 30 days.** Notify affected individuals whose sensitive customer
  information was, or is reasonably likely to have been, accessed or used without authorization, as
  soon as practicable and no later than 30 days after becoming aware. The U.S. Attorney General
  can determine that notice poses a substantial national security or public safety risk and delay
  it. [UNVERIFIED against primary text]
- **Service providers.** Keep written policies and procedures reasonably designed to require
  oversight, including through due diligence and monitoring, of service providers. Those policies
  and procedures must be reasonably designed to ensure you receive timely notice from a provider
  that has had a breach of a system holding customer information (the 72-hour period comes from
  law-firm reporting, [UNVERIFIED against primary text]; the proposal said 48). The final rule does
  not require a contract. Source: SEC
  [fact sheet for Release 34-100155](https://www.sec.gov/files/34-100155-fact-sheet.pdf).
- **Recordkeeping.** Document the incident response program, the assessments and the notices, within
  each entity type's existing books-and-records rules. For advisers this sits beside Rule 204-2
  (section 3). [UNVERIFIED against primary text]

**Compliance dates.** The rule was published in the Federal Register on June 3, 2024
([document 2024-11116](https://www.federalregister.gov/d/2024-11116), not sec.gov). Per SEC
[press release 2024-58](https://www.sec.gov/newsroom/press-releases/2024-58), larger entities
comply 18 months after publication (December 3, 2025) and smaller entities 24 months after
(June 3, 2026). The size threshold for "smaller" (roughly $1.5 billion in assets under management for
advisers, from law-firm summaries) is [UNVERIFIED against primary text]. **Both dates have passed
as of 2026-09-24**, so the amended requirements apply to every SEC-registered adviser.

## 2. Regulation S-ID

Regulation S-ID (17 CFR 248.201 to 248.202, identity theft red flags) is a separate, older rule
requiring firms with "covered accounts" to keep a written identity theft prevention program. The
research found no change to it in the 2024 S-P amendments: the SEC's compliance guide does not
describe one. That conclusion is inferred from absence, so treat it as [UNVERIFIED as a definitive
rule-history check]. Text: [17 CFR 248.201 at Cornell](https://www.law.cornell.edu/cfr/text/17/248.201)
(not sec.gov). The SEC's [December 2022 risk alert](https://www.sec.gov/files/risk-alert-reg-s-id-120522.pdf)
lists common S-ID deficiencies.

Practical point: if your firm offers or maintains covered accounts, AI tools that touch client
identity data (onboarding, KYC, fraud screening) fall under your S-ID program. S-P does not
replace it. If you have no covered accounts, S-ID does not apply to you.

## 3. Rule 204-2 and AI-generated content

[Rule 204-2](https://www.law.cornell.edu/cfr/text/17/275.204-2) (text at Cornell, not sec.gov;
sec.gov copy not read) requires registered advisers to keep records relating to their advisory
business, including written communications about recommendations and advice, generally five years,
the first two in an easily accessible place. It has no AI-specific text.

The practical reading below is from securities counsel (Skadden, September 2024,
[article](https://www.skadden.com/insights/publications/2024/09/how-and-when-sec-recordkeeping-rules-may-apply)),
**not from the SEC**:

- The trigger is whether the content is a written communication that is sent and received, not
  whether AI made it.
- An AI note or summary that stays inside an internal tool and is never sent generally does not by
  itself trigger retention.
- Once AI-generated content goes to a client or counterparty and falls in a category the rule
  covers (recommendations, advice, performance, order-related messages), keep it like any other
  written communication.
- Document what data an AI tool was trained or fine-tuned on, and keep records that support your claims
  about how you use AI.

A 2023 SEC proposal would have added AI-specific recordkeeping; it was withdrawn (section 5).

## 4. The Marketing Rule and the 2024 "AI washing" actions

On March 18, 2024, the SEC announced its first actions charging AI-related misrepresentations,
including under the Marketing Rule and Compliance Rule. Source: SEC
[press release 2024-36](https://www.sec.gov/newsroom/press-releases/2024-36).

- **Delphia (USA) Inc.:** said in filings, press materials and its website that it used AI and
  machine learning on client data to predict winning companies and trends, when it had not built the
  algorithm it described. Penalty $225,000.
- **Global Predictions Inc.:** called itself the "first regulated AI financial advisor" and claimed
  AI-driven forecasts it did not have, plus other false claims. Penalty $175,000.
- Combined penalties $400,000.

The takeaway under Rule 206(4)-1 is that any AI claim in marketing, a website, a pitch deck or a
brochure must be true and supportable. Using a chatbot for drafting does not by itself make "we use AI"
false. These cases are about describing accurately how you use AI and what it does. Claiming a "private" or "local"
setup you cannot demonstrate belongs in the same category.

## 5. The withdrawn 2023 predictive data analytics proposal

In 2023 the SEC proposed "Conflicts of Interest Associated with the Use of Predictive Data Analytics
by Broker-Dealers and Investment Advisers" (July 26, 2023, Release No. 34-97990). It would have
required firms to eliminate or neutralize, not just disclose, conflicts from AI and similar tools.

- SEC docket page: [S7-12-23](https://www.sec.gov/rules-regulations/2025/06/s7-12-23).
- **Withdrawn.** On June 12, 2025 the SEC issued a notice (Release Nos. 33-11377 and 34-103247)
  withdrawing it and 13 other pending proposals, effective June 17, 2025, and said it does not intend
  to issue final rules on them. [Notice](https://www.sec.gov/files/rules/final/2025/33-11377.pdf)
  [UNVERIFIED against primary text for the list and dates; cross-checked against the Federal Register
  entry (not sec.gov) and law-firm summaries.]

Effect: no SEC rule specifically governs predictive-data-analytics conflicts today. General
fiduciary duty and the Marketing Rule still apply.

## 6. FY2026 exam priorities

The Division of Examinations announced its 2026 priorities on November 17, 2025
([press release 2025-132](https://www.sec.gov/newsroom/press-releases/2025-132-sec-division-examinations-announces-2026-priorities);
the release itself does not use the word "AI"). AI appears in the
[full priorities document](https://www.sec.gov/files/2026-exam-priorities.pdf). That PDF could not be
extracted, so what follows is from several law-firm summaries that agree with each other (Akin Gump,
Goodwin, Dorsey, Grant Thornton, Katten, Comply): [UNVERIFIED against primary text]

- AI is treated as a cross-cutting risk, not one line item.
- Examiners will compare what firms say about their AI use to what they do.
- For firms using AI in the advisory process, expect questions on accurate representations,
  controls over the tools, and whether output fits each client's stated profile.
- AI adoption is named as a driver of cybersecurity and operational-resilience risk, including
  vendor oversight and training on AI-assisted attacks.
- Expect sweeps of likely early adopters such as robo-advisers.

A separate claim about a September 2026 SEC definition of "AI washing" and a draft strategic plan came
from an aggregator and could not be traced to sec.gov. It is [UNVERIFIED] and not relied on. No
other 2025 to 2026 AI-specific SEC rule was found; check the SEC's rulemaking agenda and recent
risk alerts, because this area moves.

## 7. What a local-first setup helps with, and what it does not

Saying local AI equals compliance would be its own kind of AI washing.

**Helps:**

- **Fewer service providers.** Client data that never reaches a third-party API means fewer vendors
  needing Regulation S-P due diligence, oversight and breach-notice arrangements. The model
  weights, runtime and libraries are still third-party software to evaluate; see the license and
  telemetry notes in [models](models/README.md), [search](search/README.md) and [pii](pii/README.md).
- **Logging you own.** Local systems can record prompts, retrieved documents and outputs in a form
  you control, which supports Rule 204-2 retention and lets you show an examiner how a tool was used.
- **Retention you set.** You choose retention and deletion instead of inheriting a vendor's policy.
- **Smaller exposure.** Fewer outbound transmissions of customer information means fewer chances for
  the unauthorized access events that trigger S-P incident response and notice.

**Does not solve:**

- **Disclosure and marketing duties.** Claims about what your AI does must be accurate wherever it
  runs. The Delphia and Global Predictions cases were about describing AI use inaccurately, not about using AI.
- **The programs.** You still need the S-P incident response program, and the S-ID program if you have covered accounts. A
  compromised or misconfigured local system, or an unauthorized insider, is still an incident.
- **No new AI-conflicts rule to satisfy, and none replaced.** The withdrawn proposal leaves ordinary
  fiduciary analysis in place for AI-influenced recommendations.
- **Records do not appear by themselves.** A local model with no logging leaves you with nothing to
  retain or show. You have to build logging, retention and retrieval.
- **A written information security program.** On-premises is not the same as adequately safeguarded:
  access controls, patching and testing still apply to your own hardware.
- **Provenance.** If a model was trained on nonpublic or third-party proprietary data, running it locally
  does not fix that. Document what you can about training data, as the Skadden piece advises.
- **Detection is imperfect.** See the accuracy notes in [pii](pii/README.md) and the limits of the
  routing model in [classifiers](classifiers/README.md).

## Not covered

State law, FINRA-specific AI guidance, non-SEC federal guidance such as NIST frameworks, and any
firm-specific procedure. Re-check the compliance dates and rule status against the primary
sources before use.
