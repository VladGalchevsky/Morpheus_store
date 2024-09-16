import uvicorn

from fastapi import FastAPI
from fastapi.routing import APIRouter

from api.handlers.user_handler import user_router
from api.handlers.order_handlers import order_router
from api.handlers.login_handler import login_router
from api.handlers.product_handler import product_router

# BLOCK WITH API ROUTES #

# create instance of the app
app = FastAPI(title="nnp-university")

# create the instance for the routes
main_api_router = APIRouter()

# set routes to the app instance 
main_api_router.include_router(user_router, prefix="/user", tags=["user"])

main_api_router.include_router(order_router, prefix="/order", tags=["order"])

main_api_router.include_router(login_router, prefix="/login", tags=["login"])

main_api_router.include_router(product_router, prefix="/product", tags=["product"])

app.include_router(main_api_router)

if __name__ == "__main__":
    # run app on the host and port
    uvicorn.run(app, host="localhost", port=8000)
