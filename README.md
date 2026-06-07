# Predator thermal vision gui generator for videos
Basic repo for generate Predator thermal vision gui in your videos

## Usage

Put your wished video as "input.mp4" and execute with `python predator.py` to generate "thermal_predator.mp4" video.
---

## 🚀 Installation & Usage
### **1️⃣ Install Dependencies**
Make sure you have Python 3 installed, then install required packages:

```bash
sudo apt install -yqq python3-tk python3.10-venv

python3.10 -m venv test
source test/bin/activate
pip install -r requirements.txt
```
**Note**: Only tested in Ubuntu/Debian distros.


### **2️⃣ Run the Program**
`python predator.py`

### **3️⃣ Deactivate Virtual Environment when finished**
`
deactivate
`

### Wintel usage
```powershell
python.exe -m venv wintel

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

.\wintel\Scripts\Activate.ps1

winget install Gyan.FFmpeg

pip install -r requirements.txt

python predator.py
```