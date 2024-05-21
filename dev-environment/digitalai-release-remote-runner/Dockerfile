FROM xebialabs/release-runner:24.1.2

USER root

RUN apt update && apt install -y curl jq

COPY spin-remote-runner.sh /spin-remote-runner.sh
RUN sed -i 's/\r$//' /spin-remote-runner.sh && chmod +x /spin-remote-runner.sh

ENTRYPOINT ["/spin-remote-runner.sh"]
