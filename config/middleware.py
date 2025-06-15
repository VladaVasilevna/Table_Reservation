from django.utils.cache import patch_cache_control


class ClientCacheControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Добавляем заголовки кеширования для статических и медиа файлов, а также для HTML страниц
        if "text/html" in response.get("Content-Type", ""):
            patch_cache_control(response, max_age=3600, public=True)
        return response
