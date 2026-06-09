"""Clinical inbox autopilot.

Reusable core that ingests a physician's historical sent messages into a typed response graph
and retrieves voice + next-action to ground drafted inbox replies.

Synthetic-first: everything runs without live credentials. Live data is gated behind
``InboxConfig.source == "live"`` plus DrChrono OAuth credentials and token state.
"""
