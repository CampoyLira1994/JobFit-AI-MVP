# Installation Guide

This guide installs the **public JobFit-AI-MVP repository currently published on `main`**.

> The newer Campoy Nexus / JobFit Alpha implementation is documented in
> `docs/CURRENT_ARCHITECTURE.md`, but its full source tree has not yet been
> synchronized into this public mirror. Do not expect the public MVP to expose
> every Nexus screen or worker endpoint described there.

## 1. Requirements

Recommended:

- Git
- Python 3.11
- pip
- Windows 10/11, Linux or macOS
- Docker Desktop only if using the container option

For searches against external providers you also need credentials for the provider
you choose to use. Keep them only in your local `.env` file.

## 2. Clone the repository

```bash
git clone https://github.com/CampoyLira1994/JobFit-AI-MVP.git
cd JobFit-AI-MVP
```

## 3. Create a virtual environment

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Windows CMD

```cmd
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Linux / macOS

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## 4. Optional Playwright browser

The legacy API/scraper modules can use Playwright. Install Chromium only when
you need those modules:

```bash
python -m playwright install chromium
```

On Linux, system packages may also be required:

```bash
python -m playwright install --with-deps chromium
```

## 5. Configure environment variables

Copy the template:

### Windows CMD

```cmd
copy .env.example .env
```

### PowerShell

```powershell
Copy-Item .env.example .env
```

### Linux / macOS

```bash
cp .env.example .env
```

Edit `.env` and fill **only** the providers you are authorized to use.

For Adzuna, for example:

```env
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
ADZUNA_COUNTRY=mx
```

Never commit the resulting `.env`.

## 6. Validate the installation

Run the focused tests:

```bash
python -m pytest tests/jobfit
```

Then run the local scoring example:

```bash
python examples/jobfit_demo.py
```

The example uses `Candidate Example 001`, a synthetic profile with no real
personal data.

## 7. Run the multi-source demo

When provider credentials are configured:

```bash
python examples/multi_source_jobfit_demo.py
```

Runtime output is written under ignored local directories and should not be
committed.

## 8. Start the legacy FastAPI service

```bash
python start_api.py
```

The public MVP API is the legacy service included in this repository. It is not
the same service topology as the newer Campoy Nexus API + PostgreSQL + dedicated
JobFit worker described in the architecture document.

## 9. Docker option

Build:

```bash
docker build -t jobfit-ai-mvp .
```

Run:

```bash
docker run --rm -p 8080:8080 --env-file .env jobfit-ai-mvp
```

Then open:

```text
http://localhost:8080
```

Do not publish a container with a baked-in `.env` or credentials.

## 10. Working with classmates

Recommended workflow:

```bash
git checkout -b feature/short-description
# make changes
python -m pytest tests/jobfit
git add .
git commit -m "feat: describe the contribution"
git push origin feature/short-description
```

Then open a Pull Request instead of pushing experimental work directly to
`main`.

## 11. Troubleshooting

### Python command not found

On Windows try:

```cmd
py -3.11 --version
```

### Import errors

Confirm the virtual environment is active and reinstall:

```bash
python -m pip install -r requirements.txt
```

### External search returns authentication errors

Check the corresponding keys in your local `.env`. Do not paste credentials
into issues, commits or screenshots.

### Playwright browser missing

```bash
python -m playwright install chromium
```

## Security checklist

Before every push:

- no `.env`
- no API keys
- no CVs or identity documents
- no real candidate names
- no personal email/phone/address
- no database dumps
- no runtime artifacts containing personal data

See `SECURITY.md` and `CONTRIBUTING.md` for the repository rules.
