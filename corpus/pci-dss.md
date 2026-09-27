# PCI DSS — Payment Card Industry Data Security Standard

PCI DSS is a security standard for any organization that stores, processes, or transmits payment-card data. It is maintained by the PCI Security Standards Council and enforced through the card brands and acquiring banks rather than by a government.

## What it protects

The standard centers on cardholder data — primarily the Primary Account Number (PAN) — and sensitive authentication data. A recurring theme is to not store what you do not need: sensitive authentication data must not be retained after authorization, and the PAN must be rendered unreadable (for example through strong cryptography) wherever it is stored.

## The control areas

The requirements group into goals such as building and maintaining a secure network (firewalls, no vendor default passwords), protecting stored cardholder data and encrypting it in transit, running a vulnerability-management program (anti-malware, secure development), enforcing strong access control on a need-to-know basis, regularly monitoring and testing networks (logging, file integrity, and vulnerability scans, including quarterly external scans by an Approved Scanning Vendor), and maintaining an information-security policy.

## Scope reduction

Because the requirements apply to the cardholder data environment, organizations reduce cost and risk through network segmentation that isolates card systems, and through tokenization or outsourcing that keeps raw card data out of their environment entirely.
