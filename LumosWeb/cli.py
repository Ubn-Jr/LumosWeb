import sys
import os
from LumosWeb.api import API  # Import the API class


def main():
    if len(sys.argv) < 4 or sys.argv[1] != "--app":
        print("Usage: Lumosweb --app <module_name> run")
        return

    app_module = sys.argv[2]
    app_path = os.path.abspath(os.path.join(os.getcwd(), app_module + ".py"))
    app_directory = os.path.dirname(app_path)
    
    if os.path.exists(app_path):
        sys.path.append(app_directory)  # Add app directory to the system path
        
        with open(app_path, "r") as file:
            code = compile(file.read(), app_path, "exec")
            namespace = {}
            exec(code, namespace)
            app = None
            for obj in namespace.values():
                if isinstance(obj, API):
                    app = obj
                    break
            if app is not None:
                app.run()
            else:
                raise AttributeError(f"No instance of 'API' found in module: {app_module}")
    else:
        raise ImportError(f"Failed to import app module: {app_module}")

if __name__ == "__main__":
    main()
