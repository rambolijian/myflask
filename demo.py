from app_hello import app
from flask import current_app, g, request, session

app_ctx = app.app_context()
app_ctx.push()
print(current_app.name)
app_ctx.pop()