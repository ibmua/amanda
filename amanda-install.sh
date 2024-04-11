#!/bin/bash



# Get the current folder path
current_folder=$(pwd)

# Detect the current platform and shell
platform=$(uname)
shell=$(basename "$SHELL")

# Function to set the AMANDA_FOLDER variable and append it to the configuration file
set_amanda_folder() {
    local config_file="$1"
    local export_command="export AMANDA_FOLDER=\"$current_folder\""

    # Set the AMANDA_FOLDER variable in the current session
    export AMANDA_FOLDER="$current_folder"

    # Append the export command to the configuration file if it doesn't exist already
    grep -qF "$export_command" "$config_file" || echo "$export_command" >> "$config_file"

    echo "AMANDA_FOLDER variable set to $current_folder and appended to $config_file"
}

# Set the AMANDA_FOLDER variable based on the platform and shell
if [ "$platform" == "Darwin" ]; then
    # macOS
    set_amanda_folder "$HOME/.bash_profile"
elif [ "$platform" == "Linux" ]; then
    # Linux
    set_amanda_folder "$HOME/.bashrc"
elif [[ "$platform" == CYGWIN* || "$platform" == MINGW* ]]; then
    if [ "$shell" == "bash" ]; then
        # Windows (Git Bash)
        set_amanda_folder "$HOME/.bashrc"
    elif [ "$shell" == "pwsh" ] || [ "$shell" == "powershell" ]; then
        # Windows (PowerShell)
        powershell -Command "\$env:AMANDA_FOLDER = '$current_folder'"
        echo "\$env:AMANDA_FOLDER = '$current_folder'" >> "$HOME/Documents/PowerShell/Microsoft.PowerShell_profile.ps1"
        echo "AMANDA_FOLDER variable set to $current_folder and appended to PowerShell profile"
    elif [ "$shell" == "cmd.exe" ]; then
        # Windows (Command Prompt)
        setx AMANDA_FOLDER "$current_folder"
        set AMANDA_FOLDER=$current_folder
        echo "AMANDA_FOLDER variable set to $current_folder as a system environment variable"
    else
        echo "Unsupported shell: $shell"
        exit 1
    fi
else
    echo "Unsupported platform: $platform"
    exit 1
fi




pip3 install -U anthropic[vertex] termcolor rich

# Get the current folder path
CURRENT_FOLDER=$(pwd)

# Set the destination folder for the executable
DESTINATION_FOLDER="/usr/local/bin"

# Create the amanda executable file
cat > "$DESTINATION_FOLDER/amanda" << EOL
#!/bin/bash

# Set the AMANDA_FOLDER path
export AMANDA_API="$AMANDA_API"
export AMANDA_FOLDER="$CURRENT_FOLDER"
export CLAUDE_API_KEY="$CLAUDE_API_KEY"
export GOOGLE_PROJECT_ID="$GOOGLE_PROJECT_ID"

# Change directory to the AMANDA_FOLDER
cd "\$AMANDA_FOLDER"

# Check if no arguments are provided
if [ \$# -eq 0 ]; then
    # Display help information
    echo "Usage: amanda [--code] <text>"
    echo "  --code    Optional parameter to include code knowledge base"
    echo "  <text>    Question"
    echo ""
    echo "Examples:"
    echo "  amanda Blah blah blah question text"
    echo "  amanda --code Blah blah blah question text"
    exit 0
fi

# Check if the --code parameter is provided
if [ "\$1" == "--code" ]; then
    rm "$AMANDA_FOLDER/outputs/"*
    # Shift the arguments to remove --nocode
    shift
    # Join the arguments with spaces
    TEXT="\$*"
    # Write the text to the outputs/question file
    echo "\$TEXT" > outputs/question
    # Execute the full-cycle.py script
    python3 full-cycle.py
else
    rm "$AMANDA_FOLDER/outputs/"*
    # Join the remaining arguments with spaces
    TEXT="\$*"
    # Write the text to the outputs/question file
    echo "\$TEXT" > outputs/question
    # Execute the full-cycle.py script with --nocode
    python3 full-cycle.py --nocode
    cat outputs/question-refined > outputs/question
    echo "We will now try to refine the improve it"
    cp outputs/ai-answer.md outputs/ai-answer-FIRST.md
    sleep 10
    echo "Trying to improve the answer"
    python3 full-cycle.py --nocode
fi
EOL

# Make the amanda executable file executable
chmod +x "$DESTINATION_FOLDER/amanda"

echo "Installation complete. The 'amanda' command is now available."


# ./export-amanda-var.sh # setting persistent environment variable AMANDA_FOLDER to link to Amanda folder
# source ./export-amanda-var.sh
