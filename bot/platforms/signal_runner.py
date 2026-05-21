import asyncio
import logging
from typing import (
    Awaitable,
    Callable,
    Dict,
    List,
    Type,
)

from bot.adapters.signal.signal_http_client import SignalHttpClient
from bot.adapters.signal.signal_message import SignalMessage
from bot.adapters.signal.signal_responder import SignalResponder
from bot.database.database_manager import DatabaseManager
from bot.factory import create_all_factories
from bot.handlers import BotMessageHandler
from bot.interfaces.message import AbstractMessage
from bot.interfaces.responder import AbstractResponder
from bot.middlewares import BotMiddleware
from bot.settings import settings

logger = logging.getLogger(__name__)


async def _run_middleware_chain(
    message: AbstractMessage,
    responder: AbstractResponder,
    middlewares: List[BotMiddleware],
    final: Callable[[], Awaitable[None]],
) -> None:
    if not middlewares:
        await final()
        return

    async def next_step() -> None:
        await _run_middleware_chain(message, responder, middlewares[1:], final)

    await middlewares[0].handle(message, responder, next_step)


async def _handle_incoming_event(
    data: Dict,
    client: SignalHttpClient,
    command_handlers: Dict[str, Type[BotMessageHandler]],
    all_middlewares: List[BotMiddleware],
) -> None:
    logger.warning("Signal raw event: %s", data)

    if data.get("exception"):
        return

    envelope = data.get("envelope", {})
    data_msg = envelope.get("dataMessage")
    if not data_msg:
        logger.warning("Signal: no dataMessage, envelope keys: %s", list(envelope.keys()))
        return

    text = (data_msg.get("message") or "").strip()
    if not text:
        return

    source_uuid = envelope.get("sourceUuid", "")
    source_number = envelope.get("sourceNumber") or source_uuid
    source_name = envelope.get("sourceName", "")

    logger.warning("Signal: source=%s name=%s text=%r", source_number, source_name, text)

    if not source_number or not text.startswith("/"):
        return

    command = text.split()[0].lstrip("/").lower()
    handler_cls = command_handlers.get(command)

    if handler_cls is None:
        logger.debug("Signal: unknown command '/%s' from %s", command, source_number)
        return

    user_id = await DatabaseManager.get_or_create_signal_user(source_number)
    message = SignalMessage(
        source=source_number,
        text=text,
        user_id=user_id,
        display_name=source_name,
    )
    recipient = source_uuid or source_number
    responder = SignalResponder(client=client, recipient=recipient)

    async def execute() -> None:
        handler = handler_cls(message, responder, logger)
        await handler.handle()

    await _run_middleware_chain(message, responder, all_middlewares, execute)


async def run_signal_bot() -> None:
    client = SignalHttpClient(
        base_url=settings.SIGNAL_API_URL,
        phone=settings.SIGNAL_PHONE_NUMBER,
    )

    factories = create_all_factories(logger)
    command_handlers: Dict[str, Type[BotMessageHandler]] = {}
    all_middlewares: List[BotMiddleware] = []

    for factory in factories:
        for command, handler_cls in factory.get_command_handler_pairs():
            command_handlers[command] = handler_cls
        all_middlewares.extend(factory.get_middlewares())

    logger.info(
        "Signal: %d commands registered, %d middlewares loaded.",
        len(command_handlers),
        len(all_middlewares),
    )

    await client.start()

    async def on_event(data: Dict) -> None:
        try:
            await _handle_incoming_event(data, client, command_handlers, all_middlewares)
        except Exception as exc:
            logger.exception("Signal: error handling event: %s", exc)

    client.start_receiving(on_event)

    logger.info(
        "Signal bot listening on %s via %s.",
        settings.SIGNAL_PHONE_NUMBER,
        settings.SIGNAL_API_URL,
    )

    try:
        await asyncio.Event().wait()
    finally:
        await client.stop()
