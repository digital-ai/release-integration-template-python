FROM xebialabsunsupported/release-remote-runner:24.1.0-410.113

RUN apk add --no-cache curl jq

COPY spin-remote-runner.sh /spin-remote-runner.sh
RUN dos2unix /spin-remote-runner.sh && chmod +x /spin-remote-runner.sh

ENTRYPOINT ["/spin-remote-runner.sh"]
