 -📦 K3U Installer v2 Beta – 
Flexible ComfyUI Installation
K3U Installer is a desktop GUI tool designed to simplify and automate the installation of ComfyUI with flexible setups.

This is a configurable and scriptable installer that reads .k3u files to create full environments, clone repos, install PyTorch, CUDA, Triton, SageAttention, and more.
Perfect for both first-time users and advanced developers who want version control and automation.

🖼️ What’s New in v2 Beta?
Complete GUI redesign (Tkinter-based)

Full automation for:

Virtual environments (external_venv)

Updates for embedded Python installs (embedded)

Rich preview and logging system with real-time feedback

Summary step with version choices (e.g. Triton Stable/Nightly, Sage v1/v2)

Auto-creation of launch/update scripts (.bat)

Prepackaged .k3u configurations for various Python/CUDA/PyTorch versions

⚙️ Features
🔧 Flexible JSON-based configs (.k3u)
Define installation logic step-by-step. Includes variables, setup types, conditionals, and user choices.

🖥️ GUI-based installer (no terminal needed)
Just double-click to run the GUI. Works with both:

K3U_GUI.bat: Uses system Python

K3U_emebeded_GUI.bat: Uses embedded Python (included separately)

📜 Setup scripts generator
Automatically generates .bat files to run or update ComfyUI with custom options.

🧠 Advanced components supported

Triton: choose between Stable/Nightly

SageAttention: v1 (pip) or v2 (from source, requires PyTorch >=2.7)

OnnxRuntime, Diffusers, Transformers, Accelerate, Ninja, etc.

📦 Included Configs (.k3u files):

k3u_Comfyui_venv_StableNightly.k3u

Full setups for Python 3.12, CUDA 12.4/12.6, PyTorch Stable/Nightly with choice of Triton/Sage.

k3u_Comfyui_venv_allPyton.k3u

Covers Python 3.10, 3.11, 3.12, 3.13 — various compatible toolchains.

k3u_Comfyui_Embedded.k3u

Designed to update ComfyUI installs that run with embedded Python.

▶️ How to Use
Download or clone this repository

Choose how to launch:

K3U_GUI.bat (uses your Python from PATH)

K3U_emebeded_GUI.bat (if you use embedded Python)

Run the GUI and:

Select base installation folder

Select Python.exe (if required)

Choose a .k3u configuration

Choose the desired setup (e.g., Stable/Nightly + Triton/Sage options)

Click "Summary and Start" to preview all actions

Confirm and watch the logs and progress bar

🔍 Screenshots

![1](https://github.com/user-attachments/assets/ce2ce699-f44e-44a7-a3f5-40f3b6f6c469)

![2](https://github.com/user-attachments/assets/05391d97-b84f-4fc6-bd5e-0a43d62c6886)

![k3u](https://github.com/user-attachments/assets/d819a357-0430-4ef9-adfb-3945fb6d1653)

![k3u3](https://github.com/user-attachments/assets/dc045c3b-f84e-47fa-bfb3-88f90dd54bdc)

</details>
📜 License
Licensed under the Apache License 2.0.
You are free to use, distribute, and modify this tool in personal and commercial projects.

See LICENSE for full details.

💬 Feedback / Issues
Found a bug? Have a suggestion?
Please open an issue or contribute via pull requests.

