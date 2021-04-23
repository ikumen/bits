import os
import dotenv

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse, JSONResponse
from starlette.routing import Route

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
dotenv.load_dotenv(dotenv_path)


from mainapp.datastore import bits_collection



print(f"====> {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")


async def get_status(req):
    """Returns 'OK' if app is up and running."""
    return PlainTextResponse(content="OK")

async def list_bits(req):
    return bits_collection.all()

app = Starlette(
    debug=False, 
    routes=[
        Route("/status", get_status),
        Route("/api/bits", list_bits)
    ])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=5000, reload=True, log_level='info')
