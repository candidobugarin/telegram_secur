#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Basic example for a bot that awaits an answer from the user
# This program is dedicated to the public domain under the CC0 license.

import logging, requests, datetime,telegram,folium, time
from selenium import webdriver
from folium import plugins
from telegram import ForceReply, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, filters
#from pyvirtualdisplay import Display

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - ' '%(message)s', level=logging.INFO)

# Define the different states a chat can be in
MENU, AWAIT_CONFIRMATION, AWAIT_INPUT = range(3)

# States are saved in a dict that maps chat_id -> state
state = dict()
# Sometimes you need to save data temporarily
context = dict()
# This dict is used to store the settings value for the chat.
# Usually, you'd use persistence for this (e.g. sqlite).
values = dict()

#display = Display(visible=0, size=(800, 800))
#display.start()

browser = webdriver.Firefox()

# Example handler. Will be called on the /set command and on regular messages
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Olá, '+str(update.message.from_user.first_name)+' '+str(update.message.from_user.last_name)+'!')
    bot.sendMessage(update.message.chat_id, text='Bem Vindo!\nO objetivo deste robô é ajudar os alunos, professores e usuários da Ilha do Fundão na questão da segurança.\n O uso deste robô é bem simples.\n Caso você esteja passando por algum local que considere perigso, basta apertar o botão que diz "/Local Perigoso" e enviar sua localização.\n Esta informação, somada com outras, irão para um mapa que você poderá ver clicando no botão "Mapa".\n Todos os dados que você visualiza no mapa são das últimas 6 horas.', reply_markup=ReplyKeyboardMarkup([[KeyboardButton("/Mapa")],[KeyboardButton("/Local Perigoso")]]))

def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Bem Vindo!\nO objetivo deste robô é ajudar os alunos, professores e usuários da Ilha do Fundão na questão da segurança.\n O uso deste robô é bem simples.\n Caso você esteja passando por algum local que considere perigso, basta apertar o botão que diz "/Local Perigoso" e enviar sua localização.\n Esta informação, somada com outras, irão para um mapa que você poderá ver clicando no botão "Mapa".\nDúvidas?\nSugestões?\nMande um E-Mail para: candidobugarin@gmail.com\n', reply_markup=ReplyKeyboardMarkup([[KeyboardButton("/Mapa")],[KeyboardButton("/Local Perigoso")]]))

def location(bot, update):
    bot.sendMessage(update.message.chat_id, text='Mande sua localização',reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Enviar Localização Atual", request_location=True)]] , one_time_keyboard=True))

def entered_value(bot, update):
    file_contains = open("file.txt","a")
    file_contains.write(""+str(update.message.date)+","+str(update.message.location.latitude)+","+str(update.message.location.longitude)+"\n")
    file_contains.close()
    bot.sendMessage(update.message.chat_id, text='Pronto, você enviou sua localização.\nPara ver o mapa com todas as ocorrências, clique em /Mapa.', reply_markup=ReplyKeyboardMarkup([[KeyboardButton("/Mapa")],[KeyboardButton("/Local Perigoso")]]))

def mapa_p(bot, update):
    bot.sendChatAction(update.message.chat_id, action=telegram.ChatAction.TYPING)
    heat = []
    with open("file.txt","r") as myfile:
        data_p = myfile.read().replace("\n",",").split(",")

    data_p.remove("")

    x = 0
    while x != len(data_p):
        date_format = "%Y-%m-%d %H:%M:%S"
        t1 = datetime.datetime.strptime(data_p[x], date_format)
        data_dif = datetime.datetime.now() - t1
        print(data_dif.days)
        print((data_dif.seconds)/60)
        if data_dif.days == 0 and (data_dif.seconds)/60 < 360:
            heat.append([data_p[x+1],data_p[x+2],data_dif.seconds])
        x += 3

    mapa = folium.Map([-22.934007, -43.356883], tiles='stamentoner', zoom_start=11)
    mapa.add_children(plugins.HeatMap(heat))
    fn='/Users/candidobugarin/Desktop/telegram_proj/testmap.html'
    mapa.save(fn)

    browser.get('file://'+str(fn))
    browser.refresh()
    time.sleep(3)
    browser.save_screenshot('map.png')
    
    bot.sendPhoto(update.message.chat_id, photo=open('map.png','rb'))


# Handler for the /cancel command.
# Sets the state back to MENU and clears the context
def cancel(bot, update):
    chat_id = update.message.chat_id
    del state[chat_id]
    del context[chat_id]

# Create the Updater and pass it your bot's token.
token = ''
updater = Updater(token)

# The command
updater.dispatcher.addHandler(CommandHandler("Local", location))
updater.dispatcher.addHandler(CommandHandler("Mapa", mapa_p))
# The answer and confirmation
updater.dispatcher.addHandler(MessageHandler([filters.LOCATION], entered_value))
updater.dispatcher.addHandler(CommandHandler('cancel', cancel))
updater.dispatcher.addHandler(CommandHandler('start', start))
updater.dispatcher.addHandler(CommandHandler('Ajuda', help))

# Start the Bot
updater.start_polling()

# Run the bot until the user presses Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT
updater.idle()
