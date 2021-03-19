# tcping

### Features
- Утилита позволяет пинговать tcp порты
- Работает только на Linux и только с правами суперпользователя
- Есть debug режим с разбором пакетов

### Запуск
```sh
$ sudo python3 tcping.py [host] [-i seconds] [-n attempts] [-p port] [-w wait sec] [--from-ip 127.0.0.1] [-d True]
```
### [OPTIONS]
```sh
host IP или URL хоста
-i Интервал между отправкой пакетов
-n количество запросов к хосту, по умолчанию бесконечный пинг
-p порт на который будет отправлен запрос, по умолчанию 80
-w Ожидание ответа в секундах, по умолчанию 5
--from-ip Возможность указать интерфейс, отличный от найденного по умолчанию
-d Debug режим, выводит хекс-дамп интересующих входящих и исходящих пакетов с кратеньким разбором (как в wireshark)
```

### Пример запуска
```sh
$ sudo python3 tcping.py google.com
```

<br>

##### `Это учебный проект`