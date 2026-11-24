Welcome to Your AI-Enabled SWE Coding Interview
You are working on the invoice statement generator for a theatrical company. You have full access to the AI Assistant and the unit test suite.

What We Need You to Do
Fix the Comedy Audience Surcharge Boundary Bug:
For "comedy" plays, the base cost is $300.00 (30000 cents) plus $3.00 (300 cents) per attendee. Only when the audience is strictly greater than 20 (audience > 20) should we add the $100.00 (10000 cents) surcharge plus $5.00 (500 cents) per attendee over 20.
Right now, an audience of exactly 20 people is being overcharged.
Support "history" Plays & the Cross-Play Repertoire Bonus:
Base cost for "history": $350.00 (35000 cents). If audience > 25, add $15.00 (1500 cents) for each attendee over 25.
Base volume credits for "history": max(audience - 25, 0) + floor(audience / 10).
Cross-Play Repertoire Bonus: If the invoice contains at least one "tragedy" play AND at least one "history" play (regardless of which one appears first in the invoice's performance list), every "history" performance on that invoice earns double (2x) its volume credits.
Add an HTML Statement Renderer:
Implement an HTML statement function returning an HTML representation with the exact same figures as the plain-text statement(invoice, plays), refactored cleanly so pricing and credit formulas are never duplicated across the two output formats.
Please explore the codebase, re-enable any disabled tests in the test suite, fix the boundary bug, implement "history" plays and html_statement, and verify that the repertoire bonus works regardless of performance order.