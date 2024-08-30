# SQLite database create
from application.route import app, db
app.app_context().push()
db.create_all()
exit()
