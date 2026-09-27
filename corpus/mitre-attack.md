# MITRE ATT&CK

MITRE ATT&CK is a public knowledge base of adversary behavior, organized as tactics and techniques observed in real intrusions. It gives defenders a shared vocabulary for describing what an attacker did, independent of any single vendor's tooling.

## Tactics and techniques

A tactic is the attacker's goal at a stage of an intrusion — for example Initial Access, Execution, Persistence, Privilege Escalation, Defense Evasion, Credential Access, Discovery, Lateral Movement, Collection, Command and Control, Exfiltration, and Impact. A technique is a specific way that goal is achieved. Every technique has a stable identifier of the form Txxxx, and many have sub-techniques written Txxxx.yyy.

Examples of technique IDs:
- T1190 — Exploit Public-Facing Application (gaining initial access by exploiting an internet-facing service).
- T1059 — Command and Scripting Interpreter (executing commands through shells such as PowerShell or bash).
- T1078 — Valid Accounts (using legitimate credentials to blend in).
- T1486 — Data Encrypted for Impact (ransomware-style encryption of victim data).

## How defenders use it

Detection engineers map each detection rule to the technique it catches, so coverage can be measured against the matrix instead of guessed. Mapping findings to ATT&CK IDs also lets a report say precisely which adversary behavior was seen, which makes triage, threat hunting, and purple-team exercises repeatable. The framework is a mapping and communication tool, not a scanner: it describes behavior, and it is up to the detection and telemetry to observe that behavior.
