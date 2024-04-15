FROM xebialabsunsupported/release-runner:24.1.0-412.113

USER root

RUN apt update && apt install -y curl jq dos2unix

COPY spin-remote-runner.sh /spin-remote-runner.sh
RUN dos2unix /spin-remote-runner.sh && chmod +x /spin-remote-runner.sh

ENTRYPOINT ["/spin-remote-runner.sh"]
