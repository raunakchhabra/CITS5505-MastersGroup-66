from app import create_app
from app.extensions import db
from app.models import User, Data, SharedData, DataType, SharedPermission

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Data': Data,
        'SharedData': SharedData,
        'DataType': DataType,
        'SharedPermission': SharedPermission
    }

if __name__ == '__main__':
    app.run(debug=True)
