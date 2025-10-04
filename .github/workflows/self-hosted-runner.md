goto github actions -> runners -> self-hosted runners -> new runner -> follow instructions

each runner must be in different folders (actions-runner-01, actions-runner-02, actions-runner-03 etc.)

run as service:

sudo ./svc.sh install

sudo systemctl start actions.runner.molokov-klim-Appium-Python-Client-Shadowstep.vps-XXX.service

sudo systemctl status actions.runner.molokov-klim-Appium-Python-Client-Shadowstep.vps-XXX.service

dont forget remove downloaded archive
