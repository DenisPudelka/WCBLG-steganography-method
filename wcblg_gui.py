from ui.gui import GUI
import mylibpkg
import os

def main():
    eng = mylibpkg.initialize()
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    print("Current Working Directory:", os.getcwd())
    app = GUI(eng)
    app.mainloop()
    eng.terminate()


if __name__ == '__main__':
    main()