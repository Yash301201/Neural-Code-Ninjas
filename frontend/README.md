# LearnPath AI frontend

Open the root project README for the complete run and showcase guide. Run `start-project.ps1` in the parent LearnPathAI folder and open http://127.0.0.1:8001/app.

This is a buildless HTML/CSS/JavaScript frontend. FastAPI serves its assets from the same origin and all private data comes from authenticated backend calls. No hardcoded assessment scores, attendance values or charts are used. The local showcase login buttons use the fictional accounts enabled by `backend/scripts/prepare_showcase.py`.

Do not open index.html directly using a file:// URL: authentication and API calls require the FastAPI server. For another local port use the root launcher `-Port` option. No node_modules folder is needed.
