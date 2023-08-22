import traceback
from abc import ABC, abstractmethod
from typing import Optional
from channels.exceptions import StopConsumer
from django.http import HttpResponseServerError
from config_manager import get_config
from .base import BaseHttpMiddleware, BaseWebsocketMiddleware

config = get_config()


class ErrorLoggingInterface(ABC):
    @abstractmethod
    def log_error(self, context: str, error_message: str):
        pass


class ConsoleErrorLogger(ErrorLoggingInterface):
    def log_error(self, context: str, error_message: str):
        pass


class FileErrorLogger(ErrorLoggingInterface):
    def __init__(self, error_file_path: Optional[str] = None):
        if not error_file_path:
            error_file_path = "./error_log.out"
        self.error_file_path = error_file_path

    def log_error(self, context: str, error_message: str):
        pass


class EmailNotifierLogger(ErrorLoggingInterface):
    def __init__(
        self, recipient_email: Optional[str] = None, sender_email: Optional[str] = None
    ):
        if not recipient_email:
            recipient_email = "admin@admin.com"
        if not sender_email:
            sender_email = "admin@admin.com"
        self.recipient_email = recipient_email
        self.sender_email = sender_email

    def log_error(self, context: str, error_message: str):
        pass


class ErrorLoggingMiddleware:
    @classmethod
    async def handle_error(
        cls,
        context: str,
        error_message: str,
        loggers: Optional[list[ErrorLoggingInterface]] = None,
    ):
        # default: send mail and log in file if production
        # default: print on console for development
        if loggers is None:
            loggers = (
                [EmailNotifierLogger(), FileErrorLogger()]
                if not config.DEBUG
                else [ConsoleErrorLogger()]
            )
        for logger in loggers:
            logger.log_error(context, error_message)


class HttpErrorLoggingMiddleware(BaseHttpMiddleware, ErrorLoggingMiddleware):
    def __call__(self, request):
        if self.skip_middleware(request):
            # continue with other middleware/ view
            return self.get_response(request)

        try:
            response = self.get_response(
                request
            )  # invokes the next middleware in the chain if their else invokes the main view
            return response
        except Exception:
            self.handle_error("Error while handling request", traceback.format_exc())
            return HttpResponseServerError(
                "An error occurred while processing your request.", status=500
            )


class WebsocketErrorLoggingMiddleware(BaseWebsocketMiddleware, ErrorLoggingMiddleware):
    async def __call__(self, scope, receive, send):
        if self.skip_middleware(scope):
            # continue with other middleware/ view
            return await super().__call__(scope, receive, send)

        # wrapping function passed over call
        async def logging_receive():
            try:
                return await receive()
            except Exception:
                await self.handle_error(
                    "Error receiving message", traceback.format_exc()
                )
                raise StopConsumer()

        async def logging_send(message):
            try:
                return await send(message)
            except Exception as e:
                await self.handle_error("Error sending message", traceback.format_exc())
                raise StopConsumer()

        try:
            # Call the inner application with the wrapped receive and send
            return await super().__call__(scope, logging_receive, logging_send)
        except Exception as e:
            await self.handle_error(
                "Error during WebSocket connection", traceback.format_exc()
            )
            raise StopConsumer()
