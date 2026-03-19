from src.triage import run_triage


tests = (
    "What are the general principles questions?",
    "What are the Segregation of Activities Policy questions?",
    "What are the Information Security and Confidentiality Policy questions?",
    "What are the Personal Investments Policy questions?",
    "What are the Order Allotment Policy questions?",
    "What are the Compliance, Risk Management, and Internal Controls Policy questions?",
    "What are the Anti-Money Laundering Policy questions?",
    "What are the Training questions?",
)


def main() -> None:
    for question in tests:
        result = run_triage(question)
        print("-" * 80)
        print(question)
        print(result["screening"])
        print(result["response"])


if __name__ == "__main__":
    main()

