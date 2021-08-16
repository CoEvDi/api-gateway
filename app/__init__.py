from fastapi import FastAPI, Request, Response

#from .config import YamlConfigManager
#from .config import cfg
#from .errors import exception_handlers


#ConfigManager = YamlConfigManager(interval=60)

app = FastAPI()#exception_handlers=exception_handlers)


@app.on_event('startup')
async def startup():
    #await ConfigManager.start(cfg)

    from .router import router
    app.include_router(router)


