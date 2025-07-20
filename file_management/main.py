# main.py
from file_system import FileSystem
from exceptions import FileSystemError

def run_cli():
    fs = FileSystem()

    print("\n--- In-Memory File System CLI ---")
    print("Commands:")
    print("  mkdir <path>")
    print("  touch <path> [content]")
    print("  ls <path>")
    print("  cat <path>")
    print("  rm <path>")
    print("  cp <source_path> <destination_path>")
    print("  mv <source_path> <destination_path>")
    print("  exit")
    print("\nExample: mkdir /users/john/docs")
    print("Example: touch /users/john/docs/report.txt 'This is my report.'")
    print("Example: ls /users/john")
    print("Example: cat /users/john/docs/report.txt")
    print("Example: cp /users/john/docs/report.txt /home/new_report.txt")

    while True:
        try:
            command_line = input("\n$ ").strip()
            if not command_line:
                continue

            parts = command_line.split(maxsplit=2) # maxsplit=2 for touch, cp, mv to get all content/path
            cmd = parts[0].lower()

            if cmd == "mkdir":
                if len(parts) == 2:
                    fs.mkdir(parts[1])
                else:
                    print("Usage: mkdir <path>")
            elif cmd == "touch":
                if len(parts) >= 2:
                    path = parts[1]
                    content = parts[2] if len(parts) == 3 else ""
                    fs.touch(path, content)
                else:
                    print("Usage: touch <path> [content]")
            elif cmd == "ls":
                if len(parts) == 2:
                    children = fs.ls(parts[1])
                    print(f"Contents of '{parts[1]}': {children}")
                else:
                    print("Usage: ls <path>")
            elif cmd == "cat":
                if len(parts) == 2:
                    content = fs.cat(parts[1])
                    print(f"Content of '{parts[1]}':\n---\n{content}\n---")
                else:
                    print("Usage: cat <path>")
            elif cmd == "rm":
                if len(parts) == 2:
                    fs.rm(parts[1])
                else:
                    print("Usage: rm <path>")
            elif cmd == "cp":
                if len(parts) == 3:
                    fs.cp(parts[1], parts[2])
                else:
                    print("Usage: cp <source_path> <destination_path>")
            elif cmd == "mv":
                if len(parts) == 3:
                    fs.mv(parts[1], parts[2])
                else:
                    print("Usage: mv <source_path> <destination_path>")
            elif cmd == "exit":
                print("Exiting file system. Goodbye!")
                break
            else:
                print("Unknown command.")

        except FileSystemError as e:
            print(f"Operation failed: {e}")
        except ValueError as e:
            print(f"Input error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            # import traceback
            # traceback.print_exc()

if __name__ == "__main__":
    run_cli()