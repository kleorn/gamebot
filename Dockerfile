FROM python:3.11.2-bullseye
# Указываем рабочую папку
WORKDIR /var/gamebot
# Копируем все файлы проекта в контейнер -  закомментировано, т.к. используем docker volumes
#COPY . /var/gamebot
#EXPOSE 80
RUN pip install telebot
CMD cd /var/gamebot && python3 bot.py