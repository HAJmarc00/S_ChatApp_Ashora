# asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter  # type: ignore

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')  # اسم پروژه‌ت رو جایگزین کن

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # "websocket": URLRouter(...) ← اینو بعداً اضافه می‌کنیم
})
