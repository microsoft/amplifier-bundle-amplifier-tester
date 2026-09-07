"""SCRATCH ONLY -- a deliberate failure, to prove the test job can go red.

This file exists on the throwaway branch ci/red-proof-j1e6 and nowhere else.
It is never merged: the branch is closed and deleted once the RED run is
observed. Its whole purpose is to make the TEST job fail for a TEST reason,
so the job log reads "1 failed, 18 passed" rather than a setup or lint error
-- a red that came from a broken runner proves nothing about the gate.
"""

from __future__ import annotations


def test_deliberate_failure_to_prove_the_gate_bites() -> None:
    assert 1 == 2, "deliberate scratch failure: proving the test job can go red"
