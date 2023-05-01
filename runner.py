from botik import bot

if __name__ == "__main__":
    while True:
        try:
            print("###Bot started!")
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print(e)