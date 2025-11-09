# Self-hosted Runner Setup

1. Open `GitHub Actions → Runners → Self-hosted runners → New runner` and follow the instructions in the UI.
2. Create a dedicated directory for each runner, for example `actions-runner-01`, `actions-runner-02`, `actions-runner-03`.
3. Install the service script:

    ```bash
    sudo ./svc.sh install
    ```

4. Start the service:

    ```bash
    sudo systemctl start actions.runner.molokov-klim-Appium-Python-Client-Shadowstep.vps-XXX.service
    ```

5. Verify the service status:

    ```bash
    sudo systemctl status actions.runner.molokov-klim-Appium-Python-Client-Shadowstep.vps-XXX.service
    ```

6. Remove the downloaded runner archive after installation to keep the workspace clean.
