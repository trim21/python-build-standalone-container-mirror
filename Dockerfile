FROM caddy@sha256:9e95012adcbbd599f853cb315b986781845c238f9e52aa3652798758cca01422

EXPOSE 5678

COPY Caddyfile /etc/caddy/Caddyfile

CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile"]

COPY artifact /artifact/
