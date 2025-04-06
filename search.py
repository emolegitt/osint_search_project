import requests
import sqlite3
from PyQt5.QtCore import QThread, pyqtSignal
import re
from bs4 import BeautifulSoup
from torpy.http.requests import tor_requests_session
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from concurrent.futures import ThreadPoolExecutor

class SearchWorker(QThread):
    result_signal = pyqtSignal(list)
    progress_signal = pyqtSignal(int)

    def __init__(self, nickname, email, phone, ip, use_tor=False, tor_proxy="socks5h://127.0.0.1:9050", db_path=None, txt_path=None):
        super().__init__()
        self.nickname = nickname
        self.email = email
        self.phone = phone
        self.ip = ip
        self.use_tor = use_tor
        self.tor_proxy = tor_proxy
        self.db_path = db_path
        self.txt_path = txt_path
        self.txt_data = []

    def load_txt_data(self):
        if not self.txt_path:
            return
        try:
            with open(self.txt_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("telegram_user"):
                        parts = line.split(",")
                        if len(parts) == 15:
                            self.txt_data.append(parts)
        except Exception as e:
            self.txt_data = []
            self.result_signal.emit([f"Ошибка загрузки TXT базы данных: {str(e)}"])

    def run(self):
        results = []
        progress = 0
        
        if self.use_tor:
            try:
                session = tor_requests_session(proxy=self.tor_proxy)
            except Exception as e:
                results.append(f"Tor: Ошибка подключения - {str(e)}")
                self.result_signal.emit(results)
                return
        else:
            session = requests.Session()

        def search_x(nick):
            try:
                url = f"https://api.twitter.com/2/users/by/username/{nick}"
                return f"X: Профиль - https://twitter.com/{nick}"
            except:
                return "X: Ошибка поиска"
            finally:
                nonlocal progress
                progress += 15
                self.progress_signal.emit(progress)

        def search_vk(nick):
            try:
                url = f"https://vk.com/{nick}"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                response = session.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = soup.title.string if soup.title else "No title"
                    if "404" in title or "Not Found" in title:
                        return f"VK: Профиль {nick} не найден"
                    return f"VK: Профиль найден - {url} ({title})"
                elif response.status_code == 404:
                    return f"VK: Профиль {nick} не найден"
                else:
                    return f"VK: Ошибка {response.status_code}"
            except requests.exceptions.Timeout:
                return "VK: Таймаут при запросе"
            except requests.exceptions.RequestException as e:
                return f"VK: Ошибка сети - {str(e)}"
            finally:
                nonlocal progress
                progress += 15
                self.progress_signal.emit(progress)

        def search_instagram(nick):
            try:
                options = webdriver.ChromeOptions()
                options.add_argument("--headless")
                driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
                url = f"https://instagram.com/{nick}"
                driver.get(url)
                time.sleep(3)
                if "Page Not Found" in driver.title:
                    return f"Instagram: Профиль {nick} не найден"
                try:
                    username = driver.find_element(By.TAG_NAME, "h2").text
                    return f"Instagram: Профиль найден - {url} (Имя: {username})"
                except:
                    return f"Instagram: Профиль {nick} не найден или доступ ограничен"
            except Exception as e:
                return f"Instagram: Ошибка парсинга - {str(e)}"
            finally:
                driver.quit()
                nonlocal progress
                progress += 15
                self.progress_signal.emit(progress)

        def search_telegram(nick):
            nonlocal progress
            progress += 15
            self.progress_signal.emit(progress)
            return f"Telegram: @{nick} (API проверки в разработке)"

        def check_email_leak(email):
            try:
                url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
                headers = {"User-Agent": "OSINT-App"}
                response = session.get(url, headers=headers, timeout=5)
                if response.status_code == 200:
                    breaches = response.json()
                    return f"Email {email} утёк в: {', '.join([b['Name'] for b in breaches])}"
                return f"Email {email} не найден в утечках"
            except:
                return "Ошибка проверки email"
            finally:
                nonlocal progress
                progress += 15
                self.progress_signal.emit(progress)

        def search_phone(phone):
            if re.match(r'^\+?\d{10,12}$', phone):
                result = f"Телефон {phone}: Формат верный, поиск по базам в разработке"
            else:
                result = f"Телефон {phone}: Неверный формат"
            nonlocal progress
            progress += 15
            self.progress_signal.emit(progress)
            return result

        def search_darknet(nick):
            if not self.use_tor:
                return "Darknet: Для поиска включите Tor в настройках"
            try:
                darknet_url = "http://example.onion"
                response = session.get(darknet_url, timeout=10)
                if response.status_code == 200:
                    return f"Darknet: Найдено на {darknet_url} (результаты: {response.text[:100]}...)"
                return "Darknet: Ничего не найдено"
            except Exception as e:
                return f"Darknet: Ошибка поиска - {str(e)}"
            finally:
                nonlocal progress
                progress += 15
                self.progress_signal.emit(progress)

        def search_ip(ip):
            try:
                if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                    return f"IP {ip}: Неверный формат"
                response = session.get(f"http://ip-api.com/json/{ip}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data["status"] == "success":
                        return (f"IP {ip}: Страна - {data['country']}, "
                               f"Город - {data['city']}, "
                               f"ISP - {data['isp']}")
                    return f"IP {ip}: Не удалось получить информацию"
                return f"IP {ip}: Ошибка запроса"
            except:
                return f"IP {ip}: Ошибка поиска"
            finally:
                nonlocal progress
                progress += 15
                self.progress_signal.emit(progress)

        def search_in_database(nickname, email, phone, ip):
            if not self.db_path:
                return "SQLite база данных не подключена"

            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                query = """
                    SELECT * FROM user_data 
                    WHERE telegram_user LIKE ? OR instagram_user LIKE ? OR twitter_user LIKE ? OR facebook_user LIKE ? OR vk_id LIKE ?
                    OR telegram_phone LIKE ? OR instagram_phone LIKE ? OR twitter_phone LIKE ? OR facebook_phone LIKE ? OR vk_phone LIKE ?
                """
                params = (
                    f"%{nickname}%", f"%{nickname}%", f"%{nickname}%", f"%{nickname}%", f"%{nickname}%",
                    f"%{phone}%", f"%{phone}%", f"%{phone}%", f"%{phone}%", f"%{phone}%"
                )
                cursor.execute(query, params)
                rows = cursor.fetchall()

                if not rows:
                    return "Данные в SQLite базе не найдены"

                result = "Найдено в SQLite базе данных:\n"
                for row in rows:
                    result += (
                        f"Telegram User: {row[1]}, Telegram ID: {row[2]}, Telegram Phone: {row[3]}\n"
                        f"Instagram User: {row[4]}, Instagram Phone: {row[5]}, Instagram Password: {row[6]}\n"
                        f"VK ID: {row[7]}, VK Phone: {row[8]}, VK Password: {row[9]}\n"
                        f"Twitter User: {row[10]}, Twitter Phone: {row[11]}, Twitter Password: {row[12]}\n"
                        f"Facebook User: {row[13]}, Facebook Phone: {row[14]}, Facebook Password: {row[15]}\n"
                        "----------------------------------------\n"
                    )
                return result
            except Exception as e:
                return f"Ошибка поиска в SQLite базе данных: {str(e)}"
            finally:
                conn.close()
                nonlocal progress
                progress += 15
                self.progress_signal.emit(progress)

        def search_in_txt(nickname, email, phone, ip):
            if not self.txt_path:
                return "TXT база данных не подключена"

            self.load_txt_data()
            if not self.txt_data:
                return "Данные в TXT базе не найдены или файл пуст"

            result = "Найдено в TXT базе данных:\n"
            found = False
            for row in self.txt_data:
                telegram_user, telegram_id, telegram_phone, instagram_user, instagram_phone, instagram_password, \
                vk_id, vk_phone, vk_password, twitter_user, twitter_phone, twitter_password, \
                facebook_user, facebook_phone, facebook_password = row

                if (nickname and (nickname.lower() in telegram_user.lower() or
                                 nickname.lower() in instagram_user.lower() or
                                 nickname.lower() in twitter_user.lower() or
                                 nickname.lower() in facebook_user.lower() or
                                 nickname.lower() in vk_id.lower())) or \
                   (phone and (phone in telegram_phone or
                               phone in instagram_phone or
                               phone in twitter_phone or
                               phone in facebook_phone or
                               phone in vk_phone)):
                    found = True
                    result += (
                        f"Telegram User: {telegram_user}, Telegram ID: {telegram_id}, Telegram Phone: {telegram_phone}\n"
                        f"Instagram User: {instagram_user}, Instagram Phone: {instagram_phone}, Instagram Password: {instagram_password}\n"
                        f"VK ID: {vk_id}, VK Phone: {vk_phone}, VK Password: {vk_password}\n"
                        f"Twitter User: {twitter_user}, Twitter Phone: {twitter_phone}, Twitter Password: {twitter_password}\n"
                        f"Facebook User: {facebook_user}, Facebook Phone: {facebook_phone}, Facebook Password: {facebook_password}\n"
                        "----------------------------------------\n"
                    )
            if not found:
                return "Данные в TXT базе не найдены"
            return result

        # Параллельный поиск
        if self.nickname:
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(search_x, self.nickname),
                    executor.submit(search_vk, self.nickname),
                    executor.submit(search_instagram, self.nickname),
                    executor.submit(search_telegram, self.nickname),
                    executor.submit(search_darknet, self.nickname),
                    executor.submit(search_in_database, self.nickname, self.email, self.phone, self.ip),
                    executor.submit(search_in_txt, self.nickname, self.email, self.phone, self.ip)
                ]
                for future in futures:
                    results.append(future.result())
        if self.email:
            results.append(check_email_leak(self.email))
        if self.phone:
            results.append(search_phone(self.phone))
        if self.ip:
            results.append(search_ip(self.ip))

        self.result_signal.emit(results)