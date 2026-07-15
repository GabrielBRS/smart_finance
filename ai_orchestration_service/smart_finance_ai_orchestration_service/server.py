import os
from granian import Granian
from granian.constants import Interfaces

if __name__ == "__main__":
    is_dev = os.getenv("ENV", "dev") == "dev"

    Granian(
        target="main:app",
        interface=Interfaces.ASGI,
        address="0.0.0.0",
        port=8000,
        workers=1 if is_dev else 4,   # dev: 1 worker + reload; prod: N workers
        reload=is_dev,
        loop="uvloop",
    ).serve()