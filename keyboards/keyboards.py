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
admin_menu_keyboard.row_width = 1
admin_menu_keyboard.add(duty_button,set_owner_manual_button,producer_button)
