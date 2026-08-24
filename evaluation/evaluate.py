"""Run the deterministic rules evaluation against versioned fixtures."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.rules import decide  # noqa: E402
from app.schemas import RallyObservation  # noqa: E402


def main() -> int:
    fixture_path = Path(__file__).with_name("cases.jsonl")
    cases = [
        json.loads(line)
        for line in fixture_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    correct = 0
    safety_true_positive = 0
    safety_total = 0
    observed_classes: set[str] = set()

    for case in cases:
        predicted = decide(RallyObservation(**case["observation"])).decision.value
        expected = case["expected"]
        observed_classes.add(expected)
        correct += int(predicted == expected)
        if case["safety_critical"]:
            safety_total += 1
            safety_true_positive += int(predicted == expected)

    accuracy = correct / len(cases)
    safety_recall = safety_true_positive / safety_total if safety_total else 0.0

    print(f"fixture_count={len(cases)}")
    print(f"class_coverage={len(observed_classes)}")
    print(f"rules_accuracy={accuracy:.3f}")
    print(f"safety_critical_recall={safety_recall:.3f}")
    print("scope=synthetic_rules_fixtures_not_real_match_performance")

    return 0 if accuracy == 1.0 and safety_recall == 1.0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
