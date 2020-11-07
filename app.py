from crawler.big_bang_theory import BigBangTheory as BBT

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/big-bang-theory/{season}")
async def get_big_bang_theory(season: int):
    try:
        crawler = BBT(season)
        return crawler.run()
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