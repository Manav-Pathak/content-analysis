import uvicorn

if __name__ == "__main__":
    # Local fallback entrypoint. Docker Compose is the primary workflow.
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
