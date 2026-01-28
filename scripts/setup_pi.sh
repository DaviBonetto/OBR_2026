#!/bin/bash

# OBR 2026 - Raspberry Pi Setup Script
# Installs system dependencies, Coral TPU drivers, and Python environment.

set -e  # Exit immediately if a command exits with a non-zero status.

GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}[1/5] Updating System...${NC}"
sudo apt-get update && sudo apt-get upgrade -y

echo -e "${GREEN}[2/5] Installing System Dependencies (OpenCV, Tkinter)...${NC}"
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-tk \
    libgl1 \
    libglib2.0-0 \
    libatlas-base-dev \
    libopenjp2-7 \
    libtiff5 \
    libgtk-3-0 \
    libopenblas-dev \
    liblapack-dev \
    libjpeg-dev

echo -e "${GREEN}[3/5] Installing Google Coral EdgeTPU Drivers...${NC}"
if ! dpkg -l | grep -q libedgetpu1-std; then
    echo "Adding Coral package repository..."
    echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
    sudo apt-get update
    sudo apt-get install -y libedgetpu1-std python3-pycoral
else
    echo "Coral drivers already installed."
fi

echo -e "${GREEN}[3.5/5] Configuring User Permissions (Serial/Video)...${NC}"
sudo usermod -a -G dialout $USER
sudo usermod -a -G video $USER
sudo usermod -a -G gpio $USER 2>/dev/null || true
echo "Permissions added. A reboot (or logout/login) is required for these to take effect."

# Optional: Install the 'max' frequency driver (uncomment if needed for extra performance, beware of heat)
# sudo apt-get install -y libedgetpu1-max

echo -e "${GREEN}[4/5] Setting up Python Environment...${NC}"
# It is recommended to use a virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing requirements from requirements.txt..."
# Note: On Pi, some packages like numpy might need specific versions or system packages.
# We attempt standard install first.
pip install -r requirements.txt

fi

echo -e "${GREEN}[4.5/5] Ensuring Config Exists...${NC}"
CONFIG_PATH="src/Python/main/config.ini"
if [ ! -f "$CONFIG_PATH" ]; then
    echo "Creating default config.ini at $CONFIG_PATH..."
    # Create a basic config structure to prevent crash
    cat <<EOF > "$CONFIG_PATH"
[DEFAULT]
debug = False
speed_limit = 100
rotation_correction = 0
EOF
fi

echo -e "${GREEN}[5/5] Setup Complete!${NC}"
echo "To start the robot, activate the environment and run main.py:"
echo "source venv/bin/activate"
echo "cd src/Python/main"
echo "python3 main.py"
