# Recommendation module for Box my domain

Run `pip3 install --index-url https://${artifactory_id}:${artifactory_pw}@${artifactory_url} -r requirements.txt ` to install requirements. 

For LLM calls, find AWS creds need to be set up (instruction: https://github.com/gdcorp-domains/find-aws/tree/master/bashrc) and login script (adev) is present in ~/.zshrc

Run `python3 mystery_box_rec.py` to start the fasapi server. Docs available at http://localhost:8005/docs