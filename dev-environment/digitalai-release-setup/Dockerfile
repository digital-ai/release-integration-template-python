FROM alpine:3.8

RUN apk add --no-cache curl

RUN curl --fail-early -o /usr/local/bin/xl https://dist.xebialabs.com/public/xl-cli/22.3.9/linux-amd64/xl && \
    chmod +x /usr/local/bin/xl

RUN curl --fail-early -o /usr/local/bin/wait-for https://raw.githubusercontent.com/eficode/wait-for/master/wait-for && \
    chmod +x /usr/local/bin/wait-for

RUN mkdir /.xebialabs
RUN chmod 777 /.xebialabs

USER 10001
VOLUME "/data"

COPY ./config.yaml /.xebialabs/config.yaml
# RUN xl version

ENTRYPOINT ["/usr/local/bin/wait-for", "-t", "600", "digitalai-release:5516", "--", "/usr/local/bin/xl"]
