import demo
import quantum
import automation_assistant_demo


def main():
    print("Running threat detection demo...")
    demo.main()
    print("Helper availability:", ", ".join(quantum.__all__))
    
    print("\n" + "=" * 70)
    print("Running automation assistant demo...")
    print("=" * 70 + "\n")
    automation_assistant_demo.main()


if __name__ == "__main__":
    main()
