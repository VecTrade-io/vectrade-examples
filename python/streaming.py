"""VecTrade Python SDK — Streaming AI Analysis Example."""

from vectrade import VecTrade


def main():
    vt = VecTrade()

    print("=== Streaming AI Analysis ===\n")

    # Stream a detailed analysis
    print("Prompt: Analyze NVDA before Q4 earnings\n")
    print("-" * 50)

    for chunk in vt.ai.stream("Analyze NVDA before Q4 earnings. Cover: revenue growth, AI segment, valuation, risks."):
        print(chunk.text, end="", flush=True)

    print("\n" + "-" * 50)
    print("\nDone!")


if __name__ == "__main__":
    main()
