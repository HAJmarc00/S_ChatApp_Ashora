# از تصویر رسمی پایتون
FROM python:3.13

# تنظیم مسیر کاری
WORKDIR /app

# کپی فایل‌ها به کانتینر
COPY . /app

# نصب وابستگی‌ها
RUN pip install --upgrade pip
RUN pip install -r requirements/requirement.txt

# پورت پیش‌فرض برای Django
EXPOSE 8000

# اجرای سرور Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
