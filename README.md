# Job Resune Tracker 

AI Powered job application tracker that uses an LLM to tailor resumes and cover letters per job opening. 
Built to solve a real problem: manually tailoring application materials for each job posting is repetitive. 
This automates the tailoring step while tracking outcomes to learn what actually works.

## Architecture

- MySQL — stores jobs, applications, tailored materials, and tailoring run history
- FastAPI  — endpoints to submit jobs, trigger tailoring, and track application status
- LLM  — generates tailored resume/cover letter content per job posting
- Cloud data platform  — syncs application data for funnel analysis and trend reporting
