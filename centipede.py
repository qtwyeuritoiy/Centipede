# Copyright (c) 2017, Jihoon Kim
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of the FreeBSD Project.

# This library downloads EVERY conversation(except stickers & images) in a certain group.
# Due to how Telegram is designed, this script cannot obtain conversations in an encrypted chat.
# Requirements: Python 3, telethon library(pip install telethon)
# Obtain API ID/hash via registering the application to the Telegram.
# You need access to your phone number you have registered your Telegram account with.

from telethon import TelegramClient
from telethon.tl.types import Message
from telethon.utils import get_display_name
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import datetime, timedelta
import time

class Centipede:
    def __init__(self, api_id, api_hash, phone_num, target_index=None):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_num = phone_num
        self.target_index = target_index

    def connect(self):
        self.client = TelegramClient('session_id', self.api_id, self.api_hash)
        if not self.client.connect():
            print("Connection Failed")
            return False
        if not self.client.is_user_authorized():
            self.client.send_code_request(self.phone_num)
            self.client.sign_in(self.phone_num, input('Enter code: '))
        return True

    def get_entity(self):
        dialogs = self.client.get_dialogs(limit=None)
        if self.target_index is not None:
            self.entity = dialogs[self.target_index].entity
            return
        i = None
        while i is None and self.target_index is None:
            for i, dialog in enumerate(dialogs, start=1):
                print('{}. {}'.format(i, get_display_name(dialog.entity)))
            i = input('Enter dialog ID: ')
            try:
                i = int(i if i else 0) - 1
                # Ensure it is inside the bounds, otherwise retry
                if not 0 <= i:
                    i = None
            except ValueError:
                i = None
        self.entity = dialogs[i].entity
        

    def write_to_file(self, messages):
        output = open(get_display_name(self.entity)+'-telegram-logs.csv', 'w')
        count = 1
        for msg in reversed(messages):
            message = msg.message
            sender_id = get_display_name(msg.sender)
            date = msg.date.strftime("%Y%m%dT%H%M%SZ") #Specify datetime according to ISO 8601 standard.
            if message and sender_id is not None:
                count += 1
                output.write(date+","+sender_id+',"'+message.replace('"', '""')+'"\n')
        output.close()
        print ("%d text-only messages exported."%count)

    def run(self):
        if not self.connect():
            return
        self.get_entity()
        messages = self.client.get_message_history(self.entity, limit=1)
        sec = timedelta(seconds=int(messages.total/100))
        d = datetime(1,1,1)+ sec
        print("Retreiving "+str(messages.total)+" messages in a given conversation...")
        print("This may take a long time depending on the size of its history.")
        print("Approximate processing time would be at least %d hours %d minutes and %d seconds." % ((d.day-1)*24+d.hour, d.minute, d.second))
        print("Please wait...")
        messages = self.client.get_message_history(self.entity, limit=None)
        print("Successfully retreived "+str(len(messages)) +" messages.")
        print("Now writing...")
        self.write_to_file(messages)


#Centipede(api_id, api_hash, phone_num, target_index(optional)).run()
