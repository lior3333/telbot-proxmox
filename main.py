import telebot
from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from dotenv import load_dotenv
from proxmoxer.core import ResourceException
import logging
from logging.handlers import RotatingFileHandler
from handler_shutdown import shutdown_host

load_dotenv()
import time
LOG_FILE = "bot.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        RotatingFileHandler(
            LOG_FILE,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=5
        ),
        logging.StreamHandler()  # גם למסך
    ]
)

logger = logging.getLogger("telbot_proxmox")

from proxmox_client import ProxmoxClient
from config import (
    TELEGRAM_BOT_TOKEN,
    ALLOWED_USERS,
    MAIN_MENU,
    WAIT_VM_ID,
    CONFIRM_ACTION
)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
px = ProxmoxClient()
ALLOWED_USERS = ALLOWED_USERS





def init_user(chat_id):
    if chat_id not in users:
        users[chat_id] = {
            "state": MAIN_MENU,
            "data": {}
        }

users = {}

def show_main_menu(chat_id):
    users[chat_id]["state"] = MAIN_MENU

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("SHOW VMS", "Stop VM", "Start VM", "Get vm Status", "Show lXC","Show Running")

    bot.send_message(
        chat_id,
        "תפריט ראשי – בחר פעולה:",
        reply_markup=markup
    )


def get_vm(px):
    STATUS_ICON = {
        "running": "🟢",
        "stopped": "🔴",
        "paused": "🟡",
    }

    vms = px.list_vms()
    lines = []

    header = f"{'':<2} {'VMID':<6} {'NAME':<35} STATUS"
    lines.append(header)
    lines.append("-" * len(header))

    for vm in vms:
        icon = STATUS_ICON.get(vm["status"], "⚪")
        name = vm["name"][:35]
        lines.append(
            f"{icon:<2} {vm['vmid']:<6} {name:<35} {vm['status']}"
        )

    table = "\n".join(lines)
    return f"{table}"
   
def handle_show_running_resources(message, px):
    chat_id = message.chat.id

    try:
        running = px.list_running_resources()

        if not running:
            bot.send_message(chat_id, "🟢 אין משאבים פעילים כרגע")
            return

        lines = []
        for r in running:
            icon = "🖥️" if r["type"] == "vm" else "📦"
            lines.append(
                f"{icon} {r['type'].upper()} {r['vmid']}  {r['name']}"
            )

        msg = "\n".join(lines)
        bot.send_message(chat_id, msg)

    except Exception as e:
        bot.send_message(chat_id, f"❌ שגיאה: {e}")


def handle_show_lxc(message, px):
    chat_id = message.chat.id

    try:
        lxc = px.list_lxc()

        if not lxc:
            bot.send_message(chat_id, "📦 אין LXC containers")
            return

        msg = "\n".join(
            f"{ct['vmid']}  {ct['name']}  {ct['status']}"
            for ct in lxc
        )

        bot.send_message(chat_id, msg)

    except Exception as e:
        bot.send_message(chat_id, f"❌ שגיאה: {e}")




def handle_vm_id(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if not text.isdigit():
        bot.send_message(chat_id, "אנא הזן מספר VM תקין")
        return

    vm_id = int(text)
    action = users[chat_id]["data"].get("action")

    users[chat_id]["data"]["vm_id"] = vm_id

    try:
        # ---- פעולה מיידית ----
        if action == "status":
            handle_vm_status(message, px)
            return

        # ---- פעולות שדורשות אישור ----
        if action in ("start", "stop"):
            users[chat_id]["state"] = CONFIRM_ACTION

            kb = ReplyKeyboardMarkup(
                resize_keyboard=True,
                one_time_keyboard=True
            )
            kb.row(
                KeyboardButton("✅ Yes"),
                KeyboardButton("❌ No")
            )

            bot.send_message(
                chat_id,
                f"האם אתה בטוח שברצונך לבצע {action} על VM {vm_id}?",
                reply_markup=kb
            )
            return

        bot.send_message(chat_id, "פעולה לא מוכרת")
        users[chat_id]["data"] = {}
        show_main_menu(chat_id)

    except Exception as e:
        bot.send_message(chat_id, f"❌ שגיאה: {e}")
        users[chat_id]["data"] = {}
        show_main_menu(chat_id)




def handle_vm_status(message, px):
    chat_id = message.chat.id
    vm_id = users[chat_id]["data"]["vm_id"]
    try:
        status = px.get_vm_status(vm_id)

        bot.send_message(
            chat_id,
            f"ℹ️ סטטוס VM {vm_id}: {status}"
        )
    except ResourceException as e:
        bot.send_message(chat_id, f"❌ שגיאת Proxmox: {e}")

    except Exception as e:
        bot.send_message(chat_id, f"❌ שגיאה כללית: {e}")
    
    finally:
            users[chat_id]["data"] = {}
            show_main_menu(chat_id)



def handle_vm_confirm(message, px):
    chat_id = message.chat.id
    text = message.text.lower()
    YES_VALUES = ("yes", "✅ yes", "✅ Yes")
    NO_VALUES  = ("no",  "❌ no",  "❌ No")
    data = users[chat_id].get("data", {})
    action = data.get("action")

    # פעולות שדורשות אישור yes/no
    if action in ("shutdown_host", "start", "stop"):
        if text not in YES_VALUES + NO_VALUES:
            bot.send_message(chat_id, "ענה yes או no")
            return

        if text in NO_VALUES:
            bot.send_message(chat_id, "בוטל")
            users[chat_id]["data"] = {}
            show_main_menu(chat_id)
            return

    try:
        # ===== SHUTDOWN HOST =====
        if action == "shutdown_host":
            running = px.list_running_resources()

            if running:
                lines = []
                for r in running:
                    icon = "🖥️" if r["type"] == "vm" else "📦"
                    lines.append(
                        f"{icon} {r['type'].upper()} {r['vmid']}  {r['name']}"
                    )

                msg = (
                    "⚠️ יש משאבים פעילים, לא ניתן לכבות:\n\n"
                    + "\n".join(lines)
                )
                bot.send_message(chat_id, msg)
                return

            logger.critical("SHUTDOWN HOST requested by user %s", chat_id)
            bot.send_message(
                chat_id,
                "⏻ השרת נכבה כעת. החיבור יתנתק."
            )
            shutdown_host()
            return

        # ===== VM ACTIONS =====
        elif action in ("start", "stop"):
            vm_id = data.get("vm_id")
            if not vm_id:
                bot.send_message(chat_id, "❌ VM ID חסר")
                return

            if action == "stop":
                px.stop_vm(vm_id)
                time.sleep(2)
                logger.info("STOP VM %s by user %s", vm_id, chat_id)
                status = px.get_vm_status(vm_id)
                if status == "stopped":
                    bot.send_message(chat_id, "✅ ה־VM נכבה")
                else:
                    bot.send_message(
                        chat_id,
                        "⚠️ נשלחה בקשה לכיבוי, אך ה־VM עדיין פעיל"
                    )

            elif action == "start":
                px.start_vm(vm_id)
                time.sleep(2)
                status = px.get_vm_status(vm_id)
                if status == "running":
                    logger.info("START VM %s by user %s", vm_id, chat_id)
                    bot.send_message(chat_id, "✅ ה־VM נדלק")
                else:
                    bot.send_message(
                        chat_id,
                        "⚠️ נשלחה בקשה להדלקה, אך ה־VM עדיין לא רץ"
                    )

        else:
            bot.send_message(chat_id, "פעולה לא מוכרת")

    except ResourceException:
        bot.send_message(
            chat_id,
            "❌ המשאב לא קיים או שלא ניתן לבצע עליו פעולה"
        )

    except Exception as e:
        bot.send_message(chat_id, f"❌ שגיאה כללית: {e}")

    finally:
        users[chat_id]["data"] = {}
        show_main_menu(chat_id)



def handle_main_menu(message): 
    chat_id = message.chat.id
    text = message.text
    if text == "SHOW VMS":
        bot.send_message(chat_id, get_vm(px),parse_mode="Markdown") 
        return

    if text == "Stop VM":
        users[chat_id]["data"] = {"action": "stop"}
        users[chat_id]["state"] = WAIT_VM_ID
        bot.send_message(chat_id, "הכנס VM ID לכיבוי:")
        return

    if text == "Start VM":
        users[chat_id]["data"] = {"action": "start"}
        users[chat_id]["state"] = WAIT_VM_ID
        bot.send_message(chat_id, "הכנס VM ID להדלקה:")
        return
    if text == "Get vm Status":
        users[chat_id]["data"] = {"action": "status"}
        users[chat_id]["state"] = WAIT_VM_ID
        bot.send_message(chat_id, "הכנס VM ID לבדיקת סטטוס:")
        return
    
    if text == "Show lXC":
        handle_show_lxc(message,px)
        return
    if text == "Show Running":
        handle_show_running_resources(message, px)
        return

    
    if text == "Shutdown Host":
        users[chat_id]["data"] = {"action": "shutdown_host"}
        users[chat_id]["state"] = CONFIRM_ACTION
        bot.send_message(
        chat_id,
        "⚠️ אתה עומד לכבות את השרת עצמו!\n"
        "האם אתה בטוח? (yes/no)"
    )
        return



@bot.message_handler(commands=['start'])
def start(message):
    init_user(message.chat.id)
    show_main_menu(message.chat.id)

@bot.message_handler(func=lambda m: True)
def router(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if user_id not in ALLOWED_USERS:
        bot.send_message(
            chat_id,
            "❌ אין לך הרשאה להשתמש בבוט הזה"
        )
        return
    
    if chat_id not in users:
        bot.send_message(
            chat_id,
            "ברוך הבא 👋\nכדי להתחיל, שלח /start"
        )
        return
    
    state = users[chat_id]["state"]

    if state == "MAIN_MENU":
        handle_main_menu(message)

    elif state == "SHOW_VMS":
        handle_vm_show(message)

    elif state == "CONFIRM_ACTION":
        handle_vm_confirm(message,px)

    elif state == "WAIT_VM_ID":
        handle_vm_id(message)
    else:
        bot.send_message(chat_id, "מצב לא ידוע, חוזר לתפריט")
        show_main_menu(chat_id)


bot.infinity_polling()