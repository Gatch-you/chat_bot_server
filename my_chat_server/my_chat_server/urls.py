from django.contrib import admin
from django.urls import include, path
from line_bot.views import ChatwitBotView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/chat_with_user/', ChatwitBotView.as_view(), name='chat_with_gpt'),
    path('line_bot/', include('line_bot.urls')),
]
