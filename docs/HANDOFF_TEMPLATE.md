# Hand-off message

Post in the team channel when a deliverable has passed its acceptance tests.

    HANDOFF | from: <name> | to: <names> | file: <path> | version: <v0, v1, ...>
    rows/size: <n> | check: <one command that proves it works> | known limits: <one line>
    sample (20 rows): <paste or link>

Receiver replies within 15 minutes:

    GOT IT   or   MISSING: <what, exactly>

Then the sender adds one line to data/MANIFEST.md. If a hand-off is late, the receiver keeps working
against the fixture or stub and the sender says when it will land.
