import logging
import os
import requests
import telegram
import time
from http import HTTPStatus
from dotenv import load_dotenv
from exceptions import MessageSendError, CheckTokenError


load_dotenv()

PRACTICUM_TOKEN = os.getenv('YA_PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('MY_TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('MY_TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(message)s', level=logging.INFO)
handler = logging.StreamHandler()


def check_tokens() -> bool:
    """Проверяет доступность переменных окружения.
    Если отсутствует хотя бы одна переменная окружения — ошибка.
    """
    if not all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        logging.critical('Отсутствует хотя бы одна переменная окружения')
        raise CheckTokenError('Отсутствует хотя бы одна переменная окружения')
    return True


def send_message(bot: telegram.bot.Bot, message: str) -> None:
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug(f'Сообщение отправлено: {message}')
    except Exception as error:
        error = f'Сообщение не удалось отправить: {error}'
        logging.error(error)
        raise MessageSendError(error)


def get_api_answer(timestamp: int) -> dict:
    """Запрос к единственному эндпоинту API-сервиса."""
    playload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=playload)
        if response.status_code != HTTPStatus.OK:
            logging.error(f'Ошибка доступа к {ENDPOINT}. Код ответа: '
                          f'{response.status_code}')
            raise Exception(f'Эндпоинт API-сервиса не доступен: '
                            f'Код ответа: {response.status_code}')
        if response is None:
            message = ('нет ответа от API-сервиса')
            logging.error(message)
            raise Exception(message)
        return response.json()
    except Exception as error:
        message = (f'При запросе к API произошел сбой. "{error}"')
        logging.error(message)
        raise Exception(message)


def check_response(response: dict) -> list:
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError('ответ API не является словарем')
    if 'homeworks' not in response:
        message = ('Ответ API не содержит ключа "homeworks"')
        logging.error(message)
        raise KeyError(message)
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        message = ('Ключ "homeworks" не является списком')
        logging.error(message)
        raise TypeError(message)
    return homeworks


def parse_status(homework: dict) -> str:
    """Извлекает из информации о конкретной домашней работе статус."""
    if not isinstance(homework, dict):
        raise Exception('homework не словарь.')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_name is None:
        raise Exception('Ключ "homework_name" не обнаоужен')
    if homework_status in HOMEWORK_VERDICTS:
        verdict = HOMEWORK_VERDICTS[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    raise Exception(f'Неизвестный статус "{homework_status}"')


def main() -> None:
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    send_message(bot, 'Бот запущен')
    timestamp = int(time.time())
    last_message = ''

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            for homework in homeworks:
                message = parse_status(homework)
                send_message(bot, message)
            else:
                logging.debug('Нет нового статусa')
        except Exception as error:
            message_error = f'Сбой в работе программы: {error}'
            logging.error(message_error)
            if message_error != last_message:
                last_message = message_error
                send_message(bot, message_error)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
