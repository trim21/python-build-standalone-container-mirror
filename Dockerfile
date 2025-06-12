FROM caddy

EXPOSE 5678

COPY Caddyfile /etc/caddy/Caddyfile

CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile"]

COPY artifact /artifact/
