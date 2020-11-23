from crawler.big_bang_theory import BigBangTheory as BigBang
from crawler.the_good_doctor import TheGoodDoctor as GoodDoc
from crawler.simpsons import Simpsons

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

app = FastAPI()

@app.get("/big-bang-theory/{season}")
async def get_big_bang_theory(season: int):
    try:
        crawler = BigBang(season, "Big Bang Theory")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"downloaded_episodes": crawler.run().dict()}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)}
        )

"""
@app.get("/the-good-doctor/{season}")
async def get_the_good_doctor(season: int):
    try:
        crawler = GoodDoc(season, "The Good Doctor")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"downloaded_episodes": crawler.run().dict()}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)}
        )
"""

@app.get("/simpsons/{season}")
async def get_simpsons(season: int):
    try:
        crawler = Simpsons(season, "Os Simpsons")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"downloaded_episodes": crawler.run().dict()}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        debug=True,
        log_level="debug"
    )