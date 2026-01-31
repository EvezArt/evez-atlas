"""Main entry point for running the quantum codex agent setup."""

import demo
import quantum


def main():
    """Run the demo and display available quantum helpers."""
    print("Running demo...")
    demo.main()
    print("Helper availability:", ", ".join(quantum.__all__))


if __name__ == "__main__":
    main()
