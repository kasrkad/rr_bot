from telebot import types

# Клавиатура для основного меню
main_menu_keyboard = types.InlineKeyboardMarkup()
contacts_button = types.InlineKeyboardButton(
    text="Контакты", callback_data="contacts")
help_button = types.InlineKeyboardButton(text="Помощь", callback_data="help")
admin_button = types.InlineKeyboardButton(
    text="Админка", callback_data="admin_menu")

main_menu_keyboard.row_width = 2
main_menu_keyboard.add(contacts_button, help_button, admin_button)

# Клавиатура для админского меню
admin_menu_keyboard = types.InlineKeyboardMarkup()
duty_button = types.InlineKeyboardButton(text="Дежурю", callback_data="duty")
set_owner_manual_button = types.InlineKeyboardButton(
    text="Назначение на HPSM", callback_data="set_owner_manual")
set_duty_manual_button = types.InlineKeyboardButton(
    text="Назначение на дежурство", callback_data="set_duty_manual")
producer_button = types.InlineKeyboardButton(
    text="Продюсер", callback_data="producer")
notify_button = types.InlineKeyboardButton(
    text="Показать уведомления", callback_data="notify_get")
accept_sending = types.InlineKeyboardButton(
    text="Отправить скриншот", callback_data="screenshot")
notify_set_active_button = types.InlineKeyboardButton(
    text="Вкл/выкл уведомлений", callback_data="notify_set_active")
get_status_button = types.InlineKeyboardButton(
    text="Текущий статус HPSM", callback_data="status_hpsm")
show_hpsm_panel = types.InlineKeyboardButton(
    text="HPSM меню", callback_data="show_hpsm_panel")
admin_menu_keyboard.row_width = 2
admin_menu_keyboard.add(duty_button, accept_sending,
                        set_owner_manual_button, set_duty_manual_button,
                        notify_button, notify_set_active_button,
                        get_status_button, producer_button, show_hpsm_panel)


# Клавиатура для работы с HPSM CHECKER
hpsm_checker_keyboard = types.InlineKeyboardMarkup()
deactivate_hpsm_notifi = types.InlineKeyboardButton(
    text="Выключить уведомления от hpsm", callback_data="hpsm_notify_off")
activate_hpsm_notifi = types.InlineKeyboardButton(
    text="Включить уведомления от hpsm", callback_data="hpsm_notify_on")
status_hpsm_notifi = types.InlineKeyboardButton(
    text="Статус уведомлений от hpsm", callback_data="hpsm_notify_status")
hpsm_checker_keyboard.row_width = 2
hpsm_checker_keyboard.add(activate_hpsm_notifi,
                          deactivate_hpsm_notifi, status_hpsm_notifi)

# Клавиатуры для работы с документами
document_keyboard_admin = types.InlineKeyboardMarkup()  # Админская
document_keyboard_user = types.InlineKeyboardMarkup()  # Юзерская
download_doc_dev = types.InlineKeyboardButton(
    text="Скачать документ с Теста", callback_data="download_doc_test")
download_json_dev = types.InlineKeyboardButton(
    text="Скачать композицию с Теста", callback_data="download_json_test")
audit_test = types.InlineKeyboardButton(
    text="Аудит документа Тест", callback_data="audit_test")
document_status_test = types.InlineKeyboardButton(
    text="Статус документа с Тест", callback_data="status_test")

download_doc_ppak = types.InlineKeyboardButton(
    text="Скачать документ с ППАК", callback_data="download_doc_ppak")
download_json_ppak = types.InlineKeyboardButton(
    text="Скачать композицию с ППАК", callback_data="download_json_ppak")
audit_ppak = types.InlineKeyboardButton(
    text="Аудит документа ППАК", callback_data="audit_ppak")
document_status_ppak = types.InlineKeyboardButton(
    text="Статус документа ППАК", callback_data="status_ppak")

document_keyboard_admin.row_width = 2
document_keyboard_user.row_width = 1

document_keyboard_user.add(
    download_doc_dev, download_json_dev, audit_test, document_status_test)
document_keyboard_admin.add(download_doc_dev, download_doc_ppak,
                            download_json_dev,
                            download_json_ppak, audit_test, audit_ppak,
                            document_status_test, document_status_ppak)
