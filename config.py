import configparser
def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    token = config.get("Settings", "vk_group_token")
    admins = config.get("Settings", "admin_vk_id")

    admins = admins.replace(' ','').split(',')
    try:
        admins = [int(i) for i in admins] # перевод всех элементов в int
    except Exception:
        print('Введите числовые значения VK_ID админов!')
    return [token, admins]