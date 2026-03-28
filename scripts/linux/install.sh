#!/bin/bash

# ----------------------------
# Helpers
# ----------------------------

PAGER_CMD=""
if command -v less >/dev/null 2>&1; then
    PAGER_CMD="less"
elif command -v more >/dev/null 2>&1; then
    PAGER_CMD="more"
fi

prompt_choice() {
    # Usage: prompt_choice "Question" "valid_chars"  (returns chosen char in $REPLY)
    local question="$1"
    local valid="$2"
    while true; do
        echo
        read -r -p "$question " REPLY
        REPLY="$(echo "$REPLY" | tr '[:upper:]' '[:lower:]')"
        if [[ "$valid" == *"$REPLY"* ]]; then
            return 0
        fi
        echo "Invalid choice. Please enter one of: $valid"
    done
}

show_file() {
    local file_path="$1"
    if [ ! -f "$file_path" ]; then
        echo "File not found: $file_path"
        return 1
    fi

    if [ -n "$PAGER_CMD" ]; then
        $PAGER_CMD "$file_path"
    else
        # Fallback: print to stdout
        cat "$file_path"
    fi
}

# ----------------------------
# 1) GPLv3+ license prompt
# ----------------------------

LICENSE_FILE="LICENSE"

echo "------------------------------------------------------------"
echo "FcsIT installer"
echo "------------------------------------------------------------"
echo

if [ ! -f "$LICENSE_FILE" ]; then
    echo "ERROR: LICENSE file not found in the current directory."
    echo "Expected: $PWD/$LICENSE_FILE"
    exit 1
fi

echo "This installer will set up FcsIT and its dependencies."
echo "FcsIT is licensed under the GNU GPL v3 or later."
echo

while true; do
    echo "Choose an option:"
    echo "  [a] Continue installation"
    echo "  [s] Show GPL license text"
    echo "  [d] Abort the installation"
    echo "Choosing 'Abort' will only terminate the installer."
    echo "The source code remains available to you under the terms of the GNU GPL v3 or later."
    prompt_choice "Your choice [a/s/d]:" "asd"

    if [ "$REPLY" = "a" ]; then
        echo "Continuing installation."
        break
    elif [ "$REPLY" = "s" ]; then
        echo "Displaying LICENSE..."
        show_file "$LICENSE_FILE"
        # After showing, loop again to accept/deny
    elif [ "$REPLY" = "d" ]; then
        echo "Installation aborted."
        exit 1
    fi
done

# ----------------------------
# 2) Prompt for readPTU_FLIM.py download (MIT)
# ----------------------------

# If user declines, PTU_Corr module is removed before pip install . so it won't be installed.
PTU_CORR_DIR="src/Methods/PTU_Corr"
THIRD_PARTY_DIR="src/Methods/PTU_Corr/include/Third_party"

echo
# echo "------------------------------------------------------------"
# echo "Optional component: PTU_Corr / readPTU_FLIM.py"
# echo "------------------------------------------------------------"
echo
echo "The PTU_Corr module requires a third-party component:"
echo "  - readPTU_FLIM.py (MIT License), downloaded from an external repository during installation."
echo
echo "If you accept, the installer will download readPTU_FLIM.py and store it together with"
echo "the MIT license text in:"
echo "  $THIRD_PARTY_DIR"
echo
echo "If you deny, the PTU_Corr module directory will be removed and PTU_Corr functionality will NOT be installed."
echo


# Default: do NOT download third-party component unless user explicitly agrees
export FCSIT_DOWNLOAD_READPTU_FLIM="0"

prompt_choice "Download and install readPTU_FLIM.py now? [y/n]:" "yn"
if [ "$REPLY" = "y" ]; then
    export FCSIT_DOWNLOAD_READPTU_FLIM="1"
    echo "Accepted. readPTU_FLIM.py will be downloaded during installation."
else
    export FCSIT_DOWNLOAD_READPTU_FLIM="0"
    echo "Denied. Proceeding with partial installation (without PTU_Corr)."
    if [ -d "$PTU_CORR_DIR" ]; then
        echo "Removing module directory: $PTU_CORR_DIR"
        rm -rf "$PTU_CORR_DIR" || exit 1
    fi
fi






# ----------------------------
# 3) DejaVu fonts notice
# ----------------------------

echo
echo "------------------------------------------------------------"
echo "Third-party asset notice: DejaVu fonts"
echo "------------------------------------------------------------"
echo
echo "This software uses the DejaVu Sans Condensed font (DejaVu Fonts Project)."
echo "License information is embedded in the font file metadata (TTF)."
echo
prompt_choice "Press [c] to continue installation:" "c"
echo "Continuing..."

# ----------------------------
# Existing installation logic (original script)
# ----------------------------

# Define the name of the virtual environment directory
VENV_DIR="v_FcsIT_env"

# Ensure Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install Python 3.10 or higher and re-run this script."
    exit 1
fi

PY_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:3])))")

if ! python3 - <<EOF
import sys
if not ( (3,10) <= sys.version_info[:2] <= (3,12) ):
    sys.exit(1)
EOF
then
    echo "Unsupported Python version: $PY_VERSION"
    echo "Please install Python between 3.10 and 3.12."
    exit 1
fi

# Check if pip is available or create a virtual environment first
echo "Checking for pip..."
if ! python3 -m pip --version &> /dev/null; then
    echo "Pip is not available. Creating a virtual environment to bootstrap pip."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "Failed to create a virtual environment. Exiting."
        exit 1
    fi
    source "$VENV_DIR/bin/activate"
    python -m ensurepip --upgrade
    if [ $? -ne 0 ]; then
        echo "Failed to bootstrap pip in the virtual environment. Exiting."
        deactivate
        exit 1
    fi
else
    echo "Pip is available. Proceeding."
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "Failed to create a virtual environment. Exiting."
        exit 1
    fi
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"
if [ $? -ne 0 ]; then
    echo "Failed to activate the virtual environment. Exiting."
    exit 1
fi

# Upgrade pip in the virtual environment
echo "Upgrading pip in the virtual environment..."
python -m pip install --upgrade pip

# Install the package and dependencies using pip
echo "Installing dependencies using pip..."
python -m pip install .
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies. Exiting."
    deactivate
    exit 1
fi

# Ensure the icon directory exists and copy the icon
ICON_SRC="$PWD/src/res/icons/FcsIT.png"
ICON_DEST="$HOME/.local/share/icons/FcsIT.png"
echo "Preparing icon directory at $HOME/.local/share/icons/"
mkdir -p "$(dirname "$ICON_DEST")"
cp "$ICON_SRC" "$ICON_DEST"
if [ $? -ne 0 ]; then
    echo "Failed to copy icon to $ICON_DEST. Exiting."
    deactivate
    exit 1
fi

# Update the icon cache
echo "Updating icon cache..."
gtk-update-icon-cache "$HOME/.local/share/icons"

# Create run_app.sh script
echo "Creating run_FcsIT script..."
cat <<EOL > run_FcsIT
#!/bin/bash
# Activate the virtual environment and run the main script

source "$PWD/$VENV_DIR/bin/activate"
cd FcsIT
python "$PWD/FcsIT/FcsIT.py" #--timing  ## uncomment the argument to analyse functions' timing
deactivate
EOL

# Make run_FcsIT executable
chmod +x run_FcsIT
if [ $? -ne 0 ]; then
    echo "Failed to make run_FcsIT executable. Exiting."
    deactivate
    exit 1
fi
echo "run_FcsIT script created and made executable."

# Create a .desktop entry in KDE/GNOME menu
DESKTOP_ENTRY_DIR="$HOME/.local/share/applications"
DESKTOP_ENTRY="$DESKTOP_ENTRY_DIR/FcsIT.desktop"

# Ensure the directory exists
mkdir -p "$DESKTOP_ENTRY_DIR"

# Generate the .desktop file
cat <<EOL > "$DESKTOP_ENTRY"
[Desktop Entry]
Version=0.6
Type=Application
Name=FcsIT
Comment=Run FcsIT application
Exec=$PWD/run_FcsIT
Path=$PWD/FcsIT/
Icon=$HOME/.local/share/icons/FcsIT.png
Terminal=false
Categories=Utility;Application;
EOL

if [ $? -ne 0 ]; then
    echo "Failed to create desktop entry. Exiting."
    deactivate
    exit 1
fi
echo "Desktop entry created at $DESKTOP_ENTRY"

# Deactivate the virtual environment
echo "Deactivating virtual environment..."
deactivate

echo "Renaming src directory to FcsIT..."
mv src FcsIT
if [ $? -ne 0 ]; then
    echo "Failed to rename src directory to FcsIT. Exiting."
    exit 1
fi

# Step 2: Move all files in the main directory (except install.sh and setup.py) to the FcsIT directory
echo "Moving files to FcsIT directory..."
for file in *; do
    if [[ "$file" != "install.sh" && "$file" != "setup.py" && "$file" != "run_FcsIT" && "$file" != "FcsIT" && "$file" != "v_FcsIT_env" && "$file" != "python_embedded" ]]; then
        mv "$file" FcsIT/
        if [ $? -ne 0 ]; then
            echo "Failed to move file $file to FcsIT directory. Exiting."
            exit 1
        fi
    fi
done

# Step 3: Remove setup.py and install.sh
echo "Removing setup.py and install.sh..."
rm -f -R setup.py install.sh
if [ $? -ne 0 ]; then
    echo "Failed to remove setup.py or install.sh. Exiting."
    exit 1
fi

# Confirm completion
echo "All files successfully organized and cleaned up."
echo "Installation and reorganization completed successfully!"
