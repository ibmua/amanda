# import os
# import subprocess
# import sys

# def create_progress_text(commands_with_statuses):
#     output = ""
#     for command, status in commands_with_statuses:
#         output += f"{status} {command}\n"
#     return output

# def update_progress(previous_text, new_text):
#     num_lines = previous_text.count("\n")
#     sys.stdout.write("\033[{}A".format(num_lines))
#     sys.stdout.write("\033[J")
#     print(new_text, end="")
#     sys.stdout.flush()

# def execute_commands_with_progress(commands):
#     commands_with_statuses = [(command, " ") for command in commands]
#     progress_text = create_progress_text(commands_with_statuses)
#     print(progress_text, end="")
#     sys.stdout.flush()

#     for i, command in enumerate(commands):
#         commands_with_statuses[i] = (command, "🏇")
#         progress_text = create_progress_text(commands_with_statuses)
#         update_progress(progress_text, progress_text)
#         subprocess.run(command, shell=True)
#         commands_with_statuses[i] = (command, "✅")
#         progress_text = create_progress_text(commands_with_statuses)
#         update_progress(progress_text, progress_text)

# def main():
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     os.chdir(script_dir)

#     nocode_flag = "--nocode" in sys.argv

#     commands = [
import os
import subprocess
import sys

def execute_commands_with_progress(commands):
    total_commands = len(commands)
    for i, command in enumerate(commands, start=1):
        print(f"({i}/{total_commands}) Executing: {command}")
        subprocess.run(command, shell=True)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    nocode_flag = "--nocode" in sys.argv

    commands = [
        "./launch-file-vetting-prompt-gens.sh" + (" nocode" if nocode_flag else ""),
        "python3 launch-file-vetting-ai-batch.py",
        "python3 combine_jsons.py --input outputs/response-of-the-file-filter",
        "python3 remove-0.py --json-selection \"outputs/response-of-the-file-filter_combined.json\" > outputs/response-of-the-file-filter_non-zero.json",
        "python3 parse-template.py --template templates/file-filter-refinement-phase.template --question outputs/question --hashtags outputs/response-of-the-file-filter_non-zero.json --output outputs/files-refined.prompt",
        "python3 AI-request.py --model sonnet --max-tokens 4096 --temperature 0.1 --system system-request-json --message-user outputs/files-refined.prompt --message-assistant response-start-json > outputs/response-of-the-file-refiner",
        "cat response-start-json > outputs/refined-file-priorities.json",
        "cat outputs/response-of-the-file-refiner >> outputs/refined-file-priorities.json",
        "python3 all-docs-joined.py --json-selection outputs/refined-file-priorities.json --json-all-hashtags \"hashtags/hashtags-sonnet.json\" > outputs/joined-selected-files",
        "python3 cli-gen.py",
        "cat outputs/joined-selected-files > outputs/all-available-resources",
        "cat outputs/cli-commands >> outputs/all-available-resources",
        "python3 parse-template.py --template templates/final.template --question outputs/question --hashtags outputs/all-available-resources --output outputs/asking-ai.prompt",
        "python3 doc-change-to-links.py --input \"outputs/asking-ai.prompt\" > outputs/asking-ai-http-docs.prompt",
        "python3 AI-request.py --model sonnet --max-tokens 4096 --temperature 0.1 --system system-request-final --message-user outputs/asking-ai-http-docs.prompt > outputs/ai-answer.md",
        "cat outputs/question > outputs/question-refined",
        "echo \"\nHere's an answer that isn't very good. Looks like it may be incomplete, or incorrect. Look:<poor_answer>\n\" >> outputs/question-refined",
        "cat outputs/ai-answer.md >> outputs/question-refined",
        "echo \"\n</poor_answer>\nPlease, answer the same following question, but better, including more sources that were lacking in this analysis:\" >> outputs/question-refined",
        "cat outputs/question >> outputs/question-refined",
        "python3 display-markdown.py --input outputs/ai-answer.md"
    ]

    execute_commands_with_progress(commands)

if __name__ == "__main__":
    main()