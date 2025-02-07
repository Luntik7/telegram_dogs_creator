from linecache import cache
import time
from telegram import TelegramApp,TelegramAppHOT, TelegramDogs, TelegramAppBlum
from loguru import logger
import random

TRIES_COUNT = 3
CHECK_WEBVIEW_INSPECTIOIN = False
counter = 0

def main_blum(path, ref_link):
    global counter
    telegram_app = TelegramAppBlum(path)
    if CHECK_WEBVIEW_INSPECTIOIN:
        telegram_app.turn_on_webview_inspecting()
    telegram_app.launch_blum(ref_link)
    telegram_app.manage_account_and_open_devtools()
    data = telegram_app.collect_data()


    with open('proxies.txt', 'r', encoding='utf-8') as fileobj:
        proxies_list = fileobj.readlines()
    number = TelegramAppBlum.get_account_number_from_path(path)
    if number:
        proxy = proxies_list[number].strip()
    else:
        proxy = proxies_list[counter].strip()
        
    counter = (counter + 1)

    data['proxy'] = proxy
    telegram_app.append_to_json_file('blum.json', data)

        

    time.sleep(0.3)
    telegram_app.quit_telegram()
    time.sleep(1)


def main_hot():
    if TelegramAppHOT.is_proxifier_running():
        TelegramAppHOT.stop_telegram_processes()
        telegram_app = TelegramAppHOT('D:\\DATA\\Python\\Tdata_unpack\\all_telegrams\\172\\+6283176166127\\Telegram.exe')
        if CHECK_WEBVIEW_INSPECTIOIN:
            telegram_app.turn_on_webview_inspecting()
        telegram_app.launch_hot('https://t.me/herewalletbot/app')
        telegram_app.open_dev_tools(10)
        telegram_app.collect_data()
        
        # TelegramAppHOT.test_devtools()


def main_dogs(path, ref_link):
    telegramDogs = TelegramDogs(path)
    telegramDogs.set_random_nicknames(10)
    telegramDogs.launch_dogs(ref_link)
    telegramDogs.work_with_dogs()
    time.sleep(0.3)
    telegramDogs.quit_telegram()
    time.sleep(1)


def main():
    logger.add("file.log", level="DEBUG")
    
    with open('all_refs.txt', 'r', encoding='utf-8') as fileobj:
        ref_links = fileobj.readlines()

    with open('all_pathes.txt', 'r', encoding='utf-8') as fileobj:
        pathes_list = fileobj.readlines()

    for path in pathes_list:
        for i in range(TRIES_COUNT):
            try:
                if path.find('all_telegrams') != -1:
                    short_path = path[path.index('all_telegrams')+13:].strip()
                else:
                    short_path = path[-40:]

                if TelegramApp.is_proxifier_running():
                    TelegramApp.stop_telegram_processes()
                    time.sleep(1)
                    logger.info(f"Start account ...{short_path}")

                    ref_link = random.choice(ref_links).strip()
                    logger.info(f"Account referal: {ref_link[ref_link.index('?'):]}")

                    main_blum(path.strip(), ref_link)                                                    #sub main
                    break
                else:
                    logger.warning('Launch proxyfier firstly')
                    return 0
            except Exception as e:
                logger.error(f'Error: {str(e).strip()}')
                logger.warning(f"TRY {i+1}/{TRIES_COUNT}")
                if i+1 < TRIES_COUNT:
                    continue
                else:
                    with open('bad_accounts.txt', 'a', encoding='utf-8') as fileobj:
                        fileobj.write(path + '\n')
            finally:
                logger.info(f"Finish account ...{short_path}\n")
    input()


if __name__ == '__main__':
    main()