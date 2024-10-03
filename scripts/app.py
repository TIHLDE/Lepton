import os


def create_app():
    """
    Create a Django app directory with all the necessary directories and files.
    """
    try:
        app_name = input("Enter the app name: ").strip().lower()

        BASE_PATH = "app"

        if app_name in os.listdir(BASE_PATH):
            print(f"App '{app_name}' already exists.")
            return

        app_path = os.path.join(BASE_PATH, app_name)
        
        # Create the app directory
        os.makedirs(app_path, exist_ok=True)

        # Create the app's directories
        init_dir(app_path, "factories")
        init_dir(app_path, "filters")
        init_dir(app_path, "migrations")
        init_dir(app_path, "models")
        init_dir(app_path, "tasks")
        init_dir(app_path, "tests")
        init_dir(app_path, "util")
        init_dir(app_path, "views")
        init_dir(app_path, "serializers")

        # create tests directory
        TESTS_PATH = os.path.join(BASE_PATH, "tests")

        if app_name in os.listdir(TESTS_PATH):
            print(f"App '{app_name}' already exists in 'tests'.")
        else:
            path = os.path.join(TESTS_PATH, app_name)
            os.makedirs(os.path.join(TESTS_PATH, app_name), exist_ok=True)
            init_app_file(path, "__init__.py")

        # Create the app's files
        init_app_file(app_path, "__init__.py")
        init_app_file(app_path, "admin.py")

        config_content = f"""from django.apps import AppConfig

    
class {app_name.capitalize()}Config(AppConfig):
    name = "app.{app_name}"
    """

        init_app_file(app_path, "app.py", content=config_content)
        init_app_file(app_path, "enums.py")
        init_app_file(app_path, "exceptions.py")
        init_app_file(app_path, "mixins.py")
        init_app_file(app_path, "urls.py")

        print(f"App '{app_name}' created successfully.")
        print("Don't forget to add the app to the INSTALLED_APPS in the settings.py file.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        return


def init_dir(app_path: str, dir_name: str):
    """Create a directory in the app directory, with a __init__.py file."""
    dir_path = os.path.join(app_path, dir_name)
    os.makedirs(dir_path, exist_ok=True)
    with open(os.path.join(dir_path, "__init__.py"), "w") as f:
        f.write("")

    
def init_app_file(app_path: str, file_name: str, content: str = ""):
    """Create a file in the app directory."""
    file_path = os.path.join(app_path, file_name)
    with open(file_path, "w") as f:
        f.write(content)
    

if __name__ == "__main__":
    create_app()
