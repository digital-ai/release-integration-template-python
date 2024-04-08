# todo change image to official
FROM xlr-registry:5050/digitalai/release-runner:0.2.0

RUN apk add --no-cache curl jq

COPY spin-remote-runner.sh /spin-remote-runner.sh
RUN dos2unix /spin-remote-runner.sh && chmod +x /spin-remote-runner.sh

ENTRYPOINT ["/spin-remote-runner.sh"]
