import telebot
from telebot import types


token = 'TOKEN'
bot = telebot.TeleBot(token)

all_users = set()
id_local_admin = name_local_admin = None
general_message_id = 'message_id главного админа'
local_admin = [[general_message_id, 'главный админ', []]]
name_chanel = 'название вашего телеграмм канала'
chanel_chat_id = 'chat_id вашего тг чата (отрицательное число)'
block_users = {}

try:
    @bot.message_handler(commands=["start"])
    def start(message):
        global all_users
        all_users.add(message.from_user.id)
        bot.send_message(message.chat.id, f'Отправте сообщение')


    @bot.message_handler(commands=["up_admin"])
    def new_local_admin(message):
        global id_local_admin, name_local_admin, all_users

        all_users.add(message.from_user.id)

        flag_admin = False
        id_local_admin = str(message.from_user.id)
        name_local_admin = message.from_user.username

        for i in range(len(local_admin)):
            if str(id_local_admin) == local_admin[i][0]:
                flag_admin = True

        if not flag_admin:
            bot.send_message(id_local_admin, f'Мы напишем главному админу, что вы хотите быть модератором')

            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton('✅', callback_data='yes_admin')
            btn2 = types.InlineKeyboardButton('❌', callback_data='not_admin')
            markup.row(btn1, btn2)

            bot.send_message(general_message_id, f'Человек с id: {id_local_admin} и под именем:'
                                                 f' {name_local_admin} хочет стать модератором', reply_markup=markup)
        else:
            bot.send_message(id_local_admin, f'Вы уже являетесь модератором')
            id_local_admin = name_local_admin = None


    @bot.message_handler(commands=["delete"])
    def delete_loc_admin(message):
        global local_admin, general_message_id
        if str(message.from_user.id) == general_message_id:
            if len(local_admin) != 0:
                total_delete_adm(message)
            else:
                bot.send_message(general_message_id, f'У вас нет модераторов')
        else:
            bot.send_message(message.chat.id, f'у вас нет доступа к этой функции')


    def total_delete_adm(message):
        global local_admin, general_message_id
        text = message.text.lower()[7:].strip().replace(' ', '')
        flag_f = False
        for i in range(len(local_admin)):
            str_i = str(i + 1)
            if str_i == text:
                if str(local_admin[int(text) - 1][0]) != general_message_id:
                    del local_admin[int(text) - 1]
                    flag_f = True
                    break
                else:
                    bot.send_message(message.chat.id, f"Невозможно удалить главного админа")
                    return None
        if not flag_f:
            bot.send_message(general_message_id, f'Такого модератора не существует')
        else:
            bot.send_message(general_message_id, f'Модератор удалён')


    @bot.message_handler(commands=["send"])
    def send_mess(message):
        global all_users
        delete_users = []
        if message.from_user.id != general_message_id:
            bot.send_message(message.chat.id, 'У вас нет доступа к этой функции')

        message_text = ''
        type_message = message.content_type
        if type_message == 'text':
            message_text = message.text.strip()[5:]
        if type_message == 'photo':
            message_text = message.caption.strip()[5:]

        for el in all_users:
            try:
                if type_message == 'text':
                    bot.send_message(el, message_text)
                if type_message == 'photo':
                    file_id = message.photo[-1].file_id
                    bot.send_photo(el, file_id, caption=message_text)
            except Exception as ex:
                delete_users.append(el)
                print(ex)

        for el in delete_users:
            all_users.discard(el)


    @bot.message_handler(commands=["admin"])
    def list_adm(message):
        global local_admin, all_users

        if str(message.from_user.id) != general_message_id:
            bot.send_message(message.chat.id, 'У вас нет доступа к этой функции')

        all_users.add(message.from_user.id)

        if len(local_admin) != 0:
            list_loc_adm = ''
            for i in range(len(local_admin)):
                list_loc_adm += f"№ {i + 1} name: {local_admin[i][1]}\n"
            bot.send_message(general_message_id, f'{list_loc_adm}')


    @bot.message_handler(commands=["block_lst"])
    def block_user(message):
        global block_users, general_message_id

        block_inf = 'Заблокированные пользователи:\n'

        tuple_block = tuple(block_users.items())
        for i in range(len(tuple_block)):
            block_inf += f'username: {tuple_block[i][1]}, message id: {tuple_block[i][0]}\n'

        bot.send_message(general_message_id, block_inf)


    @bot.message_handler(commands=["unblock"])
    def unblock(message):
        global block_users, general_message_id, chanel_chat_id

        if message.from_user.id != general_message_id:
            bot.send_message(message.chat.id, 'У вас не доступа к этой функции')
            return None

        if message.content_type == 'text':
            user = message.text.strip()[8:]
            unblock_user_id = ''
            tuple_block = tuple(block_users.items())

            for i in range(len(tuple_block)):
                if tuple_block[i][1] == user:
                    unblock_user_id = tuple_block[i][1]

            if unblock_user_id == '':
                bot.send_message(general_message_id, 'Такого пользователя нет в списке')
                return None

            bot.unban_chat_member(chanel_chat_id, unblock_user_id)
            block_users.pop(user, False)
            bot.send_message(general_message_id, 'Пользователь разблокирован')
            return None

        bot.send_message(general_message_id, 'Тип даныых не поддерживается')


    @bot.message_handler(content_types=["text", "photo", "video"])
    def sleep_text(message):
        global local_admin, all_users, block_users

        all_users.add(message.from_user.id)

        if message.content_type == 'photo' and message.caption.lower().strip()[:5] == '/send':
            send_mess(message)
            return None

        if str(message.from_user.id) in block_users:
            bot.send_message(message.chat.id, 'Вы были заблокированны модератором этого канала')
            return None

        bot.send_message(message.chat.id, f'Спасибо за ваше сообщение')

        markup = types.InlineKeyboardMarkup()
        btn_public = types.InlineKeyboardButton('✅', callback_data='public')
        btn_delete = types.InlineKeyboardButton('❌', callback_data='delete')
        btn_block = types.InlineKeyboardButton('🚫', callback_data='blocked')
        markup.row(btn_public, btn_delete)
        markup.add(btn_block)

        if len(local_admin) != 0:
            for i in range(len(local_admin)):
                bot.forward_message(chat_id=local_admin[i][0],
                                    from_chat_id=message.chat.id,
                                    message_id=message.message_id)
                id_delete_message = bot.send_message(local_admin[i][0], f'Выберите функцию', reply_markup=markup)
                local_admin[i][2].append(str(id_delete_message.id))


    @bot.callback_query_handler(func=lambda callback: True)
    def callback_message(call):
        global local_admin, id_local_admin, name_local_admin, name_chanel, chanel_chat_id
        try:
            if call.data == 'blocked':
                if not (block_users[call.message.from_user.id] in block_users):
                    block_users[str(call.message.chat.id)] = str(call.message.from_user.username)
                bot.restrict_chat_member(chanel_chat_id, call.message.from_user.id)
            if call.data == 'public':
                bot.copy_message(
                    chat_id=f'@{name_chanel}',
                    from_chat_id=call.message.chat.id,
                    message_id=call.message.id - 1)
            if call.data == 'public' or call.data == 'delete' or call.data == 'blocked':
                id_delete_message = 0
                for i in range(len(local_admin)):
                    for j in range(len(local_admin[i][2])):
                        if local_admin[i][2][j] == str(call.message.id):
                            id_delete_message = j

                for del_message in range(len(local_admin)):
                    bot.delete_message(
                        local_admin[del_message][0], int(local_admin[del_message][2][id_delete_message])
                    )
                    bot.delete_message(
                        local_admin[del_message][0], int(local_admin[del_message][2][id_delete_message]) - 1
                    )
                    del local_admin[del_message][2][id_delete_message]

            if call.data == "yes_admin":
                local_admin.append([str(id_local_admin), str(name_local_admin), []])
                bot.send_message(general_message_id, f'Вы добавили нового модератора')

                bot.send_message(str(id_local_admin), f'Поздравляю, вы модератор')
                id_local_admin = name_local_admin = None
            elif call.data == "not_admin":
                bot.send_message(general_message_id, f'Вы отклонили заявку')

                bot.send_message(str(id_local_admin), f'Вам отказано')
                id_local_admin = name_local_admin = None
        except Exception as ex:
            bot.send_message(general_message_id, str(ex))


except Exception as all_mistakes:
    print(all_mistakes)

print('bot worked')
bot.polling(none_stop=True, interval=0, timeout=0)