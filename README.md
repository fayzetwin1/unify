# Unify Messenger
A messenger that doesn't have something serious in it.



![logo](https://github.com/user-attachments/assets/83ddee9d-c183-4576-97a9-a1934aa8a260)

/// ENG ///

Please read it right away!

Unify Messenger can be a template for your project, which has developed a full-fledged function of correspondence between users with session support, a backend server on Flask, an authorization system on the SQLite database and a BCrypt password encryption system.

This project is not something serious for me. The messenger was made just like that, without any seriousness or desire to make some kind of major project out of it.

Now, let's move on to the guide for installing the messenger on your server. The Backend and Frontend parts of the messenger consist of two files: server.py and client.py . The entire project was written entirely in Python, but you can easily rewrite Frontend for yourself into any other programming language. 

First, you will need to download the project and install the necessary libraries from requirements.txt . I think you will figure out how to do this. 

And then, you just run server.py , and in this case, you have the Unify server running. 

To launch the messenger client, you will need to run client.py . If you want to get more information about the client's work (or, roughly speaking, enable Debug mode), then run client.py with the --debug argument. 

Eg:

python client.py --debug

Well, then you can safely work with the messenger and interact with its code.


/// RUS /// 

Прошу ознакомиться сразу!

Unify Messenger может являться шаблоном для вашего проекта, в котором разработана полноценная функция переписки между пользователями с поддержкой сессий, backend сервером на Flask, системой авторизацией на БД SQLite и систему шифрования паролей BCrypt.

Данный проект не является для меня чем-то серьезным. Мессенджер был сделан просто так, без какой либо серьезности или желания делать из него какой-то крупный проект.

Теперь, перейдем к гайду по установке мессенджера на ваш сервер. Backend и Frontend часть мессенджера состоят из двух файлов: server.py и client.py. Весь проект был полностью написан на Python, но Frontend вы можете переписать под себя спокойно на любой другой язык программирования. 

Для начала, Вам нужно будет скачать проект и установить нужные библиотеки из requirements.txt. Как это сделать, я думаю Вы разберетесь. 

Ну и далее, Вы просто запускаете server.py, и в таком случае у Вас запускается сервер Unify. 

Чтобы запустить клиент мессенджера, вам нужно будет запустить client.py. Если Вы хотите получать больше информации о работе клиента (ну или грубо говоря включить Debug режим), то запустите client.py с аргументом --debug. 

К примеру:

python client.py --debug

Ну а далее Вы можете спокойно работать с мессенджером и взаимодействовать с его кодом. 
