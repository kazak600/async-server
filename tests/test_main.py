import unittest
from async_server.server import Server


class MainTestCase(unittest.TestCase):

    def setUp(self) -> None:
        super(MainTestCase, self).setUp()

    def tearDown(self) -> None:
        super(MainTestCase, self).tearDown()

    def test_main(self):
        self.assertEqual(True, False)

    async def test_server_startup(self):
        server = Server({})
        await server.run()
        self.assertEqual(server.config, {})

    async def test_server_serve(self):
        server = Server({})
        await server.serve()
        self.assertEqual(server.servers, [])
