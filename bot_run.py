from bot import start_bot


if __name__ == '__main__':
    while True:
        try:
            start_bot()
        except KeyboardInterrupt:
            break
        except Exception as ex:
            print(ex)
