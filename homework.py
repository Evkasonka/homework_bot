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


def check_tokens():
    """Проверяет доступность переменных окружения.
    Если отсутствует хотя бы одна переменная окружения — ошибка.
    """
    if (PRACTICUM_TOKEN is None
            or TELEGRAM_TOKEN is None
            or TELEGRAM_CHAT_ID is None):
        logging.critical('Отсутствует хотя бы одна переменная окружения')
        raise CheckTokenError('Отсутствует хотя бы одна переменная окружения')
    else:
        return True


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug(f'Сообщение отправлено: {message}')
    except Exception as error:
        error = f'Сообщение не удалось отправить: {error}'
        logging.error(f'Ошибка при отправке сообщения: {error}')
        raise MessageSendError(f'Ошибка при отправке сообщения: {error}')


def get_api_answer(timestamp):
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
            logging.error('нет ответа от API-сервиса')
            raise Exception('нет ответа от API-сервиса')
        return response.json()
    except Exception as error:
        logging.error(f'При запросе к API произошел сбой. "{error}"')
        raise Exception(f'При запросе к API произошел сбой. "{error}"')


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError('ответ API не является словарем')
    if 'homeworks' not in response.keys():
        logging.error('Ответ API не содержит ключа "homeworks"')
        raise KeyError('Ответ API не содержит ключа "homeworks"')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        logging.error('Ключ "homeworks" не является списком')
        raise TypeError('Ключ "homeworks" не является списком')
    return homeworks


def parse_status(homework):
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


def main():
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
                if message:
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
