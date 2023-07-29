from telebot.async_telebot import AsyncTeleBot
from telebot.types import BotCommand, CallbackQuery, Poll, BotCommandScopeChat
import asyncio
import time
TOKEN = 'YOUR_TOKEN'
bot = AsyncTeleBot(TOKEN)

myGroupID = 0000000 # group ID

async def add_commands():
    await bot.delete_my_commands()
    scope_chat = BotCommandScopeChat(myGroupID)
    commands = [
            BotCommand('role', 'Смена роли'),
            BotCommand('invite', 'Добавить'),
            BotCommand('mute', 'Заглушить'),
            BotCommand('ban', 'Изгнать')
        ]
    await bot.set_my_commands(commands, scope_chat)

class PollBot:
    def __init__(self):
        self.poll_active = False
        self.current_poll = {}
        self.current_role = ''
        self.type = ''
        self.votes = []
        self.username = ''
        self.changing_user_id = 0
        self.invoke_user_id = 0
        self.muted_users = []
        self.muted_user_ids = []
        self.mute_timeout = []
        self.temp_mute_user_id = 0
        self.temp_mute_timeout = 0
        self.temp_user = ''
        self.warn_user_timers = []
        self.warns_to_user = []

    async def close_poll(self):
        # await bot.stop_poll(myGroupID, self.current_poll.id)
        await bot.reply_to(self.current_poll, 'Опрос закрыт')
        self.current_poll = {}
        self.poll_active = False
        self.votes.clear()
        self.current_role = ''
        self.type = ''
        self.username = ''
        self.changing_user_id = 0
        self.invoke_user_id = 0
        self.temp_mute_user_id = 0
        self.temp_mute_timeout = 0
        self.temp_user = ''
    
    async def create_poll(self, type, message):
        if type == 'ban':
            self.poll_active = True
            await bot.delete_message(myGroupID, message.id)
            self.current_poll = await bot.send_poll(myGroupID, f'Изгнать пользователя {message.reply_to_message.from_user.first_name}', ['👍🏻', '👎🏻'], is_anonymous=False, open_period=600)
            await asyncio.sleep(600)
            await self.close_poll()
        elif type == 'invite':
            self.poll_active = True
            await bot.delete_message(myGroupID, message.id)
            self.current_poll = await bot.send_poll(myGroupID, f'{message.from_user.first_name} хочет добавить нового пользователя, добавим ?', ['👍🏻', '👎🏻'], is_anonymous=False, open_period=600)
            await asyncio.sleep(600)
            await self.close_poll()
        elif type == 'mute':
            self.poll_active = True
            self.temp_mute_user_id = message.reply_to_message.from_user.id
            self.temp_mute_timeout = message.text.replace('/mute ', '')
            self.temp_user = message.reply_to_message.from_user.first_name
            await bot.delete_message(myGroupID, message.id)
            self.current_poll = await bot.send_poll(myGroupID, f'Мут пользователя {message.reply_to_message.from_user.first_name} на {self.temp_mute_timeout} минут.', ['👍🏻', '👎🏻'], is_anonymous=False, open_period=600)
            await asyncio.sleep(600)
            await self.close_poll()
        elif type == 'title_change':
            self.poll_active = True
            self.username = message.reply_to_message.from_user.first_name
            self.changing_user_id = message.reply_to_message.from_user.id
            self.current_role = message.text.replace('/role ', '').strip()
            await bot.delete_message(myGroupID, message.id)
            self.current_poll = await bot.send_poll(myGroupID, f'{self.username} претендует на титул {self.current_role}', ['👍🏻', '👎🏻'], is_anonymous=False, open_period=600)
            await asyncio.sleep(600)
            await self.close_poll()
    async def invite(self):
        link = await bot.create_chat_invite_link(myGroupID, name='Приглашение', member_limit=1)
        await bot.send_message(myGroupID, link.invite_link)

    async def ban(self):
        await bot.promote_chat_member(myGroupID, self.changing_user_id, 
                                False,
                                False,
                                False,
                                False,
                                False,
                                False,
                                False,
                                False,
                                False,
                                False)
        await bot.ban_chat_member(myGroupID, self.changing_user_id)

    async def mute(self):
        self.muted_user_ids.append(self.temp_mute_user_id)
        self.muted_users.append(self.temp_user)
        self.warn_user_timers.append(time.time())
        self.warns_to_user.append(0)
        current_time = time.time()
        self.mute_timeout.append(float(current_time) + float(self.temp_mute_timeout) * 60.0)

    async def title_change(self):
        role = self.current_role
        user_id = self.changing_user_id
        await bot.promote_chat_member(myGroupID, user_id, 
                                False,
                                False,
                                False,
                                False,
                                False,
                                False,
                                True,
                                False,
                                False,
                                True)
        await bot.set_chat_administrator_custom_title(myGroupID, user_id, role)
        await bot.send_message(myGroupID, f'{poll_manager.username} теперь имеет титул {poll_manager.current_role}.', disable_notification=True)

poll_manager = PollBot()

#------------------------------------Перехват ответов на опрос--------------------------------------------------------
@bot.poll_answer_handler()
async def handle_poll(a):
    if poll_manager.poll_active:
        if len(a.option_ids) == 0:
            if len(poll_manager.votes) > 0:
                for vote_data in poll_manager.votes:
                    if vote_data['user_id'] == a.user.id:
                        poll_manager.votes.remove(vote_data)
                        return

        if a.option_ids[0] == 0:
            poll_manager.votes.append({'user_id': a.user.id, 'vote': 'yes'})
        else:
            poll_manager.votes.append({'user_id': a.user.id, 'vote': 'no'})
        
        
        yes_votes = 0
        count_users = await bot.get_chat_members_count(myGroupID)
        if len(poll_manager.votes) > 0:
            for vote in poll_manager.votes:
                if vote['vote'] == 'yes':
                    yes_votes += 1
        
        if yes_votes > ((count_users - 2)/2):
            if poll_manager.type == 'title_change':
                await poll_manager.title_change()
            elif poll_manager.type == 'ban':
                await poll_manager.ban()
            elif poll_manager.type == 'invite':
                await poll_manager.invite()
            elif poll_manager.type == 'mute':
                await poll_manager.mute()
#------------------------------------Перехват ответов на опрос--------------------------------------------------------

#------------------------------------Опрос на титулы--------------------------------------------------------
@bot.message_handler(commands=['role'])
async def role_change(message):
    poll_manager.type = 'title_change'
    
    if poll_manager.poll_active:
        await bot.reply_to(message, f'{message.from_user.first_name}, предыдущий опрос ещё не закрыт, над подождать 😒')
        return

    if message.reply_to_message:
        await poll_manager.create_poll('title_change', message)
    else:
        await bot.reply_to(message, f'{message.from_user.first_name} эту команду надо отправлять цитируя сообщение пользователя, чей титул хочешь сменить.')
#------------------------------------Опрос на титулы--------------------------------------------------------

#------------------------------------Опрос на добавление пользователя--------------------------------------------------------
@bot.message_handler(commands=['invite'])
async def invite_user(message):
    poll_manager.type = 'invite'

    if poll_manager.poll_active:
        await bot.reply_to(message, f'{message.from_user.first_name}, предыдущий опрос ещё не закрыт, над подождать 😒')
        return
    
    await poll_manager.create_poll('invite', message)
#------------------------------------Опрос на добавление пользователя--------------------------------------------------------

#------------------------------------Опрос на бан пользователя--------------------------------------------------------
@bot.message_handler(commands=['ban'])
async def ban(message):
    poll_manager.type = 'ban'

    if poll_manager.poll_active:
        await bot.reply_to(message, f'{message.from_user.first_name}, предыдущий опрос ещё не закрыт, над подождать 😒')
        return
    
    if message.reply_to_message:
        await poll_manager.create_poll('ban', message)
    else:
        await bot.reply_to(message, f'{message.from_user.first_name} эту команду надо отправлять цитируя сообщение пользователя.')
#------------------------------------Опрос на бан пользователя--------------------------------------------------------

#------------------------------------Опрос на мут пользователя--------------------------------------------------------
@bot.message_handler(commands=['mute'])
async def mute(message):
    poll_manager.type = 'mute'

    if poll_manager.poll_active:
        await bot.reply_to(message, f'{message.from_user.first_name}, предыдущий опрос ещё не закрыт, над подождать 😒')
        return
    
    if message.reply_to_message:
        await poll_manager.create_poll('mute', message)
    else:
        await bot.reply_to(message, f'{message.from_user.first_name} эту команду надо отправлять цитируя сообщение пользователя.')

@bot.message_handler(func=lambda msg: msg.from_user.id in poll_manager.muted_user_ids)
async def mute_msg(message):
    muted_user_position = poll_manager.muted_user_ids.index(message.from_user.id)
    if poll_manager.mute_timeout[muted_user_position] - time.time() > 0:
        user_mute_time = (poll_manager.mute_timeout[muted_user_position] - time.time()) / 60
        minutes = convert_to_minuts(user_mute_time)
        await bot.delete_message(myGroupID, message.id)
        print(poll_manager.warn_user_timers[muted_user_position] - time.time())
        if poll_manager.warn_user_timers[muted_user_position] - time.time() > -5 and poll_manager.warns_to_user[muted_user_position] == 0:
            await bot.send_message(myGroupID, f'{poll_manager.muted_users[muted_user_position]} вы получаете предупреждение, в муте не надо шуметь. Ещё два предупреждения и будете удалены из чата. Оставшееся время ({minutes}) минут')
            poll_manager.warn_user_timers[muted_user_position] = time.time()
            poll_manager.warns_to_user[muted_user_position] = 1
        elif poll_manager.warn_user_timers[muted_user_position] - time.time() > -5 and poll_manager.warns_to_user[muted_user_position] == 1:
            await bot.send_message(myGroupID, f'{poll_manager.muted_users[muted_user_position]}..😕 осталось последнее и будете удалены из чата. Оставшееся время ({minutes}) минут')
            poll_manager.warn_user_timers[muted_user_position] = time.time()
            poll_manager.warns_to_user[muted_user_position] = 2
        elif poll_manager.warn_user_timers[muted_user_position] - time.time() > -5 and poll_manager.warns_to_user[muted_user_position] == 2:
            await bot.send_message(myGroupID, f'{poll_manager.muted_users[muted_user_position]}... Оставшееся время ({minutes}) минут')
            poll_manager.warn_user_timers[muted_user_position] = time.time()
            poll_manager.warns_to_user[muted_user_position] = 3
        elif poll_manager.warn_user_timers[muted_user_position] - time.time() > -5 and poll_manager.warns_to_user[muted_user_position] == 3:
            await bot.send_message(myGroupID, f'{poll_manager.muted_users[muted_user_position]} наверное было время подумать, как минимум 15 секунд ')
            await bot.ban_chat_member(myGroupID, poll_manager.muted_user_ids[muted_user_position])
            poll_manager.muted_users.pop(muted_user_position)
            poll_manager.mute_timeout.pop(muted_user_position)
            poll_manager.muted_user_ids.pop(muted_user_position)
            poll_manager.warns_to_user.pop(muted_user_position)
            poll_manager.warn_user_timers.pop(muted_user_position)
        else:
            poll_manager.warn_user_timers[muted_user_position] = time.time()
    else:
        await bot.send_message(myGroupID, f'Мут с {poll_manager.muted_users[muted_user_position]} снят. Не повторяйте ошибок 😊')
        poll_manager.muted_users.pop(muted_user_position)
        poll_manager.mute_timeout.pop(muted_user_position)
        poll_manager.muted_user_ids.pop(muted_user_position)
        poll_manager.warns_to_user.pop(muted_user_position)
        poll_manager.warn_user_timers.pop(muted_user_position)
#------------------------------------Опрос на мут пользователя--------------------------------------------------------

async def main_func():
    await add_commands()
    await bot.polling(non_stop=True)
asyncio.run(main_func())