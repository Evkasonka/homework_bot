class MessageSendError(Exception):
    """Ошибка отправки сообщения"""


class CheckTokenError(Exception):
    """Отсутствует важная переменная"""


class ResponseApiError(Exception):
    """ошибка API-сервиса"""
