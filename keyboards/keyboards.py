from telebot import types


main_menu_keyboard = types.InlineKeyboardMarkup()
contacts_button = types.InlineKeyboardButton(text = "Контакты", callback_data = "contacts")
help_button = types.InlineKeyboardButton(text = "Помощь", callback_data = "help")
admin_button = types.InlineKeyboardButton(text = "Админка", callback_data = "admin_menu")

main_menu_keyboard.row_width = 2
main_menu_keyboard.add(contacts_button,help_button,admin_button)


admin_menu_keyboard = types.InlineKeyboardMarkup()
duty_button = types.InlineKeyboardButton(text = "Дежурю", callback_data = "duty")
set_owner_manual_button = types.InlineKeyboardButton(text = "Назначение на HPSM", callback_data = "set_owner_manual")
producer_button = types.InlineKeyboardButton(text = "Продюсер", callback_data = "producer")
notify_button = types.InlineKeyboardButton(text = "Показать уведомления", callback_data = "notify_get")
notify_set_active_button = types.InlineKeyboardButton(text = "Вкл/выкл уведомлений", callback_data = "notify_set_active")
admin_menu_keyboard.row_width = 1
admin_menu_keyboard.add(duty_button,set_owner_manual_button,producer_button,notify_button,notify_set_active_button)

document_keyboard_admin = types.InlineKeyboardMarkup()
document_keyboard_user = types.InlineKeyboardMarkup()
download_doc_dev = types.InlineKeyboardButton(text = "Скачать документ с Теста", callback_data = "download_doc_test")
download_json_dev = types.InlineKeyboardButton(text = "Скачать композицию с Теста", callback_data = "download_json_test")
audit_test = types.InlineKeyboardButton(text = "Аудит документа Тест", callback_data = "audit_test")
document_status_test = types.InlineKeyboardButton(text = "Статус документа с Тест", callback_data = "status_test")

download_doc_ppak = types.InlineKeyboardButton(text = "Скачать документ с ППАК", callback_data = "download_doc_ppak")
download_json_ppak = types.InlineKeyboardButton(text = "Скачать композицию с ППАК", callback_data = "download_json_ppak")
audit_ppak = types.InlineKeyboardButton(text = "Аудит документа ППАК", callback_data = "audit_ppak")
document_status_ppak = types.InlineKeyboardButton(text = "Статус документа ППАК", callback_data = "status_ppak")

document_keyboard_admin.row_width = 2
document_keyboard_user.row_width = 1

document_keyboard_user.add(download_doc_dev,download_json_dev,audit_test,document_status_test)
document_keyboard_admin.add(download_doc_dev,download_doc_ppak,download_json_dev,download_json_ppak,audit_test
                            ,audit_ppak,document_status_test,document_status_ppak)