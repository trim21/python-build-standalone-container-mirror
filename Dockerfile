FROM caddy@sha256:c5876b163e84c44815e2fbba68245367dcf341a15947f80bffffa011bdc90ece

EXPOSE 5678

COPY Caddyfile /etc/caddy/Caddyfile

CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile"]

COPY artifact /artifact/
