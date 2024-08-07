import time
import datetime
import multiprocessing as mp
import requests
import json
import html
import logging
import traceback


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# This can be your own ID, or one for a developer group/channel.
# You can use the /start command of this bot to see your chat id.
DEVELOPER_CHAT_ID = -1002189363889

import traceback
from telegram.constants import ParseMode
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import Updater, ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
from account_api import ActiveDirectory
from time_tools import timeisformatted
from schedule_list_tools import Write_task, Cleanup_tasks, Sort_tasks, Get_First_task, Delete_First_task

# ENV
import os
DEVELOPER_CHAT_ID = os.getenv(key='DEVELOPER_CHAT_ID')
TELEGRAM_TOKEN = os.getenv(key='TELEGRAM_TOKEN')
MIS_ALERT = os.getenv(key='MIS_ALERT')
HOST16 = os.getenv(key='HOST16')
HOST34 = os.getenv(key='HOST34')

from allow import allow_groups



async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
    )


async def bad_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Raise an error to trigger the error handler."""
    await context.bot.wrong_method_name()  # type: ignore[attr-defined]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.id not in allow_groups :
        print(f"Group {update.message.chat.id} not allow !")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text="📘 I'm a ActiveDirectory Bot")

async def ad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.id not in allow_groups :
        print(f"Group {update.message.chat.id} not allow !")
        return
    keyboard = [
        [
            InlineKeyboardButton("🛑 Disable", callback_data="disable"),
        ],
        [
            InlineKeyboardButton("🟢 Enable", callback_data="enable"),
        ],
        [
            InlineKeyboardButton("🔓 Unlock", callback_data="unlock"),
        ],
        [
            InlineKeyboardButton("✂️ Reset", callback_data="reset"),
        ],
        [
            InlineKeyboardButton("📆 Expiredate", callback_data="expiredate"),
        ],
        [
            InlineKeyboardButton("🕗 Schedule Task", callback_data="schedule"),
        ],
        [
            InlineKeyboardButton("❌", callback_data="end"),
        ],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text="📍 <b>Choose A Method</b>",
        reply_markup=markup,
        parse_mode="HTML",
    )

async def schedule_level1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🛑 Disable", callback_data="schedule_disable"),
        ],
        [
            InlineKeyboardButton("🟢 Enable", callback_data="schedule_enable"),
        ],
        [
            InlineKeyboardButton("🔓 Unlock", callback_data="schedule_unlock"),
        ],
        [
            InlineKeyboardButton("❌", callback_data="end"),
        ],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        text="📍 <b>Choose A Method For Schedule Task</b>",
        reply_markup=markup,
        parse_mode="HTML",
    )

async def schedule_level2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    method = update.callback_query.data.split('_')[-1]
    activedirectory = ActiveDirectory()
    if method == "enable" :
        reply_icon = "🟢"
        user_List = activedirectory.user_List_disabled()
    elif method == "disable" :
        reply_icon = "🛑"
        user_List = activedirectory.user_List_enabled()
    elif method == "unlock" :
        reply_icon = "🔓"
        user_List = activedirectory.user_List()
    userKeyboard = []
    userKeyboardSub = []
    for user in user_List :
        if user == '' :
            continue
        if len(userKeyboardSub) == 3 :
            userKeyboardSubCopy = userKeyboardSub.copy()
            userKeyboard.append(userKeyboardSubCopy)
            userKeyboardSub.clear()
        userKeyboardSub.append(InlineKeyboardButton(user, callback_data=f"schedule-{method}-{user}"),)
    if len(userKeyboardSub) > 0 :
        userKeyboardSubCopy = userKeyboardSub.copy()
        userKeyboard.append(userKeyboardSubCopy)
        userKeyboardSub.clear()
    userKeyboard.append([InlineKeyboardButton("❌", callback_data="end"),])
    markup = InlineKeyboardMarkup(userKeyboard)
    await update.callback_query.edit_message_text(
        text=f"<b>🕗 Schedule {reply_icon} {method} A User</b>",
        reply_markup=markup,
        parse_mode="HTML"
    )

async def schedule_level3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    callback_data = update.callback_query.data
    method = callback_data.split('-')[1]
    user = callback_data.split('-')[2]
    if method == "enable" :
        reply_icon = "🟢"
    elif method == "disable" :
        reply_icon = "🛑"
    elif method == "unlock" :
        reply_icon = "🔓"
    now = datetime.datetime.now()
    keyboard = [
        [
            InlineKeyboardButton(str(now.year), callback_data=f"schedule-{method}-{user}-{str(now.year)}"),
            InlineKeyboardButton(str(now.year + 1), callback_data=f"schedule-{method}-{user}-{str(now.year + 1)}"),
        ],
    ]
    keyboard.append([InlineKeyboardButton("❌", callback_data="end"),])
    markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        text=f"<b>🕗 Schedule {reply_icon} {method} {user} At Year:</b>",
        reply_markup=markup,
        parse_mode="HTML"
    )

async def schedule_level4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    callback_data = update.callback_query.data
    method = callback_data.split('-')[1]
    if method == "enable" :
        reply_icon = "🟢"
    elif method == "disable" :
        reply_icon = "🛑"
    elif method == "unlock" :
        reply_icon = "🔓"
    user = callback_data.split('-')[2]
    year = callback_data.split('-')[3]
    now = datetime.datetime.now()
    keyboard = []
    subKeyboard = []
    for i in range(1, 13) :
        if len(subKeyboard) == 3 :
            subKeyboardCopy = subKeyboard.copy()
            keyboard.append(subKeyboardCopy)
            subKeyboard.clear()
        if i // 10 != 1 :
            month = "0" + str(i)
        else :
            month = str(i)
        subKeyboard.append(InlineKeyboardButton(str(i), callback_data=f"schedule-{method}-{user}-{year}-{month}"))
    if len(subKeyboard) > 0 :
        subKeyboardCopy = subKeyboard.copy()
        keyboard.append(subKeyboardCopy)
        subKeyboard.clear()
    keyboard.append([InlineKeyboardButton("❌", callback_data="end"),])
    markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        text=f"<b>🕗 Schedule {reply_icon} {method}</b> <code>{user}</code> <b>At {year} Month:</b>",
        reply_markup=markup,
        parse_mode="HTML"
    )

async def schedule_level5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    callback_data = update.callback_query.data
    method = callback_data.split('-')[1]
    if method == "enable" :
        reply_icon = "🟢"
    elif method == "disable" :
        reply_icon = "🛑"
    elif method == "unlock" :
        reply_icon = "🔓"
    user = callback_data.split('-')[2]
    year = callback_data.split('-')[3]
    month = callback_data.split('-')[4]
    isLeapYear = __leapyear(year)
    monthDaysMapping = {
        "01" : 31,
        "02" : 0,
        "03" : 31,
        "04" : 30,
        "05" : 31,
        "06" : 30,
        "07" : 31,
        "08" : 31,
        "09" : 30,
        "10" : 31,
        "11" : 30,
        "12" : 31,
    }
    if isLeapYear :
        monthDaysMapping["02"] = 29
    else :
        monthDaysMapping["02"] = 28 
    keyboard = []
    subKeyboard = []
    for i in range(1, monthDaysMapping[month] + 1) :
        if len(subKeyboard) == 5 :
            subKeyboardCopy = subKeyboard.copy()
            keyboard.append(subKeyboardCopy)
            subKeyboard.clear()
        if i // 10 < 1 :
            day = "0" + str(i)
        else :
            day = str(i)
        subKeyboard.append(InlineKeyboardButton(str(i), callback_data=f"schedule-{method}-{user}-{year}-{month}-{day}"))
    if len(subKeyboard) > 0 :
        subKeyboardCopy = subKeyboard.copy()
        keyboard.append(subKeyboardCopy)
        subKeyboard.clear()
    keyboard.append([InlineKeyboardButton("❌", callback_data="end"),])
    markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        text=f"<b>🕗 Schedule {reply_icon} {method}</b> <code>{user}</code> <b>At {year} {month} Day:</b>",
        reply_markup=markup,
        parse_mode="HTML"
    )

def __leapyear(year):
    year = int(year)
    if (year % 4) == 0:
       if (year % 100) == 0:
           if (year % 400) == 0:
               #print("{0} 是闰年".format(year))
               return True   # 整百年能被400整除的是闰年
           else:
               #print("{0} 不是闰年".format(year))
               return False
       else:
           #print("{0} 是闰年".format(year))       # 非整百年能被4整除的为闰年
           return True
    else:
       #print("{0} 不是闰年".format(year))
        return False

async def schedule_level6(update: Update, context: ContextTypes.DEFAULT_TYPE):
    callback_data = update.callback_query.data
    method = callback_data.split('-')[1]
    if method == "enable" :
        reply_icon = "🟢"
    elif method == "disable" :
        reply_icon = "🛑"
    elif method == "unlock" :
        reply_icon = "🔓"
    user = callback_data.split('-')[2]
    year = callback_data.split('-')[3]
    month = callback_data.split('-')[4]
    day = callback_data.split('-')[5]
    timeList = [
        "00:00", "01:00", "02:00",
        "03:00", "04:00", "05:00",
        "06:00", "07:00", "08:00",
        "09:00", "10:00", "11:00",
        "12:00", "13:00", "14:00",
        "15:00", "16:00", "17:00",
        "18:00", "19:00", "20:00",
        "21:00", "22:00", "23:00",
    ]
    keyboard = []
    subKeyboard = []
    for i in range(0, len(timeList)) :
        if len(subKeyboard) == 3 :
            subKeyboardCopy = subKeyboard.copy()
            keyboard.append(subKeyboardCopy)
            subKeyboard.clear()
        subKeyboard.append(InlineKeyboardButton(timeList[i], callback_data=f"schedule-{method}-{user}-{year}-{month}-{day}-{timeList[i]}"))
    if len(subKeyboard) > 0 :
        subKeyboardCopy = subKeyboard.copy()
        keyboard.append(subKeyboardCopy)
        subKeyboard.clear()
    keyboard.append([InlineKeyboardButton("❌", callback_data="end"),])
    markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        text=f"<b>🕗 Schedule {reply_icon} {method}</b> <code>{user}</code> <b>At {year} {month} {day} Time:</b>",
        reply_markup=markup,
        parse_mode="HTML"
    )

async def schedule_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    callback_data = update.callback_query.data
    method = callback_data.split('-')[1]
    if method == "enable" :
        reply_icon = "🟢"
    elif method == "disable" :
        reply_icon = "🛑"
    elif method == "unlock" :
        reply_icon = "🔓"
    user = callback_data.split('-')[2]
    year = callback_data.split('-')[3]
    month = callback_data.split('-')[4]
    day = callback_data.split('-')[5]
    time = callback_data.split('-')[6]
    keyboard = [
        [
            InlineKeyboardButton("✅", callback_data=f"schedule-{method}-{user}-{year}{month}{day}-{time}"),
            InlineKeyboardButton("❌", callback_data="end"),
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        text=f"<b>🕗 Schedule {reply_icon} {method}</b> <code>{user}</code> <b>At {year} {month} {day} {time}</b>",
        reply_markup=markup,
        parse_mode="HTML"
    )

async def schedule_submit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    callback_data = update.callback_query.data
    method = callback_data.split('-')[1]
    user = callback_data.split('-')[2]
    time1 = callback_data.split('-')[3]
    time2 = callback_data.split('-')[4]
    schedule_Time = time1 + time2.replace(':', '')
    result = "<b>------ Schedule Add ------</b>" + "\n" \
             "<b>Method</b> : <code>" + method + "</code>\n" + \
             "<b>Account</b> : <code>" + user + "</code>\n" + \
             "<b>Scheduled Time</b> : <code>" + schedule_Time + "</code>\n"
    print(result)
    task = '{"Method" : "' + method + '", "Account" : "' + user + '", "Time" : "' + schedule_Time + '"}'
    Write_task(str(task))
    await update.callback_query.edit_message_text(
        text=result,
        parse_mode="HTML"
    )

async def normal_level1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    callback_data = update.callback_query.data
    activedirectory = ActiveDirectory()
    if callback_data == "enable" :
        reply_icon = "🟢"
        user_List = activedirectory.user_List_disabled()
    elif callback_data == "disable" :
        reply_icon = "🛑"
        user_List = activedirectory.user_List_enabled()
    elif callback_data == "unlock" :
        reply_icon = "🔓"
        user_List = activedirectory.user_List()
    elif callback_data == "expiredate" :
        reply_icon = "📆"
        user_List = activedirectory.user_List()
    else :
        reply_icon = "✂️"
        user_List = activedirectory.user_List()
    userKeyboard = []
    userKeyboardSub = []
    for user in user_List :
        if user == '' :
            continue
        if len(userKeyboardSub) == 3 :
            userKeyboardSubCopy = userKeyboardSub.copy()
            userKeyboard.append(userKeyboardSubCopy)
            userKeyboardSub.clear()
        userKeyboardSub.append(InlineKeyboardButton(user, callback_data=f"{callback_data}-{user}"),)
    if len(userKeyboardSub) > 0 :
        userKeyboardSubCopy = userKeyboardSub.copy()
        userKeyboard.append(userKeyboardSubCopy)
        userKeyboardSub.clear()
    userKeyboard.append([InlineKeyboardButton("❌", callback_data="end"),])
    markup = InlineKeyboardMarkup(userKeyboard)
    await update.callback_query.edit_message_text(
        text=f"{reply_icon} <b>{callback_data} A User</b>",
        reply_markup=markup,
        parse_mode="HTML"
    )

async def normal_level2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    callback_data = update.callback_query.data
    method = callback_data.split('-')[0]
    target = callback_data.split('-')[1]
    if method == "unlock" or method == "reset":
        activedirectory = ActiveDirectory(host=HOST16)
        if method == "unlock" :
            result = activedirectory.Account_unlocker(target)
        elif method == "reset" :
            result = activedirectory.Account_Password_Reset(target)
    else :
        activedirectory = ActiveDirectory()
        if method == "disable" :
            result = activedirectory.Account_disabler(target)
        elif method == "enable" :
            result = activedirectory.Account_enabler(target)
        elif method == "unlock" :
            result = activedirectory.Account_unlocker(target)
        elif method == "expiredate" :
            result = activedirectory.Account_expire_date(target)
        else :
            result = "ERROR !"
    activedirectory.__del__()
    await update.callback_query.edit_message_text(
        text=f"<b>{result}</b>",
        parse_mode="HTML"
    )

async def expiredate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.id not in allow_groups :
        print(f"Group {update.message.chat.id} not allow !")
        return
    account_name = " ".join(context.args)
    ad = ActiveDirectory()
    result = ad.Account_expire_date(account_name)
    ad.__del__()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=result)

async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.id not in allow_groups :
        print(f"Group {update.message.chat.id} not allow !")
        return
    account_name = " ".join(context.args)
    ad = ActiveDirectory(host=HOST16)
    result = ad.Account_unlocker(account_name)
    ad.__del__()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=result)

async def disable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.id not in allow_groups :
        print(f"Group {update.message.chat.id} not allow !")
        return
    account_name = " ".join(context.args)
    ad = ActiveDirectory()
    result = ad.Account_disabler(account_name)
    ad.__del__()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=result)

async def enable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.id not in allow_groups :
        print(f"Group {update.message.chat.id} not allow !")
        return
    account_name = " ".join(context.args)
    ad = ActiveDirectory()
    result = ad.Account_enabler(account_name)
    ad.__del__()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=result)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.id not in allow_groups :
        print(f"Group {update.message.chat.id} not allow !")
        return
    account_name = " ".join(context.args)
    ad = ActiveDirectory(host=HOST16)
    result = ad.Account_Password_Reset(account_name)
    ad.__del__()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=result)

async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.id not in allow_groups :
        print(f"Group {update.message.chat.id} not allow !")
        return
    # check arguments count 
    if context.args == [] :
        await update.message.reply_text(text="missing arguments")
        return
    if len(context.args) > 3 :
        await update.message.reply_text(text="Too many argumetns")
        return
    # 檢查 methods 是否存在
    methods = ['enable', 'disable', 'unlock']
    if context.args[0] not in methods:
        await update.message.reply_text(text="method not exist")
        return
    else :
        # Method
        method = context.args[0]
    # Account Name
    account_Name = context.args[1]
    # check the time format
    if timeisformatted(context.args[2]) :
        # Schedule Time
        now = datetime.datetime.now()
        schedule_Time = context.args[2]
        if len(schedule_Time) == 4 :
            month = str(now.month)
            day = str(now.day)
            if len(str(now.month)) == 1 :
                month = "0" + str(now.month)
            if len(str(now.day)) == 1 :
                day = "0" + str(now.day)
            schedule_Time = str(now.year) + month + day + schedule_Time
        elif len(schedule_Time) == 6 :
            month = str(now.month)
            if len(str(now.month)) == 1 :
                month = "0" + str(now.month)
            schedule_Time = str(now.year) + month + schedule_Time
        elif len(schedule_Time) == 8 :
            schedule_Time = str(now.year) + schedule_Time
        else :
            pass
    else :
        await update.message.reply_text(text="Wrong time format")
        return
    
    result = "------ Schedule Add ------" + "\n" \
             "Method : " + method + "\n" + \
             "Account : " + account_Name + "\n" + \
             "Scheduled Time : " + schedule_Time + "\n"
    task = '{"Method" : "' + method + '", "Account" : "' + account_Name + '", "Time" : "' + schedule_Time + '"}'
    Write_task(str(task))
    await context.bot.send_message(chat_id=update.effective_chat.id, text=result)

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #print(update.callback_query.message.chat_id)
    await update.callback_query.edit_message_text(
        text="Closed",
        parse_mode="HTML"
    )

def Queue_loop():
    while True :
        #with open('mountdir/logging.log', 'a') as fd:
            #fd.write('looping\n')
        # print('looping')
        try :
            Cleanup_tasks()
            Sort_tasks()
            task = Get_First_task()
            if task == None :
                time.sleep(20)
                continue
            print(task[:-1])
            method = json.loads(task[:-1])['Method']
            account = json.loads(task[:-1])['Account']
            scheduled_time = json.loads(task[:-1])['Time']
            result = ""
            ad = ActiveDirectory()
            if method == 'disable' :
                result = ad.Account_disabler(account)
                result = f"[{scheduled_time}] Schedule Task : " + result
            elif method == 'enable' :
                result = ad.Account_enabler(account)
                result = f"[{scheduled_time}] Schedule Task : " + result
            elif method == 'unlock' :
                result = ad.Account_unlocker(account)
                result = f"[{scheduled_time}] Schedule Task : " + result
            else :
                pass
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={MIS_ALERT}&text={result}&parseMode=html"
            req = requests.post(url = url)
            req.close()
            Delete_First_task()
        except Exception as e :
            with open('mountdir/logging.log', 'a') as fd:
                fd.write(f"{e}\n")  
        time.sleep(30)


async def debug(update, context):
    print(update.callback_query.data)

def Activate_bot():
    with open('mountdir/logging.log', 'a') as f:
        f.write('bot start\n')
    start_handler = CommandHandler('start', start)
    ad_handler = CommandHandler('ad', ad)
    expiredate_handler = CommandHandler('expiredate', expiredate)
    unlock_handler = CommandHandler('unlock', unlock)
    disable_handler = CommandHandler('disable', disable)
    enable_handler = CommandHandler('enable', enable)
    reset_handler = CommandHandler('reset', reset)
    schedule_handler = CommandHandler('schedule', schedule)
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(start_handler)
    application.add_handler(CommandHandler("bad_command", bad_command))
    application.add_handler(ad_handler)
    application.add_handler(expiredate_handler)
    application.add_handler(unlock_handler)
    application.add_handler(disable_handler)
    application.add_handler(enable_handler)
    application.add_handler(reset_handler)
    application.add_handler(schedule_handler)
    application.add_handler(CallbackQueryHandler(end, pattern=f"^end$"))
    application.add_handler(CallbackQueryHandler(normal_level1, pattern=f"^(disable|enable|unlock|reset|expiredate)$"))
    application.add_handler(CallbackQueryHandler(normal_level2, pattern=f"^(disable-.*|enable-.*|unlock-.*|reset-.*|expiredate-.*)$"))
    

    application.add_handler(CallbackQueryHandler(schedule_level1, pattern=f"^schedule$"))
    application.add_handler(CallbackQueryHandler(schedule_level2, pattern=f"^schedule_.*$"))
    application.add_handler(CallbackQueryHandler(schedule_level3, pattern=f"^schedule-(disable|enable|unlock)-[0-9a-z\.\_]*$"))
    application.add_handler(CallbackQueryHandler(schedule_level4, pattern=f"^schedule-(disable|enable|unlock)-.*-[0-9][0-9][0-9][0-9]$"))
    application.add_handler(CallbackQueryHandler(schedule_level5, pattern=f"^schedule-(disable|enable|unlock)-.*-[0-9][0-9][0-9][0-9]-[0-9][0-9]$"))
    application.add_handler(CallbackQueryHandler(schedule_level6, pattern=f"^schedule-(disable|enable|unlock)-.*-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]$"))
    application.add_handler(CallbackQueryHandler(schedule_confirm, pattern=f"^schedule-(disable|enable|unlock)-.*-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-[0-2][0-9]:00$"))
    application.add_handler(CallbackQueryHandler(schedule_submit, pattern=f"^schedule-(disable|enable|unlock)-.*-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-[0-2][0-9]:00$"))


    # ...and the error handler
    application.add_error_handler(error_handler)
    application.add_handler(CallbackQueryHandler(debug, pattern=f".*"))

    application.run_polling(allowed_updates=Update.ALL_TYPES)
    

def main():
    print('main')
    process_lists = []
    process_lists.append(mp.Process(target=Activate_bot))
    process_lists[0].start()
    process_lists.append(mp.Process(target=Queue_loop))
    process_lists[1].start()

    for process in process_lists :
        process.join()

if __name__ == '__main__':
    main()


