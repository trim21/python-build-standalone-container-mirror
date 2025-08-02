FROM caddy@sha256:e23538fceb12f3f8cc97a174844aa99bdea7715023d6e088028850fd0601e2e2

EXPOSE 5678

COPY Caddyfile /etc/caddy/Caddyfile

CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile"]

COPY artifact /artifact/
