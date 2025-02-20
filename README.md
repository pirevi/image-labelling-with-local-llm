# Image Labelling with Local LLM

Use opensource multimodal LLM -> [LLaVA](https://ollama.com/library/llava:13b) for describing/annotating image locally.
The code is parallelized to speed up the process massively according to the number of CPUs available.

## Setup and Run
1. Clone the Repo
```bash
git clone https://github.com/pirevi/image-labelling-with-local-llm.git
cd image-labelling-with-local-llm
```

2. Create virtual environment and install all dependencies
```bash
python -m venv .venv
# After activating the virtual environment do ->
pip install -r requirements.txt
```

3. Install Ollama app and make sure it is running in the background

4. Configure `src/utils/config.py` file according to your needs

5. Run `src/main.py`

