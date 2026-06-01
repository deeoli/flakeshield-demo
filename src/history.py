"""Track failure history and recurring issues."""

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class FailureRecord:
    """Historical record of a failure signature."""

    signature: str
    first_seen: str
    last_seen: str
    occurrence_count: int
    is_recurring: bool = False

    def update(self) -> None:
        """Update record with new occurrence."""
        self.last_seen = datetime.utcnow().isoformat()
        self.occurrence_count += 1
        self.is_recurring = self.occurrence_count > 1


class FailureHistory:
    """Manage failure signature history."""

    def __init__(self, history_file: str = "data/failure-history.json"):
        """Initialize history tracker.

        Args:
            history_file: Path to JSON history file
        """
        self.history_file = history_file
        self.records: Dict[str, FailureRecord] = {}
        self.load()

    def load(self) -> None:
        """Load history from JSON file."""
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                data = json.load(f)
                for sig, record_data in data.items():
                    self.records[sig] = FailureRecord(**record_data)

    def save(self) -> None:
        """Save history to JSON file."""
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        data = {sig: asdict(rec) for sig, rec in self.records.items()}
        with open(self.history_file, "w") as f:
            json.dump(data, f, indent=2)

    def record_failure(self, signature: str) -> FailureRecord:
        """Record or update a failure signature.

        Args:
            signature: Normalized failure signature

        Returns:
            FailureRecord (existing or new)
        """
        now = datetime.utcnow().isoformat()

        if signature in self.records:
            # Update existing record
            record = self.records[signature]
            record.update()
        else:
            # Create new record
            record = FailureRecord(
                signature=signature,
                first_seen=now,
                last_seen=now,
                occurrence_count=1,
                is_recurring=False,
            )
            self.records[signature] = record

        self.save()
        return record

    def get_record(self, signature: str) -> Optional[FailureRecord]:
        """Get history for a signature.

        Args:
            signature: Normalized failure signature

        Returns:
            FailureRecord or None if not found
        """
        return self.records.get(signature)

    def seen_before(self, signature: str) -> bool:
        """Return True if signature existed in history before the current run."""
        return signature in self.records

    def occurrences_for_report(self, signature: str) -> int:
        """Occurrence count including the current run (call before record_failure)."""
        record = self.get_record(signature)
        if record is None:
            return 1
        return record.occurrence_count + 1

    def get_summary(self, current_signatures: List[str]) -> Dict:
        """Summarize new vs recurring failures using pre-run history.

        Args:
            current_signatures: List of signatures in current run

        Returns:
            Dict with new_count, recurring_count, details
        """
        new_sigs = []
        recurring_sigs = []

        for sig in current_signatures:
            if self.seen_before(sig):
                recurring_sigs.append(sig)
            else:
                new_sigs.append(sig)

        return {
            "new_root_causes": len(new_sigs),
            "recurring_root_causes": len(recurring_sigs),
            "new_signatures": new_sigs,
            "recurring_signatures": recurring_sigs,
        }


if __name__ == "__main__":
    # Demo: history tracking
    history = FailureHistory()

    # Record some failures
    sigs = [
        "NullPointerException in payment validation",
        "Request timeout after Xms",
    ]

    print("Recording failures...")
    for sig in sigs:
        rec = history.record_failure(sig)
        print(f"  {rec.signature}: count={rec.occurrence_count}")

    print(f"\nHistory saved to: {history.history_file}")

    # Show history
    print("\nHistory contents:")
    for sig, rec in history.records.items():
        print(f"  {sig}")
        print(f"    First: {rec.first_seen}")
        print(f"    Last: {rec.last_seen}")
        print(f"    Count: {rec.occurrence_count}")
        print(f"    Recurring: {rec.is_recurring}")
