FROM python:3.11.2-bullseye
# ��������� ������� �����
WORKDIR /var/gamebot
# �������� ��� ����� ������� � ��������� -  ����������������, �.�. ���������� docker volumes
#COPY . /var/gamebot
#EXPOSE 80
RUN pip install telebot
CMD cd /var/gamebot && python3 bot.py