from fastapi import FastAPI

app = FastAPI()

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "message": "REST API pertama berhasil berjalan!"
    }