import zipfile
import os
import json
from selenium.webdriver.common.by import By


def replace_variables_in_js(js_content: str, variables_dict: dict):
    for variable, value in variables_dict.items():
        js_content = js_content.replace('{{ ' + variable + ' }}', value)
    return js_content


def generate_proxy_auth_extension(
        proxy_host: str, proxy_port: str, proxy_user: str, proxy_pass: str,
        extension_file: str):
    """Generate a Chrome extension that modify proxy settings based on desired host, port, username and password.

    If you are using --headless in chromedriver, you must use --headless=new to support extensions in headless mode.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    manifest_json_path = os.path.join(current_dir, 'manifest.json')
    background_js_path = os.path.join(current_dir, 'background.js')
    with open(manifest_json_path, 'r', encoding='utf-8') as f:
        manifest_json = f.read()
    with open(background_js_path, 'r', encoding='utf-8') as f:
        background_js = f.read()

    variables_dict = {
        'proxy_host': proxy_host,
        'proxy_port': proxy_port,
        'proxy_user': proxy_user,
        'proxy_pass': proxy_pass
    }
    background_js = replace_variables_in_js(background_js, variables_dict)

    with zipfile.ZipFile(extension_file, 'w') as zp:
        zp.writestr('manifest.json', manifest_json)
        zp.writestr('background.js', background_js)


def get_my_ip(driver):
    origin_tab = driver.current_window_handle
    driver.execute_script("window.open('', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])

    driver.get('https://api.ipify.org/?format=json')

    ip_row = driver.find_element(By.XPATH, '//body').text
    ip = json.loads(ip_row)['ip']

    driver.close()
    driver.switch_to.window(origin_tab)

    return ip


def proxy_is_working(driver, host: str):
    ip = get_my_ip(driver)

    if ip == host:
        return True
    else:
        return False
