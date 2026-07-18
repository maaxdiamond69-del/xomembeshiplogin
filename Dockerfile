FROM python:3.13

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright dependencies
RUN playwright install-deps

# Install Chromium
RUN playwright install chromium

COPY . .

CMD ["python", "xobot.py"]
