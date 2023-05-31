import sys
from LumosWeb.api import API

def main():
    if len(sys.argv) < 3:
        print("Usage: LumosWeb --app <app_name> run")
        return

    if sys.argv[1] != '--app':
        print("Usage: LumosWeb --app <app_name> run")
        return

    app_module = sys.argv[2]
    app = __import__(app_module)
    app_instance = getattr(app, 'app', None)

    if app_instance and isinstance(app_instance, API):
        print(f"Serving Lumos app '{app_module}'")
        app_instance.run_server()
    else:
        print(f"Invalid app file: {app_module}")

if __name__ == '__main__':
    main()
