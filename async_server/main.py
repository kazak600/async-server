from datetime import datetime
from async_server.server import Server
from async_server.config import Config


def run():
    print(f'Time {datetime.utcnow()}')
    server = Server(config=Config())
    server.run()


if __name__ == '__main__':
    run()
