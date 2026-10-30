# Steering — Pay once, never twice
Money rule for both apps: one payment per certified week (App 1) / one fee per permit (App 2).
A duplicate payment is a failed build, not a warning. Every money path needs a test that tries to pay twice and proves it is blocked.
Exempt means $0: no payment object is created at all (App 2 employee permits).
