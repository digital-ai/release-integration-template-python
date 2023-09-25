FROM xebialabsunsupported/release-remote-runner:23.3.0-beta.6

RUN apk add --no-cache curl jq

COPY spin-remote-runner.sh /spin-remote-runner.sh
RUN chmod +x /spin-remote-runner.sh

ENTRYPOINT ["/spin-remote-runner.sh"]
