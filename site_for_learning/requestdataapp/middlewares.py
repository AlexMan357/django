from datetime import datetime
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def set_useragent_on_request_middleware(get_response):
    """ Ф-я Middleware для вывода данных о User-Agent запроса """
    # print("initial_call")

    def middleware(request: HttpRequest):
        # print("before get_response")
        request.user_agent = request.META["HTTP_USER_AGENT"]
        response = get_response(request)
        # print("after get_response")
        return response

    return middleware


class CountRequestsMiddleware:
    """
        Класс Middleware: реализует счетчик запросов, счетчик ответов, счетчик ошибок
        Args:
            get_response (function): объект, который принимает запрос и возвращает ответ
            requests_count (int): счетчик запросов
            responses_count (int): счетчик ответов
            exceptions_count (int): счетчик ошибок
   """
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_count = 0
        self.responses_count = 0
        self.exceptions_count = 0

    def __call__(self, request: HttpRequest):
        self.requests_count += 1
        # print("requests_count", self.requests_count)
        response = self.get_response(request)
        self.responses_count += 1
        # print("responses_count", self.responses_count)
        return response

    def process_exception(self, request: HttpRequest, exception: Exception):
        """ Ф-я для подсчета ошибок при запросах """
        self.exceptions_count += 1
        print("got", self.exceptions_count, "exceptions so far")


class ThrottlingRequestsMiddleware:
    """
    Класс Middleware: проверяет как давно пользователь с IP выполнял запрос
    Args:
        get_response (function): объект, который принимает запрос и возвращает ответ
        user_data (dict): словарь. Ключ: IP- адрес. Значение: последняя дата визита
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.user_data = dict()

    def __call__(self, request: HttpRequest) -> HttpResponse:
        ip_address = str(request.META["REMOTE_ADDR"])

        date_now = datetime.now()
        date_last_visit = self.user_data.get(ip_address, date_now)

        first_date = datetime.strptime(date_now.strftime('%d.%m.%Y %H:%M:%S'), '%d.%m.%Y %H:%M:%S')
        second_date = datetime.strptime(date_last_visit.strftime('%d.%m.%Y %H:%M:%S'), '%d.%m.%Y %H:%M:%S')
        delta = first_date - second_date
        # print("DELTA", delta.seconds)

        # if delta.seconds > 1 or delta.seconds == 0:
        #     self.user_data[ip_address] = date_now
        #     # print("DICT USER_DATA", self.user_data)
        response = self.get_response(request)
        return response

        # return render(request, 'requestdataapp/error.html')
