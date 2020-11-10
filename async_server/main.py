from datetime import datetime
from async_server.server import Server


def run():
    print(f'Time {datetime.utcnow()}')
    server = Server()
    server.run()


if __name__ == '__main__':
    run()
