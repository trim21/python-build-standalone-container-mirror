import httpx

print(
    len(
        httpx.get(
            "https://api.github.com/repos/astral-sh/python-build-standalone/releases/latest"
        ).json()["assets"]
    )
)
