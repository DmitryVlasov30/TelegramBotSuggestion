from sqlite3 import connect

import telebot
from telebot import types




token = 'TOKEN'
bot = telebot.TeleBot(token)

all_users = set()
id_local_admin = name_local_admin = None
GENERAL_MESSAGE_ID = 'message_id главного админа'
# [user_id, username, [message]]
local_admin = []
NAME_CHANEL = 'название вашего телеграмм канала'
CHANEL_ID = 'chat id группы канала (отрицательное число)'
block_users = {}
appeal_list = []
# [user_id, username, massage_id]
block_message_list = []

PATH_DB = 'путь к вашей базе данных SQlite3'
NAME_TABLE = 'название вашей таблицы в базе данных'

try:

    with connect(PATH_DB) as conn:
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS moder (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            chat_id INTEGER UNIQUE
        )''')
        try:
            cur.execute(f'''INSERT INTO {NAME_TABLE} (username, chat_id) VALUES(?, ?)''',
                        ('админ', int(GENERAL_MESSAGE_ID))
                        )
        except:
            bot.send_message(GENERAL_MESSAGE_ID, 'Что то пошло не так при добавлении данных в таблицу')

        cur.execute(f'''SELECT username, chat_id 
            FROM {NAME_TABLE} 
        ''')
        data = cur.fetchall()
        for el in data:
            local_admin.append([el[1], el[0], []])


    def not_send_message_on_public_chat(func):
        def wrapper(message):
            global CHANEL_ID
            if CHANEL_ID == str(message.chat.id):
                return None
            function = func(message)
            return function
        return wrapper


    @bot.message_handler(commands=["start"])
    @not_send_message_on_public_chat
    def start(message):
        global all_users
        all_users.add(message.from_user.id)
        bot.send_message(message.chat.id, f'Отправьте сообщение')


    @bot.message_handler(commands=["up_admin"])
    @not_send_message_on_public_chat
    def new_local_admin(message):
        global id_local_admin, name_local_admin, all_users

        all_users.add(message.from_user.id)

        flag_admin = False
        id_local_admin = str(message.from_user.id)
        name_local_admin = message.from_user.username
        if message.from_user.username is None:
            name_local_admin = message.from_user.first_name
        if name_local_admin is None:
            name_local_admin = message.from_user.last_name
        if name_local_admin is None:
            name_local_admin = message.chat.id

        for i in range(len(local_admin)):
            if str(id_local_admin) == local_admin[i][0]:
                flag_admin = True

        if not flag_admin:
            bot.send_message(id_local_admin, f'Мы напишем главному админу, что вы хотите быть модератором')

            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton('✅', callback_data='yes_admin')
            btn2 = types.InlineKeyboardButton('❌', callback_data='not_admin')
            markup.row(btn1, btn2)

            bot.send_message(GENERAL_MESSAGE_ID, f'Человек с id: {id_local_admin} и под именем:'
                                                 f' {name_local_admin} хочет стать модератором', reply_markup=markup)
        else:
            bot.send_message(id_local_admin, f'Вы уже являетесь модератором')
            id_local_admin = name_local_admin = None


    @bot.message_handler(commands=["delete"])
    @not_send_message_on_public_chat
    def delete_loc_admin(message):
        global local_admin, GENERAL_MESSAGE_ID
        if str(message.from_user.id) == GENERAL_MESSAGE_ID:
            if len(local_admin) != 0:
                total_delete_adm(message)
            else:
                bot.send_message(GENERAL_MESSAGE_ID, f'У вас нет модераторов')
        else:
            bot.send_message(message.chat.id, f'у вас нет доступа к этой функции')


    def total_delete_adm(message):
        global local_admin, GENERAL_MESSAGE_ID
        text = message.text.lower()[7:].strip().replace(' ', '')
        flag_f = False
        delete_id = 0
        for i in range(len(local_admin)):
            str_i = str(i+1)
            if str_i == text:
                if str(local_admin[int(text)-1][0]) != GENERAL_MESSAGE_ID:
                    delete_id = local_admin[int(text)-1][0]
                    flag_f = True
                    break
                else:
                    bot.send_message(message.chat.id, f"Невозможно удалить главного админа")
                    return None
        if not flag_f:
            bot.send_message(GENERAL_MESSAGE_ID, f'Такого модератора не существует')
        else:
            with connect(PATH_DB) as conn_del_adm:
                cur_del_adm = conn_del_adm.cursor()
                try:
                    cur_del_adm.execute(f'''DELETE FROM {NAME_TABLE} WHERE chat_id = ?''',
                                        (int(delete_id),)
                                        )
                except:
                    bot.send_message(GENERAL_MESSAGE_ID, 'Что то пошло не так, пользователь не удалён из базы данных')
                    flag_f = False

                data_delete = cur_del_adm.fetchall()
                local_admin = []
                for el_del in data_delete:
                    local_admin.append([el_del[2], el_del[1], []])

            if not flag_f:
                return None
            bot.send_message(GENERAL_MESSAGE_ID, f'Модератор удалён')


    @bot.message_handler(commands=["send"])
    @not_send_message_on_public_chat
    def send_mess(message):
        global all_users
        delete_users = []
        if message.from_user.id != GENERAL_MESSAGE_ID:
            bot.send_message(message.chat.id, 'У вас нет доступа к этой функции')

        message_text = ''
        type_message = message.content_type
        if type_message == 'text':
            message_text = message.text.strip()[5:]
        if type_message == 'photo':
            message_text = message.caption.strip()[5:]

        for el_send_mess in all_users:
            try:
                if type_message == 'text':
                    bot.send_message(el_send_mess, message_text)
                if type_message == 'photo':
                    file_id = message.photo[-1].file_id
                    bot.send_photo(el_send_mess, file_id, caption=message_text)
            except Exception as ex:
                delete_users.append(el_send_mess)
                print(ex)

        for el_dis in delete_users:
            all_users.discard(el_dis)
        delete_users.clear()


    @bot.message_handler(commands=["admin"])
    @not_send_message_on_public_chat
    def list_adm(message):
        global local_admin, all_users, NAME_TABLE, PATH_DB

        if str(message.from_user.id) != GENERAL_MESSAGE_ID:
            bot.send_message(message.chat.id, 'У вас нет доступа к этой функции')

        local_admin = []
        with connect(PATH_DB) as con_lst:
            cur_lst = con_lst.cursor()
            cur_lst.execute(f'''
            SELECT *
            FROM  {NAME_TABLE}
            ''')
            data_lst = cur_lst.fetchall()
            print(data_lst)
            for el_lst in data_lst:
                local_admin.append([str(el_lst[2]), el_lst[1], []])

        print(local_admin)
        list_loc_adm = ''
        for i in range(len(local_admin)):
            list_loc_adm += f"№ {i+1} name: {local_admin[i][1]}\n"
        bot.send_message(GENERAL_MESSAGE_ID, f'{list_loc_adm}')


    @bot.message_handler(commands=["block_lst"])
    @not_send_message_on_public_chat
    def block_user(message):
        global block_users, GENERAL_MESSAGE_ID

        block_inf = 'Заблокированные пользователи:\n'

        tuple_block = tuple(block_users.items())
        for i in range(len(tuple_block)):
            block_inf += (f'username: {tuple_block[i][1][0]}, '
                          f'message id: {tuple_block[i][0]}, '
                          f'возможность апелляции: {"есть" if tuple_block[i][1][1] else 'нету'}\n')

        bot.send_message(GENERAL_MESSAGE_ID, block_inf)


    @bot.message_handler(commands=["unblock"])
    @not_send_message_on_public_chat
    def unblock(message):
        global block_users, GENERAL_MESSAGE_ID, CHANEL_ID
        try:
            if str(message.from_user.id) != GENERAL_MESSAGE_ID:
                bot.send_message(message.chat.id, 'У вас не доступа к этой функции')
                return None

            if message.content_type == 'text':
                user = message.text[8:].strip()
                unblock_user_id = ''

                tuple_block = tuple(block_users.items())

                for i in range(len(tuple_block)):
                    if tuple_block[i][1][0] == user:
                        unblock_user_id = tuple_block[i][0]

                if unblock_user_id == '':
                    bot.send_message(GENERAL_MESSAGE_ID, 'Такого пользователя нет в списке')
                    return None

                bot.unban_chat_member(CHANEL_ID, int(unblock_user_id))
                del block_users[unblock_user_id]
                bot.send_message(GENERAL_MESSAGE_ID, 'Пользователь разблокирован')
                bot.send_message(unblock_user_id, 'Вас разблокировали')
                return None

            bot.send_message(GENERAL_MESSAGE_ID, 'Тип данных не поддерживается')
        except Exception as ex:
            bot.send_message(GENERAL_MESSAGE_ID, str(ex))


    @bot.message_handler(commands=["appeal"])
    @not_send_message_on_public_chat
    def appeal(message):
        global GENERAL_MESSAGE_ID, block_users, appeal_list

        if not str(message.chat.id) in block_users:
            bot.send_message(message.chat.id, "Вы не заблокированы")
            return None

        if message.content_type != 'text':
            bot.send_message(message.chat.id, 'В качестве апелляции вы можете подать только текст')
            return None

        if not block_users[str(message.chat.id)][1]:
            bot.send_message(message.chat.id, 'Вы не можете отправлять апелляцию больше одного раза')
            return None

        bot.send_message(message.chat.id, 'Мы отправили запрос на апелляцию')
        chat_id = str(message.chat.id)

        message_text = message.text[7:].strip()

        markup = types.InlineKeyboardMarkup()
        btn_approve = types.InlineKeyboardButton('✅', callback_data='approve')
        btn_refuse = types.InlineKeyboardButton('❌', callback_data='refuse')
        markup.row(btn_approve, btn_refuse)

        message_for_general_admin = bot.send_message(GENERAL_MESSAGE_ID,
                                                     f'Вам отправили запрос на разблокировку:\n {message_text}',
                                                     reply_markup=markup)
        appeal_list.append([chat_id, message_for_general_admin.id])


    @bot.message_handler(content_types=["text", "photo", "video"])
    @not_send_message_on_public_chat
    def sleep_text(message):
        global local_admin, all_users, block_users, block_message_list

        all_users.add(message.from_user.id)

        if message.content_type == 'photo' and message.caption.lower().strip()[:5] == '/send':
            send_mess(message)
            return None

        if str(message.from_user.id) in block_users:
            bot.send_message(message.chat.id, 'Вы были заблокированы модератором этого канала')
            return None

        block_username = message.from_user.username
        if message.from_user.username is None:
            block_username = message.from_user.first_name
        if block_username is None:
            block_username = message.from_user.last_name
        if block_username is None:
            block_username = message.chat.id
        block_user_id = message.chat.id

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
                block_message_list.append([block_user_id, block_username, str(id_delete_message.id)])


    @bot.callback_query_handler(func=lambda callback: True)
    def callback_message(call):
        global local_admin, id_local_admin, name_local_admin, NAME_CHANEL, \
            GENERAL_MESSAGE_ID, CHANEL_ID, block_message_list, appeal_list, NAME_TABLE, PATH_DB

        try:
            if call.data == 'blocked':
                id_block_message = -1
                for i in range(len(block_message_list)):
                    if str(call.message.id) == block_message_list[i][-1]:
                        id_block_message = i

                if id_block_message == -1:
                    bot.send_message(GENERAL_MESSAGE_ID, 'Пользователь не найден, блокировка не удалась')
                    return None

                block_username = block_message_list[id_block_message][1]
                block_user_id = block_message_list[id_block_message][0]

                if str(block_user_id) == GENERAL_MESSAGE_ID:
                    bot.send_message(GENERAL_MESSAGE_ID, 'Вас нельзя заблокировать!')

                if not (block_user_id in block_users) and str(block_user_id) != GENERAL_MESSAGE_ID:
                    block_users[str(block_user_id)] = [str(block_username), True]
                    bot.restrict_chat_member(CHANEL_ID, block_user_id)
                    bot.send_message(block_user_id, 'Вас заблокировали')

            if call.data == 'public':
                bot.copy_message(
                    chat_id=f'@{NAME_CHANEL}',
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
                        local_admin[del_message][0], int(local_admin[del_message][2][id_delete_message])-1
                    )
                    del local_admin[del_message][2][id_delete_message]

            if call.data == 'approve' or call.data == 'refuse':
                id_appeal_message = 0
                for i in range(len(appeal_list)):
                    if call.message.id == appeal_list[i][1]:
                        id_appeal_message = i

                if call.data == 'approve':
                    bot.unban_chat_member(CHANEL_ID, int(appeal_list[id_appeal_message][0]))
                    bot.delete_message(GENERAL_MESSAGE_ID, appeal_list[id_appeal_message][1])
                    bot.send_message(appeal_list[id_appeal_message][0], 'Вас разблокировали')

                    del block_users[str(appeal_list[id_appeal_message][0])]
                    del appeal_list[id_appeal_message]

                else:
                    bot.delete_message(GENERAL_MESSAGE_ID, appeal_list[id_appeal_message][1])
                    block_users[appeal_list[id_appeal_message][0]][1] = False
                    bot.send_message(appeal_list[id_appeal_message][0], 'Вам отказано в разблокировке')

                    del appeal_list[id_appeal_message]

            if call.data == "yes_admin":
                id_local_admin = int(id_local_admin)
                local_admin = []

                with connect(PATH_DB) as conn_up_admin:
                    cur_up_admin = conn_up_admin.cursor()
                    try:
                        cur_up_admin.execute(f'''INSERT INTO {NAME_TABLE} (username, chat_id) VALUES(?, ?)''',
                                             (name_local_admin, id_local_admin)
                                             )
                    except:
                        bot.send_message(GENERAL_MESSAGE_ID, 'Что то пошло не так при добавлении данных в таблицу')

                    cur_up_admin.execute(f'''SELECT username, chat_id 
                        FROM {NAME_TABLE} 
                    ''')
                    data2 = cur.fetchall()
                    for el2 in data2:
                        local_admin.append([el2[2], el2[1], []])

                bot.send_message(GENERAL_MESSAGE_ID, f'Вы добавили нового модератора')
                bot.send_message(str(id_local_admin), f'Поздравляю, вы модератор')
                id_local_admin = name_local_admin = None

            elif call.data == "not_admin":
                bot.send_message(GENERAL_MESSAGE_ID, f'Вы отклонили заявку')

                bot.send_message(str(id_local_admin), f'Вам отказано')
                id_local_admin = name_local_admin = None

        except Exception as ex:
            bot.send_message(GENERAL_MESSAGE_ID, str(ex))


except Exception as all_mistakes:
    print(all_mistakes)

print('bot worked')
bot.polling(none_stop=True, interval=0, timeout=0)
