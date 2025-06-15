#------------------------Migrações------------------------#
Django Admin(IMPORTANTE):
python manage.py importar_ambientes.py
python manage.py importar_tarifas.py

Models:
python manage.py makemigrations
python manage.py migrate

#---------------MUDANÇAS pra teste(settings)--------------#

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'energy_manager',
        'USER': 'postgres',
        'PASSWORD': '1303',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

GEMINI_API_KEY = "AIzaSyClP7PDzQR6AYg1hH7RZoNiZ-reoiQrNrs" (Opcional, se quiser colocar tua chave API do GEMINI IA)

OBSERVAÇÃO: Verifique se seu Interpretador está na .venv correta (Python da venv)

#----------------Ideias de Telas----------------#

Front-end -> (Meninas)

Configurações -> Perfil (Opcional) / Modo Escuro e Branco / FAQ / Ajuda (Contatos)

Tela de Feedback -> Comentários

Chat BOT (AJUDANTE) -> se quiserem ajudo (que fica naqueles canto inferiores da tela)

#-----------------Separação-----------------#

Cada funcionalidade separada (#-------#) com comentários (Fique de olhos abertos)
A urls é a mais importante, por isso tem mais comentários lá

#--------------Tesseract OCR)---------------#

Versão do Tesseract Salva no Drive (No grupo) -> Extrair em "Arquivos de Programas" (Extraia direto lá)

PATH -> EDITAR A VARIAVEL DE AMBIENTE -> ENDEREÇO DE TesseractOCR (OCR)

OpenCV: pip install opencv-python -> OpenCV

#--------------Gemini IA---------------------#

API KEY do Gemini IA
Link: https://aistudio.google.com/prompts/new_chat

Sempre garanta que tenha esse formato abaixo:
curl: "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=GEMINI_API_KEY"

#-------------------------------Relacionado ao QRCode e Celular (Em Manutenção)---------------------------------#

#-------------Frontend--------------# --> Unica que tem isso é o leitura-qr

Os endereços são diferentes: Exemplo: 10.30.57.32 (Faculdade)

Encontrar local host:

No cmd do Computador:

ipconfig

encontre seu: Endereço IPv4. . . . . . . .  . . . . . . . : 000.000.0.0

No seu componente Angular (leitura-qr.component.ts), ajuste a variável qrData para usar o IP da sua máquina, por exemplo:

http://localhost:4200/leitura-qr --> qrData = 'http://192.168.0.4:4200/leitura-qr';

Quando você rodar o ng serve, use o comando para aceitar conexões externas:
ng serve --host 0.0.0.0

Normal: localhost (Celular não funciona, somente local)
ng serve

#--------------Backend-------------#

Abra o arquivo settings.py do seu projeto Django e procure pela variável ALLOWED_HOSTS. Altere ou adicione assim:

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.0.4']
ou
ALLOWED_HOSTS = ['*']

Para aceitar conexões da rede local, seu servidor Django deve rodar assim:
python manage.py runserver 0.0.0.0:8000

http://192.168.0.4:8000/api -> pode testar no celular

