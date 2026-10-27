# AI Resume Tailoring Platform

> **Status: Backend in development** · Formerly **Job Resume Tracker**

An API-first application for organizing a candidate's verified professional background and, eventually, generating tailored resumes and cover letters for specific job descriptions.

The project began as a job-application tracker. Its focus has since changed: **application-status tracking is being retired** in favor of candidate profiles, job-description storage, accurate AI-assisted tailoring, and document history.

**Repository:** [NyanJahdiel/jobresumetracker](https://github.com/NyanJahdiel/jobresumetracker)  
**Development branch:** `feature/project-setup`

## Project goals

- Let users register and maintain a reusable professional profile.
- Save job descriptions and associate them with the correct candidate.
- Analyze job requirements against real skills, education, projects, and experience.
- Tailor resumes and cover letters **without inventing qualifications**.
- Let users review, revise, and export tailored documents.

**Important:** The AI-analysis, resume upload, generation, and export features are **planned, not yet implemented**. The repository currently contains a backend foundation.

## Technology stack

| Layer | Technology |
| --- | --- |
| API framework | Python 3.12, FastAPI, Uvicorn |
| Database | MySQL |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Schema migrations | Alembic |
| Authentication | JWT (PyJWT), OAuth2 password form, Argon2 password hashing (`pwdlib`) |
| Local configuration | `python-dotenv` |
| AI pipeline | Planned; no model/provider integration yet |
| Frontend and document export | Planned |

## Current development status

| Component | Status |
| --- | --- |
| FastAPI API and interactive documentation | Implemented |
| MySQL connection and ORM models | Implemented |
| Alembic baseline and user/profile ownership migration | Implemented |
| User registration and JWT login routes | Implemented; testing in progress |
| Candidate profile create/read/update routes | Implemented; testing in progress |
| User-scoped job create/list/detail routes | Implemented; testing in progress |
| Cross-account authorization tests | Not yet automated |
| Authenticated resume upload and PDF/DOCX text preview | Implemented; needs endpoint testing |
| Job-description analysis and skill-gap matching | Not implemented |
| AI resume/cover-letter generation | Not implemented |
| Document versioning/export | Not implemented |
| Frontend | Not implemented |

The original application-tracking ORM models and tables remain for compatibility during the database redesign. **Tracking application progress is not part of the new product direction.**

## Repository layout

```text
jobresumetracker/
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI application and router registration
│   ├── database.py           # MySQL engine and session dependency
│   ├── models.py             # SQLAlchemy ORM models
│   ├── schemas.py            # Pydantic request/response models
│   ├── security.py           # Password hashing and JWT creation
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py           # Registration, login, current user
│   │   ├── profile.py        # Authenticated candidate-profile endpoints
│   │   ├── jobs.py           # Authenticated job endpoints
│   │   └── tailoring.py      # Placeholder; not implemented
│   └── services/             # Reserved for business logic
├── migrations/
│   ├── env.py
│   └── versions/
├── alembic.ini
├── requirements.txt
├── .env.example
└── README.md
```

## Data model

The existing database currently includes:

| Table | Purpose |
| --- | --- |
| `users` | Account email, password hash, active status |
| `candidate_profiles` | Personal and professional details; linked to a user |
| `jobs` | Saved job postings; linked to a candidate profile |
| `applications` | Legacy application-status tracking; to be retired |
| `tailoring_runs` | Legacy AI-run structure; to be redesigned |
| `materials` | Legacy document structure; to be redesigned |

**Ownership design:** One user has at most one candidate profile in the current schema; a profile may have many jobs. All users share database tables, and access control is enforced through authenticated queries. Ownership foreign keys are currently nullable to support migration of older records; tightening these constraints is future work.

The planned document model will associate each tailoring run with the source job and profile, and associate generated materials with the corresponding tailoring run. It is **not yet represented by the legacy table relationships**.

## Local development

### Prerequisites

- Python 3.12 (the version currently used during development)
- A running MySQL server and a database account with permissions for `jobresumetracker`
- Git and a terminal (PowerShell examples below)

### 1. Clone and open the development branch

```powershell
git clone https://github.com/NyanJahdiel/jobresumetracker.git
cd jobresumetracker
git switch feature/project-setup
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The checked-in `requirements.txt` is not yet synchronized with all recently added modules. Until it is updated, install these additional development dependencies:

```powershell
python -m pip install alembic "pwdlib[argon2]" PyJWT "pydantic[email]" python-multipart
```

### 3. Configure environment variables

**Current checked-in code** in `app/database.py` and `app/security.py` explicitly loads `.env.jobresumetracker` from the project root. Create that local file (or update both loaders if using a different name).

```dotenv
DATABASE_URL=mysql+pymysql://YOUR_USER:YOUR_URL_ENCODED_PASSWORD@localhost:3306/jobresumetracker
JWT_SECRET_KEY=REPLACE_WITH_A_RANDOM_SECRET
```

Generate a random JWT secret with:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

If the MySQL password contains reserved URL characters such as `@`, `#`, `/`, or `:`, percent-encode them in `DATABASE_URL`.

**Do not commit your real environment file or credentials.** Add `.env.*` to `.gitignore` while keeping `.env.example` as a sanitized template. A previously committed secret must also be **rotated**; adding a Git ignore rule does not remove it from Git history.

### 4. Database migrations (existing development database)

The repository currently uses an **empty baseline** revision, `d1e90dc1e9d7`, followed by the ownership migration `2a16bfd835d7`. The baseline assumes that the original tables already exist.

For an **existing database with the original schema and a correctly recorded baseline**, check and apply pending migrations:

```powershell
python -m alembic current
python -m alembic heads
python -m alembic upgrade head
```

**Fresh database setup is not yet fully reproducible from Alembic migrations alone.** Do not stamp an empty database or manually adjust `alembic_version` to bypass missing tables. A complete initial-schema migration is on the roadmap.

### 5. Run the API

From the repository root:

```powershell
python -m uvicorn app.main:app --reload
```

- Health check: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Interactive API documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- OpenAPI specification: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

**Development note:** The current `app/main.py` still calls `Base.metadata.create_all(bind=engine)`. That is temporary; the intention is to rely on reviewed Alembic migrations for schema management.

## API reference (current source code)

| Method | Endpoint | Description | Authentication |
| --- | --- | --- | --- |
| `GET` | `/` | Health check | No |
| `POST` | `/auth/register` | Register a user | No |
| `POST` | `/auth/login` | Login using form fields `username` (email) and `password` | No |
| `GET` | `/auth/me` | Get current account | Bearer JWT |
| `POST` | `/profiles/me` | Create your profile | Bearer JWT |
| `GET` | `/profiles/me` | Get your profile | Bearer JWT |\n| `POST` | `/profiles/me/resume` | Upload a PDF/DOCX and preview extracted text (not saved) | Bearer JWT |
| `PATCH` | `/profiles/me` | Update your profile | Bearer JWT |
| `POST` | `/jobs/` | Save a job description | Bearer JWT |
| `GET` | `/jobs/` | List jobs for your profile | Bearer JWT |
| `GET` | `/jobs/{job_id}` | Get one of your jobs | Bearer JWT |

### Resume upload and text-extraction preview

After authenticating, use `POST /profiles/me/resume` in Swagger UI with a `.pdf` or `.docx` file (maximum **5 MB**). The API returns the filename, file size, extracted text and character count. **The uploaded file and extracted text are not persisted or written into the candidate profile.** Review/edit and explicit save will be added next.

Limits: maximum 30 PDF pages and 100,000 extracted characters. Scanned/image-only PDFs and encrypted documents are not supported. DOCX extraction includes ordinary body paragraphs and tables, but may miss text stored in headers, footers, or complex drawing objects.

Install the additional parser dependencies listed in `requirements.txt`. Run extraction unit tests with:

```powershell
python -m pip install pytest
python -m pytest tests/test_resume_extraction.py -q
```

### Example: save a job

After registering, logging in, and creating a profile, authorize with your bearer token in Swagger UI and submit:

```json
{
  "title": "Junior Machine Learning Engineer",
  "company": "Example Technologies",
  "posting_text": "Python, model training, REST APIs and SQL."
}
```

The API associates the job with the profile belonging to the authenticated user. The implementation should be tested with **two different accounts** to verify cross-account isolation.

## Roadmap

1. [x] Set up FastAPI, SQLAlchemy and MySQL.
2. [x] Add Alembic and introduce the `users` table.
3. [x] Implement registration/login and authenticated profile/job routes in source code.
4. [ ] Add automated authentication and authorization tests, including two-user isolation.
5. [ ] Resolve legacy tables and enforce non-null ownership constraints.
6. [ ] Make fresh-database migrations reproducible and synchronize dependencies.
7. [x] Implement authenticated PDF/DOCX text extraction preview (local endpoint verification pending).
8. [ ] Review, confirm and persist extracted resume information before updating a profile.\n9. [ ] Extract job requirements and compare them against verified profile facts.
10. [ ] Implement LLM-assisted tailoring with human review and no fabricated qualifications.
11. [ ] Redesign tailoring/document history and support PDF/DOCX export.
12. [ ] Build a frontend and prepare for deployment.

## Security and privacy

- Passwords are hashed with Argon2; raw passwords must never be stored.
- JWT access tokens expire after 30 minutes in the current implementation.
- User-scoped queries must never trust arbitrary `user_id` or `profile_id` values supplied by clients.
- Current source code is **not production hardened**: permissions, migrations, validation, tests, secret handling, and deployment configuration need further work.
- Treat stored resumes and candidate profiles as personal data. Add retention, deletion, and authorization controls before production deployment.
- **Security TODO:** Audit and remove any committed local environment files; rotate credentials that have been exposed in Git history.

## License

See [LICENSE](LICENSE).

---

Developed as a hands-on Python backend, database design, authentication, and applied AI engineering project.
