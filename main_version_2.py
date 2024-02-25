from ui.gui import GUI
import mylibpkg


def main():
    eng = mylibpkg.initialize()
    app = GUI(eng)
    app.mainloop()
    eng.terminate()


if __name__ == '__main__':
    main()