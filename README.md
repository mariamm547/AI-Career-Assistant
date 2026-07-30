[README.md](https://github.com/user-attachments/files/30548599/README.md)
# 🚀 [Tips Hindawi](https://www.tipshindawi.com/) Challenge (June–July) 2026

> 🏆 This repository is my official submission for the \[ \*\*Tips Hindawi\*\* ](https://www.tipshindawi.com/) \*\*Challenge (June–July) 2026\*\*.

## 👤 Participant

|Field|Value|
|-|-|
|Full Name|Mariam Tamer Shafiek|
|Project Name|AI Career Assistant|# 🚀 [Tips Hindawi](https://www.tipshindawi.com/) Challenge (June–July) 2026

> 🏆 This repository is my official submission for the \[ \*\*Tips Hindawi\*\* ](https://www.tipshindawi.com/) \*\*Challenge (June–July) 2026\*\*.

## 👤 Participant

|Field|Value|
|-|-|
|Full Name|Mariam Tamer Shafiek|
|Project Name|AI Career Assistant|
|GitHub Username|mariamm547|
|Challenge Batch|June–July 2026|
|Training Program|Large Language Models (LLMs) Program|
|Organization|[**Edrak for Ai**](https://edrak4ai.com/en)|

\---

# 📖 Project Overview



**AI Career Assistant** is a production‑ready web application that helps job seekers analyze their resumes, discover suitable career paths, and identify skill gaps – all powered by state‑of‑the‑art Large Language Models.



The system uses "Mistral‑Nemo‑Instruct‑2407" to extract structured information from PDF resumes, then matches the extracted skills against a large dataset of real‑world job postings. It recommends the top 10 most relevant jobs, provides a match percentage, lists matched and missing skills, and even suggests a learning roadmap to bridge the gaps.



The application is split into two parts:

\- Backend: Runs on a GPU‑accelerated Kaggle notebook, exposing a Flask API via "NGROK".

\- Frontend: A modern "Streamlit" dashboard that runs locally on a CPU‑only machine, communicating with the backend through the public NGROK URL.



This architecture enables anyone (even without a powerful GPU) to leverage the power of large language models for career guidance.

\---

# ✨ Features



* Resume Upload: Drag‑and‑drop PDF upload with instant validation.
* Skills Extraction: Automatically extracts technical and professional skills using Mistral AI Model.
* Job Recommendations: Ranks 500+ job titles based on skill overlap, showing:Match percentage (with a progress bar), Matched skills (green), Missing skills (red), Companies hiring for that role, and job posting frequency.
* Missing Skills Analysis: Groups skills by category (Programming, Cloud, Data, ML, Soft Skills) and assigns priority (High/Medium/Low) so you know what to learn first.
* Dashboard Metrics: Displays total skills found, number of recommended jobs, and average match score.
* Modern UI: SaaS‑style design with custom CSS, responsive layout, hover animations, and colourful badges.

\---

# 🛠️ Technologies Used



Frontend: Streamlit, Python, HTML/CSS



Backend: Flask, Hugging Face Transformers, PyTorch, LangChain, PyPDF2



LLM: Mistral-Nemo-Instruct-2407 (7B)



Infrastructure: Kaggle (GPU), NGROK, FAISS 



Data: KaggleHub, Pandas, job market datasets (4 sources)



\---

# ⚙️ Installation



Before installation you must have: Python 3.9+, a Kaggle account (for GPU), and an ngrok authtoken.



Then Install the files from the repo: app.py , backend.py , requirements.txt and Project\_notebook.ipynb.



1\. Set up the Kaggle Backend (GPU):



\- Create a new Kaggle notebook with GPU accelerator (GPU T4) enabled.

\- In the notebook, add your ngrok authtoken and Hugging Face token.

\- Run all cells. The notebook will download the model (≈7 GB), start the Flask server, and print a public ngrok URL (e.g., `https://xxxx.ngrok.io`).

\- Copy that URL – you’ll need it for the frontend.



2\. Set up the Local Streamlit Frontend:



\- Install dependencies by running this in the command prompt: pip install -r requirements.txt

\- Open app.py and set the API\_BASE\_URL variable to the ngrok URL from Kaggle: API\_BASE\_URL = "https://xxxx.ngrok.io"

\- Run the Streamlit app: streamlit run app.py

\- Access the dashboard at http://localhost:8501 in your browser.



\---

# 🚀 Usage



1. Upload your resume (PDF format) using the file uploader.



2\. Click the Analyze Resume button – a progress bar and spinner will appear while the backend processes your file.



3\. Once complete, you'll see three metric cards at the top.



4\. Use the sidebar navigation to switch between:



&#x20;  - Resume Skills Analysis – view extracted skills as badges, plus a raw text expander.



&#x20;  - Job Recommendation – browse the top 10 jobs with detailed cards.



&#x20;  - Missing Skills – explore skill gaps grouped by category and priority.



5\. Export or share your results – all data is stored in the session state for the current session.



\---

# 📸 Demo

Add screenshots, GIFs, or a demo video.

\---

# 📈 Results



The system has been tested with various resume samples and consistently delivers:

&#x20;- Average skill extraction accuracy.

&#x20;- Job recommendation relevance.

&#x20;- Good response time.

\---

# 🔮 Future Improvements



* Real‑time job scraping: integrate with live job boards (LinkedIn, Indeed) to provide up‑to‑date openings.
* User accounts: allow users to save analysis history and track progress over time.
* Deploy the frontend: host the Streamlit app on Streamlit Cloud or a VM for always‑on availability.
* Fine‑tune the model: fine‑tune Mistral on a curated dataset of resume‑job pairs for even better extraction.

\---

# 📚 About the Challenge

This project was developed as part of the [**Tips Hindawi**](https://www.tipshindawi.com/) **Challenge (June–July) 2026**.

[Tips Hindawi](https://www.tipshindawi.com/) is the internships department of [**Edrak for Ai**](https://edrak4ai.com/en), and the challenge encourages participants to build real-world projects, apply practical skills, and showcase their work through GitHub.

For more information about the challenge, training programs, and upcoming batches, visit the official [Tips Hindawi](https://www.tipshindawi.com/) website.

\---

# 📄 License

This project is shared for educational and portfolio purposes.


|GitHub Username|mariamm547|
|Challenge Batch|June–July 2026|
|Training Program|Large Language Models (LLMs) Program|
|Organization|[**Edrak for Ai**](https://edrak4ai.com/en)|

\---

# 📖 Project Overview



**AI Career Assistant** is a production‑ready web application that helps job seekers analyze their resumes, discover suitable career paths, and identify skill gaps – all powered by state‑of‑the‑art Large Language Models.



The system uses "Mistral‑Nemo‑Instruct‑2407" to extract structured information from PDF resumes, then matches the extracted skills against a large dataset of real‑world job postings. It recommends the top 10 most relevant jobs, provides a match percentage, lists matched and missing skills, and even suggests a learning roadmap to bridge the gaps.



The application is split into two parts:

\- Backend: Runs on a GPU‑accelerated Kaggle notebook, exposing a Flask API via "NGROK".

\- Frontend: A modern "Streamlit" dashboard that runs locally on a CPU‑only machine, communicating with the backend through the public NGROK URL.



This architecture enables anyone (even without a powerful GPU) to leverage the power of large language models for career guidance.

\---

# ✨ Features



* Resume Upload: Drag‑and‑drop PDF upload with instant validation.
* Skills Extraction: Automatically extracts technical and professional skills using Mistral AI Model.
* Job Recommendations: Ranks 500+ job titles based on skill overlap, showing:Match percentage (with a progress bar), Matched skills (green), Missing skills (red), Companies hiring for that role, and job posting frequency.
* Missing Skills Analysis: Groups skills by category (Programming, Cloud, Data, ML, Soft Skills) and assigns priority (High/Medium/Low) so you know what to learn first.
* Dashboard Metrics: Displays total skills found, number of recommended jobs, and average match score.
* Modern UI: SaaS‑style design with custom CSS, responsive layout, hover animations, and colourful badges.
[README.md](https://github.com/user-attachments/files/30548560/README.md)

\---

# 🛠️ Technologies Used



Frontend: Streamlit, Python, HTML/CSS



Backend: Flask, Hugging Face Transformers, PyTorch, LangChain, PyPDF2



LLM: Mistral-Nemo-Instruct-2407 (7B)



Infrastructure: Kaggle (GPU), NGROK, FAISS 



Data: KaggleHub, Pandas, job market datasets (4 sources)



\---

# ⚙️ Installation



Before installation you must have: Python 3.9+, a Kaggle account (for GPU), and an ngrok authtoken.



Then Install the files from the repo: app.py , backend.py , requirements.txt and Project\_notebook.ipynb.



1\. Set up the Kaggle Backend (GPU):



\- Create a new Kaggle notebook with GPU accelerator (GPU T4) enabled.

\- In the notebook, add your ngrok authtoken and Hugging Face token.

\- Run all cells. The notebook will download the model (≈7 GB), start the Flask server, and print a public ngrok URL (e.g., `https://xxxx.ngrok.io`).

\- Copy that URL – you’ll need it for the frontend.



2\. Set up the Local Streamlit Frontend:



\- Install dependencies by running this in the command prompt: pip install -r requirements.txt

\- Open app.py and set the API\_BASE\_URL variable to the ngrok URL from Kaggle: API\_BASE\_URL = "https://xxxx.ngrok.io"

\- Run the Streamlit app: streamlit run app.py

\- Access the dashboard at http://localhost:8501 in your browser.



\---

# 🚀 Usage



1. Upload your resume (PDF format) using the file uploader.



2\. Click the Analyze Resume button – a progress bar and spinner will appear while the backend processes your file.



3\. Once complete, you'll see three metric cards at the top.



4\. Use the sidebar navigation to switch between:



&#x20;  - Resume Skills Analysis – view extracted skills as badges, plus a raw text expander.



&#x20;  - Job Recommendation – browse the top 10 jobs with detailed cards.



&#x20;  - Missing Skills – explore skill gaps grouped by category and priority.



5\. Export or share your results – all data is stored in the session state for the current session.



\---

# 📸 Demo

Add screenshots, GIFs, or a demo video.

\---

# 📈 Results



The system has been tested with various resume samples and consistently delivers:

&#x20;- Average skill extraction accuracy.

&#x20;- Job recommendation relevance.

&#x20;- Good response time.

\---
# 🚀 [Tips Hindawi](https://www.tipshindawi.com/) Challenge (June–July) 2026

> 🏆 This repository is my official submission for the \[ \*\*Tips Hindawi\*\* ](https://www.tipshindawi.com/) \*\*Challenge (June–July) 2026\*\*.

## 👤 Participant

|Field|Value|
|-|-|
|Full Name|Mariam Tamer Shafiek|
|Project Name|AI Career Assistant|
|GitHub Username|mariamm547|
|Challenge Batch|June–July 2026|
|Training Program|Large Language Models (LLMs) Program|
|Organization|[**Edrak for Ai**](https://edrak4ai.com/en)|

\---

# 📖 Project Overview



**AI Career Assistant** is a production‑ready web application that helps job seekers analyze their resumes, discover suitable career paths, and identify skill gaps – all powered by state‑of‑the‑art Large Language Models.



The system uses "Mistral‑Nemo‑Instruct‑2407" to extract structured information from PDF resumes, then matches the extracted skills against a large dataset of real‑world job postings. It recommends the top 10 most relevant jobs, provides a match percentage, lists matched and missing skills, and even suggests a learning roadmap to bridge the gaps.



The application is split into two parts:

\- Backend: Runs on a GPU‑accelerated Kaggle notebook, exposing a Flask API via "NGROK".

\- Frontend: A modern "Streamlit" dashboard that runs locally on a CPU‑only machine, communicating with the backend through the public NGROK URL.



This architecture enables anyone (even without a powerful GPU) to leverage the power of large language models for career guidance.

\---

# ✨ Features



* Resume Upload: Drag‑and‑drop PDF upload with instant validation.
* Skills Extraction: Automatically extracts technical and professional skills using Mistral AI Model.
* Job Recommendations: Ranks 500+ job titles based on skill overlap, showing:Match percentage (with a progress bar), Matched skills (green), Missing skills (red), Companies hiring for that role, and job posting frequency.
* Missing Skills Analysis: Groups skills by category (Programming, Cloud, Data, ML, Soft Skills) and assigns priority (High/Medium/Low) so you know what to learn first.
* Dashboard Metrics: Displays total skills found, number of recommended jobs, and average match score.
* Modern UI: SaaS‑style design with custom CSS, responsive layout, hover animations, and colourful badges.

\---

# 🛠️ Technologies Used



Frontend: Streamlit, Python, HTML/CSS



Backend: Flask, Hugging Face Transformers, PyTorch, LangChain, PyPDF2



LLM: Mistral-Nemo-Instruct-2407 (7B)



Infrastructure: Kaggle (GPU), NGROK, FAISS 



Data: KaggleHub, Pandas, job market datasets (4 sources)



\---

# ⚙️ Installation



Before installation you must have: Python 3.9+, a Kaggle account (for GPU), and an ngrok authtoken.



Then Install the files from the repo: app.py , backend.py , requirements.txt and Project\_notebook.ipynb.



1\. Set up the Kaggle Backend (GPU):



\- Create a new Kaggle notebook with GPU accelerator (GPU T4) enabled.

\- In the notebook, add your ngrok authtoken and Hugging Face token.

\- Run all cells. The notebook will download the model (≈7 GB), start the Flask server, and print a public ngrok URL (e.g., `https://xxxx.ngrok.io`).

\- Copy that URL – you’ll need it for the frontend.



2\. Set up the Local Streamlit Frontend:



\- Install dependencies by running this in the command prompt: pip install -r requirements.txt

\- Open app.py and set the API\_BASE\_URL variable to the ngrok URL from Kaggle: API\_BASE\_URL = "https://xxxx.ngrok.io"

\- Run the Streamlit app: streamlit run app.py

\- Access the dashboard at http://localhost:8501 in your browser.



\---

# 🚀 Usage



1. Upload your resume (PDF format) using the file uploader.



2\. Click the Analyze Resume button – a progress bar and spinner will appear while the backend processes your file.



3\. Once complete, you'll see three metric cards at the top.



4\. Use the sidebar navigation to switch between:



&#x20;  - Resume Skills Analysis – view extracted skills as badges, plus a raw text expander.



&#x20;  - Job Recommendation – browse the top 10 jobs with detailed cards.



&#x20;  - Missing Skills – explore skill gaps grouped by category and priority.



5\. Export or share your results – all data is stored in the session state for the current session.



\---

# 📸 Demo



[AI Career Assistant Screenshots and Demo on Google drive](https://drive.google.com/drive/folders/1MwybAhcf7amze-CKsgDrG7i0_K-cv-gd?usp=sharing)



\---

# 📈 Results



The system has been tested with various resume samples and consistently delivers:

&#x20;- Average skill extraction accuracy.

&#x20;- Job recommendation relevance.

&#x20;- Good response time.

\---

# 🔮 Future Improvements



* Real‑time job scraping: integrate with live job boards (LinkedIn, Indeed) to provide up‑to‑date openings.
* User accounts: allow users to save analysis history and track progress over time.
* Deploy the frontend: host the Streamlit app on Streamlit Cloud or a VM for always‑on availability.
* Fine‑tune the model: fine‑tune Mistral on a curated dataset of resume‑job pairs for even better extraction.

\---

# 📚 About the Challenge

This project was developed as part of the [**Tips Hindawi**](https://www.tipshindawi.com/) **Challenge (June–July) 2026**.

[Tips Hindawi](https://www.tipshindawi.com/) is the internships department of [**Edrak for Ai**](https://edrak4ai.com/en), and the challenge encourages participants to build real-world projects, apply practical skills, and showcase their work through GitHub.

For more information about the challenge, training programs, and upcoming batches, visit the official [Tips Hindawi](https://www.tipshindawi.com/) website.

\---

# 📄 License

This project is shared for educational and portfolio purposes.


# 🔮 Future Improvements



* Real‑time job scraping: integrate with live job boards (LinkedIn, Indeed) to provide up‑to‑date openings.
* User accounts: allow users to save analysis history and track progress over time.
* Deploy the frontend: host the Streamlit app on Streamlit Cloud or a VM for always‑on availability.
* Fine‑tune the model: fine‑tune Mistral on a curated dataset of resume‑job pairs for even better extraction.

\---

# 📚 About the Challenge

This project was developed as part of the [**Tips Hindawi**](https://www.tipshindawi.com/) **Challenge (June–July) 2026**.

[Tips Hindawi](https://www.tipshindawi.com/) is the internships department of [**Edrak for Ai**](https://edrak4ai.com/en), and the challenge encourages participants to build real-world projects, apply practical skills, and showcase their work through GitHub.

For more information about the challenge, training programs, and upcoming batches, visit the official [Tips Hindawi](https://www.tipshindawi.com/) website.

\---

# 📄 License

This project is shared for educational and portfolio purposes.

