from fastapi import FastAPI
from dfhc.app.core.database import engine, Base
from dfhc.app.routes import users, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title='Detroit Family Home Care API',
    version='0.1.0',
    description='Backend API for DFHC caregiver management',
)

app.include_router(users.router, prefix='/users', tags=['users'])
app.include_router(auth.router, prefix='/auth', tags=['auth'])

@app.get('/health')
def health_check():
    return {'status': 'ok', 'service': 'dfhc-api'}
