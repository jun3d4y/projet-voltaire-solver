from seleniumwire import webdriver

from bs4 import BeautifulSoup
import difflib
import os

def print_logo() :
    os.system('color')
    os.system('cls')
    print("""\n\033[1;32;40m
██╗   ██╗ ██████╗ ██╗  ████████╗ █████╗ ██╗██████╗ ███████╗
██║   ██║██╔═══██╗██║  ╚══██╔══╝██╔══██╗██║██╔══██╗██╔════╝
██║   ██║██║   ██║██║     ██║   ███████║██║██████╔╝█████╗
╚██╗ ██╔╝██║   ██║██║     ██║   ██╔══██║██║██╔══██╗██╔══╝
 ╚████╔╝ ╚██████╔╝███████╗██║   ██║  ██║██║██║  ██║███████╗
  ╚═══╝   ╚═════╝ ╚══════╝╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚══════╝
████████████████████████████████████████████████████████████╗
╚═══════════════════════════════════════════════════════════╝

    ██████╗ ██╗   ██╗███████╗████████╗███████╗██████╗
    ██╔══██╗██║   ██║██╔════╝╚══██╔══╝██╔════╝██╔══██╗
    ██████╔╝██║   ██║███████╗   ██║   █████╗  ██████╔╝
    ██╔══██╗██║   ██║╚════██║   ██║   ██╔══╝  ██╔══██╗
    ██████╔╝╚██████╔╝███████║   ██║   ███████╗██║  ██║
    ╚═════╝  ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
   ████████████████████████████████████████████████████╗
   ╚═══════════════════════════════════════════════════╝

    \033[1;37;40m
                                  [\033[1;31;40mdevelopped by JuneDay\033[1;37;40m]\n

 """)

class Driver :

    def __init__(self, path):
        #préparation du webdriver
        self.last_ones = []
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(executable_path=path, options=chrome_options)
        self.driver.implicitly_wait(10)
        base_url = "https://www.projet-voltaire.fr/"
        self.driver.get(base_url)

    def find_string(self):
        #récupération de la phrase à vérifier
        source = self.driver.page_source
        soup = BeautifulSoup(source, features="html.parser")
        sentence_div = soup.find('div', {'class':'sentence'})
        if sentence_div is not None :
            sentence = ''
            for word in sentence_div.find_all('span', class_='pointAndClickSpan') :
                sentence += word.text
            return sentence
        else : return 'None'

    def get_data(self):
        #récupération des réponses
        longueur = 0
        for request in self.driver.requests:
            if request.response and request.url == 'https://www.projet-voltaire.fr/services-pjv/gwt/WolLearningContentWebService':
                if len(request.response.body)>longueur and request.response.body not in self.last_ones:
                    content = request.response.body
                    longueur = len(request.response.body)
        self.last_ones.append(content)

        #parsing des réponses
        content = str(content)
        content = content.replace('//OK', '')
        content = content.strip('][')
        content = content.replace('],0,7]', '')
        record = False
        to_process = ''
        for char in content :
            if char == '[' :
                record = True
            if record :
                to_process += char
        to_process = to_process.split('","')
        responses = []
        for line in to_process :
            if "\\x3E" in line :
                responses.append(line.replace(']', '').replace('"', '').replace('\\\\xA0', '').replace('\\\\x3CB\\\\x3E', '<').replace('\\\\x3C/B\\\\x3E', '>').replace('\\\\x27', '\''))
        return responses

    def is_homepage(self) :
        #vérification si la page courante est la page de choix de test
        source = self.driver.page_source
        soup = BeautifulSoup(source, features="html.parser")
        title = soup.find('div', {'class':'activity-selector-title'})
        if title is not None :
            return True
        else : return False

    def is_audio(self) :
        #vérification si la question est audio
        source = self.driver.page_source
        soup = BeautifulSoup(source, features="html.parser")
        audio = soup.find('div', {'class':'sentenceAudioReader'})
        if audio is not None :
            return True
        else : return False





print_logo()
os.system('color')
driver = Driver(f'webdriver/chromedriver.exe')
input('[  \033[1;32;40mSETUP\033[1;37;40m  ] Connectez-vous, puis appuyez sur entrer ...')
input('[  \033[1;32;40mSETUP\033[1;37;40m  ] Choisissez un test, puis appuyez sur entrer ...')
reponses = driver.get_data()
while True :
    print_logo()
    if driver.is_audio() :
        print('[  \033[1;32;40mAUDIO\033[1;37;40m  ] C\'est une question audio, faites-la vous-même !')
        while driver.is_audio():
            pass
    else :
        if driver.is_homepage() :
            input('[  \033[1;32;40mSETUP\033[1;37;40m  ] Choisissez un test, puis appuyez sur entrer ...')
            reponses = driver.get_data()
        phrase = driver.find_string()
        print(f'[  \033[1;32;40mSEARCHING\033[1;37;40m  ] {phrase}')
        old_phrase = phrase
        possibilites = difflib.get_close_matches(phrase, reponses)
        if len(possibilites) != 0:
            toPrint = '[  \033[1;31;40mERROR\033[1;37;40m  ] ' + possibilites[0].replace('<', '\033[1;32;40m').replace('>', '\033[1;37;40m')
            print('', toPrint, '\n')
        else:
            print('[  \033[1;32;40mOK\033[1;37;40m  ] Il n\'y a pas de faute !')
        if phrase != 'None' :
            while phrase == old_phrase :
                phrase = driver.find_string()
