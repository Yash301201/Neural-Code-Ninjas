"""Launch the integration suite in a fresh process, never against the live schema."""
from pathlib import Path
import os,sys,subprocess
from dotenv import dotenv_values
from sqlalchemy.engine import make_url

def main():
    backend=Path(__file__).resolve().parents[1]
    config=dotenv_values(backend/'.env')
    base=os.environ.get('DATABASE_URL') or config.get('DATABASE_URL')
    if not base:raise SystemExit('Configure backend/.env first')
    parsed=make_url(base)
    if parsed.get_backend_name()!='mysql':raise SystemExit('MySQL is required')
    target=parsed.set(database='learnpath_ai_test')
    env=os.environ.copy();env['TEST_DATABASE_URL']=target.render_as_string(hide_password=False)
    print('Running checks only against learnpath_ai_test; actual engine guard is enforced by the suite.')
    raise SystemExit(subprocess.run([sys.executable,'-m','pytest','tests/test_backend.py','-q','--tb=short'],cwd=backend,env=env).returncode)
if __name__=='__main__':main()
