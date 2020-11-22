import unittest
from unittest.mock import Mock
from async_server.signals import Signal
from async_server.web_app import Application


class MainTestCase(unittest.TestCase):

    async def test_function_signal_dispatch(self):
        app = Application()
        signal = Signal(app)
        kwargs = {'foo': 1, 'bar': 2}

        callback_mock = Mock()

        async def callback(**kwargs):
            callback_mock(**kwargs)

        signal.append(callback)
        signal.freeze()

        await signal.send(**kwargs)
        callback_mock.assert_called_once_with(**kwargs)
