from pywinauto import Application
from pywinauto import mouse
from pywinauto.keyboard import send_keys
from img_detection import *
import time
from random_word import RandomWords
import pyperclip
import psutil
from loguru import logger
from devtools import *


class TelegramApp:
    x, y = 100, 100
    width, height = 800, 600

    def __init__(self, exe_path, wait_network_loading=True, time_to_wait=60):
        self.app = Application().start(exe_path)
        self.app.wait_cpu_usage_lower(threshold=5)

        self.main_window = self.app.top_window()

        self.main_window.move_window(x=self.x, y=self.y, width=self.width, height=self.height, repaint=True)

        if wait_network_loading:
            time.sleep(0.2)
            if not wait_while_img_dissapear(self.main_window, 'templates\\telegram\\network_loading.png', 0.5, time_to_wait*2, 0.95):
                raise Exception(f'Telegram not loaded in {time_to_wait} sec')
            logger.info('Telegram loaded successfully!')


    def get_window_center_coords(self, window):
        rect = window.rectangle()
        x = rect.left
        y = rect.top
        width = rect.width()
        height = rect.height()

        x_center = int(x + width / 2)
        y_center = int(y + height / 2)

        return x_center, y_center

    
    def scroll_to_click(self, dist, window, template_path, delay, tries_count, threshold, click=True):
        x, y = self.get_window_center_coords(self.main_window)

        window.set_focus()

        time.sleep(0.2)
        mouse.move(coords=(x, y))
        time.sleep(0.2)

        for i in range(dist):
            if i % 5 == 0:
                if click:
                    if click_on_img(window, template_path, delay, tries_count, threshold):
                        return True
                else:
                    if get_img_coords(window, template_path, delay, tries_count, threshold):
                        return True
            send_keys('{DOWN}')
            time.sleep(0.01)
        return False


    def key_cycle(self, window, key, count, delay):
        window.set_focus()
        for i in range(count):
            send_keys(key)
            time.sleep(delay)


    def turn_on_webview_inspecting(self):
        click_on_img(self.main_window, 'templates\\telegram\\burger_menu.png', 0.5, 5, 0.7)
        click_on_img(self.main_window, 'templates\\telegram\\settings.png', 0.5, 5, 0.7)
        click_on_img(self.main_window, 'templates\\telegram\\advanced.png', 0.5, 5, 0.9)

        self.scroll_to_click(60, self.main_window, 'templates\\telegram\\exp_settings.png', 0, 1, 0.9)

        if self.scroll_to_click(50, self.main_window, 'templates\\telegram\\inspection.png', 0, 1, 0.9, click=False):
            if click_on_img(self.main_window, 'templates\\telegram\\inspection_off.png', 0.5, 5, 0.9):
                logger.info('Webview inspecction ON!')
            elif get_img_coords(self.main_window, 'templates\\telegram\\inspection_on.png', 0.5, 5, 0.9):
                logger.info('Webview inspecction already ON!')
            else:
                logger.info('Inspection not found!')

        self.key_cycle(self.main_window, '{ESC}', 4, 0.05)


    def enter_new_text(self, nickname, delay=0.2):
        time.sleep(delay)
        send_keys("^a")
        time.sleep(delay)
        send_keys("{BACKSPACE}")
        time.sleep(delay)
        send_keys(nickname)


    def set_nickname(self, nickname, delay=0.2, change_if_already_set=False):
        click_on_img(self.main_window, 'templates\\telegram\\burger_menu.png', 0.5, 5, 0.7)
        click_on_img(self.main_window, 'templates\\telegram\\settings.png', 0.5, 5, 0.7)
        click_on_img(self.main_window, 'templates\\telegram\\my_account.png', 0.5, 5, 0.9)
        click_on_img(self.main_window, 'templates\\telegram\\change_username.png', 0.5, 5, 0.9)

        if not change_if_already_set and not get_img_coords(self.main_window, 'templates\\telegram\\empty_username.png', 0.5, 5, 0.9):
            logger.info('Username already setted!')
            self.key_cycle(self.main_window, '{ESC}', 4, 0.05)
            return True

        self.enter_new_text(nickname, delay)
        time.sleep(delay * 3)

        if get_img_coords(self.main_window, 'templates\\telegram\\username_available.png', 0.5, 10, 0.9):
            if click_on_img(self.main_window, 'templates\\telegram\\save.png', 0.5, 5, 0.8):
                logger.info('Username successfully setted!')
                self.key_cycle(self.main_window, '{ESC}', 4, 0.05)
                return True
        
        raise Exception('Username do not setted!')
    

    def write_to_saved_messages(self, message, delay=0.2):
        time.sleep(delay)
        send_keys("^0")
        pyperclip.copy(message)
        time.sleep(delay)
        send_keys("^v")
        time.sleep(delay)
        send_keys("{ENTER}")

    def quit_telegram(self):
        self.main_window.set_focus()
        time.sleep(0.1)
        self.main_window.set_focus()
        time.sleep(0.3)
        send_keys('^q')
        logger.info("Telegram closed with ^q.")


    @staticmethod
    def get_random_word_with_length( min_length, max_length):
        r = RandomWords()
        while True:
            word = r.get_random_word()
            if min_length <= len(word) <= max_length:
                return word


    @staticmethod
    def get_nickname():
        word1 = TelegramApp.get_random_word_with_length(3,5)
        word2 = TelegramApp.get_random_word_with_length(3,5)
        nickname = f"{word1}{word2}"
        return nickname

    
    @staticmethod
    def stop_telegram_processes():
        for process in psutil.process_iter(['pid', 'name']):
            try:
                if 'Telegram' in process.info['name']:
                    p = psutil.Process(process.info['pid'])
                    p.terminate()
                    p.wait()
                    logger.warning(f"Telegram process - PID {process.info['pid']} was stopped.")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    
    @staticmethod
    def is_proxifier_running():
        for process in psutil.process_iter(['name']):
            if process.info['name'] == 'Proxifier.exe':
                return True
        return False
    

    @staticmethod
    def get_account_number_from_path(path):
        try:
            formatted_str = path[path.index('all_telegrams')+14:].strip()
            end_str = formatted_str[:formatted_str.index("\\")]
            return int(end_str)
        except:
            return None


class TelegramDogs(TelegramApp):
    def __init__(self, exe_path):
        super().__init__(exe_path)
        self.dogs_window = None


    def set_random_nicknames(self, tries_count=5, delay=0.2):
        for i in range(tries_count):
            if self.set_nickname(TelegramDogs.get_nickname(),delay):
                break

    
    def launch_dogs(self, link, sleep_before_launch=3, tries_count=30):
        time.sleep(2)
        old_windows = list(self.app.windows())

        for i in range(tries_count):
            self.write_to_saved_messages(link)
            time.sleep(sleep_before_launch)
            if click_on_img(self.main_window, 'templates\\dogs\\launch.png', 0.5, 2, 0.9):
                break

        for i in range(tries_count):
            if get_img_coords(self.main_window, 'templates\\dogs\\allow_msg.png', 0.5, 10, 0.9):
                click_on_img(self.main_window, 'templates\\dogs\\OK.png', 0.5, 5, 0.9)

            new_windows = list(self.app.windows())
            if len(new_windows) > len(old_windows):
                unique_windows = [w for w in new_windows if w not in old_windows]
                self.dogs_window = unique_windows[0]
                if self.dogs_window:
                    logger.info('Dogs window successfully launched!')
                    return True
            time.sleep(1)

        raise Exception('Dogs window do not launched.')
    

    def work_with_dogs(self):
        if not click_on_img(self.dogs_window, 'templates\\dogs\\start_dogs.png', 0.5, 60, 0.9):
            raise Exception('First button on Dogs not found!')
        time.sleep(8)
        click_on_img(self.dogs_window, 'templates\\dogs\\continue_blue.png', 0.5, 40, 0.9)
        click_on_img(self.dogs_window, 'templates\\dogs\\continue_white.png', 0.5, 40, 0.9)
        if not click_on_img(self.dogs_window, 'templates\\dogs\\continue_white.png', 0.5, 40, 0.9):
            raise Exception('Last button on Dogs not found!')
        logger.info('Dogs successfully claimed!')


class TelegramAppHOT(TelegramApp):
    def __init__(self, exe_path):
        super().__init__(exe_path)
        self.hot_window = None
        self.devtools = None


    def launch_hot(self, link, sleep_before_launch=3, tries_count=30):
        time.sleep(2)
        old_windows = list(self.app.windows())

        for i in range(tries_count):
            self.write_to_saved_messages(link)
            time.sleep(sleep_before_launch)
            if click_on_img(self.main_window, 'templates\\hot\\launch.png', 0.5, 2, 0.9):
                break

        for i in range(tries_count):
            if get_img_coords(self.main_window, 'templates\\hot\\allow_msg.png', 0.5, 10, 0.9):
                click_on_img(self.main_window, 'templates\\hot\\OK.png', 0.5, 5, 0.9)

            new_windows = list(self.app.windows())
            if len(new_windows) > len(old_windows):
                unique_windows = [w for w in new_windows if w not in old_windows]
                self.hot_window = unique_windows[0]
                if self.hot_window:
                    logger.info('HOT window successfully launched!')
                    return True
            time.sleep(1)

        raise Exception('HOT window do not launched.')


    def open_dev_tools(self, wait):         #do not work
        if self.hot_window is None:
            print('No HOT window!')
            return 0

        click_on_img(self.hot_window, 'templates\\hot\\main_page_arrow.png', 0.5, 5, 0.9)   #mb hot_window problem
        time.sleep(0.5)
        send_keys("{F12}")
        time.sleep(1)

        self.devtools = DevTools()
        

    def collect_data(self):
        data = self.devtools.prepare_and_get_tgWebAppData()
        print(data)






















    @staticmethod
    def test_devtools():
        devtools = DevTools()

        app_btn_control = devtools.get_Application_btn_control()
        app_btn_control.click_input()

        herewallet_control = devtools.get_session_storage_herewallet_control()
        if not herewallet_control:
            session_storage_control = devtools.get_session_storage_control()
            session_storage_control.double_click_input()

        herewallet_control = devtools.get_session_storage_herewallet_control()
        herewallet_control.click_input()

        webAppData = devtools.get__tgWebAppData()
        print(webAppData)


    @staticmethod
    def get_control_data(window):
        children = window.children()
        print()
        for control in children:
            # Отримуємо дані про контрол
            control_text = control.window_text()
            control_rect = control.rectangle()
            control_width = control_rect.width()
            control_height = control_rect.height()
            control_class = control.class_name()
            print(f"Текст контролу: {control_text}")
            print(f"Ім'я класу контролу: {control_class}")
            print(f"Розміри контролу: {control_width}x{control_height}")
            print()


    @staticmethod
    def print_window_info(window):
        window_title = window.window_text()
        window_class = window.class_name()
        window_rect = window.rectangle()
        window_position = (window_rect.left, window_rect.top)
        window_size = (window_rect.width(), window_rect.height())

        print(f"Заголовок вікна: {window_title}")
        print(f"Клас вікна: {window_class}")
        print(f"Позиція вікна: {window_position}")
        print(f"Розмір вікна: {window_size}")


class TelegramAppBlum(TelegramApp):
    def __init__(self, exe_path):
        super().__init__(exe_path)
        self.blum_window = None
        self.devtools = None


    def launch_blum(self, link, sleep_before_launch=3, tries_count=30):
        time.sleep(2)
        old_windows = list(self.app.windows())

        for i in range(tries_count):
            self.write_to_saved_messages(link)
            time.sleep(sleep_before_launch)
            if click_on_img(self.main_window, 'templates\\blum\\launch.png', 0.5, 2, 0.9):
                break

        for i in range(tries_count):
            if get_img_coords(self.main_window, 'templates\\blum\\allow_msg.png', 0.5, 10, 0.9):
                click_on_img(self.main_window, 'templates\\blum\\OK.png', 0.5, 5, 0.9)

            new_windows = list(self.app.windows())
            if len(new_windows) > len(old_windows):
                unique_windows = [w for w in new_windows if w not in old_windows]
                self.blum_window = unique_windows[0]
                if self.blum_window:
                    logger.info('Blum window successfully launched!')
                    return True
            time.sleep(1)

        raise Exception('Blum window do not launched.')
    

    def manage_account_and_open_devtools(self):
        click_on_img(self.blum_window, 'templates\\blum\\continue.png', 0.5, 10, 0.9)
        res = find_first_image([
            [self.blum_window, 'templates\\blum\\create_account.png', 0.5, 5, 0.9],
            [self.blum_window, 'templates\\blum\\start_farming.png', 0.5, 5, 0.9],
            [self.blum_window, 'templates\\blum\\currently_farming.png', 0.5, 5, 0.6],
            [self.blum_window, 'templates\\blum\\claim.png', 0.5, 5, 0.6],
            [self.blum_window, 'templates\\blum\\continue.png', 0.5, 5, 0.6],
        ])
        if 'continue' in res:
            click_on_img(self.blum_window, 'templates\\blum\\continue.png', 0.5, 5, 0.6)
            res = find_first_image([
                [self.blum_window, 'templates\\blum\\create_account.png', 0.5, 5, 0.9],
                [self.blum_window, 'templates\\blum\\start_farming.png', 0.5, 5, 0.9],
                [self.blum_window, 'templates\\blum\\currently_farming.png', 0.5, 5, 0.6],
                [self.blum_window, 'templates\\blum\\claim.png', 0.5, 5, 0.6],
            ])
        if 'currently_farming' in res:
            logger.info('Account is currently farming!')
        elif 'start_farming' in res:
            logger.info('Account start farming!')
        elif 'claim' in res:
            logger.info('Account claim earnings!')
            click_on_img(self.blum_window, 'templates\\blum\\claim.png', 0.5, 5, 0.6)
            click_on_img(self.blum_window, 'templates\\blum\\start_farming.png', 0.5, 10, 0.6)
        elif 'create_account' in res:
            logger.info('Account start to create!')
            self.create_account()
        else: 
            raise Exception("Account status not found!")

        if click_on_img(self.blum_window, 'templates\\blum\\logo.png', 0.5, 5, 0.7):
            time.sleep(0.3)
            send_keys("{F12}")
            time.sleep(1)
            self.devtools = DevTools()
        else:
            raise Exception('Blum logo not found!')


    def create_account(self):                                           #not implemented
        click_on_img(self.blum_window, 'templates\\blum\\create_account.png', 0.5, 10, 0.9)
        if get_img_coords(self.blum_window, 'templates\\blum\\blum_nickname_available.png', 0.5, 20, 0.8):
            click_on_img(self.blum_window, 'templates\\blum\\continue.png', 0.5, 10, 0.9)
        time.sleep(13)
        click_on_img(self.blum_window, 'templates\\blum\\continue.png', 0.5, 50, 0.9)
        click_on_img(self.blum_window, 'templates\\blum\\continue.png', 0.5, 20, 0.9)
        click_on_img(self.blum_window, 'templates\\blum\\start_farming.png', 0.5, 5, 0.6)

        logger.info('Account successfully created!')
        
        

    def collect_data(self, proxy=''):
        session_data = self.devtools.prepare_and_get_tgWebAppData()
        local_data = self.devtools.prepare_and_get_localdata()
        end_data = {
            'proxy': proxy,
            'Token':'',
            'distinct_id': local_data['distinct_id'],
            'device_id': local_data['device_id'],
            'user_id': local_data['user_id'],
            'tok': 'a663ec3881444e996e51121d5a98ce4d',
            'queid': session_data,
        }

        return end_data
    

    def append_to_json_file(self, file_path, new_dict):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = []  # Якщо файл не існує, створити новий список
        except json.JSONDecodeError:
            data = []  # Якщо файл пустий або пошкоджений, створити новий список

        # Переконатися, що дані є списком
        if not isinstance(data, list):
            data = []

        # Додавання нового словника
        data.append(new_dict)

        # Запис оновлених даних назад у файл
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)


    @staticmethod
    def test_devtools():
        devtools = DevTools()
        
        session_data = devtools.prepare_and_get_tgWebAppData()
        local_data = devtools.prepare_and_get_localdata()
        end_data = {
            'proxy':'---',
            'Token':'',
            'distinct_id': local_data['distinct_id'],
            'device_id': local_data['device_id'],
            'user_id': local_data['user_id'],
            'tok': 'a663ec3881444e996e51121d5a98ce4d',
            'queid': session_data,
        }

        for i,j in end_data.items():
            print(f"{i}: {j}")
