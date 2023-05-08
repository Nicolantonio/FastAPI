from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse
import io
import cv2
import numpy as np
import uvicorn
import asyncio

app = FastAPI()

def process_image(image_bytes):
    # convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    # decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # process image
    processed_img = cv2.flip(img, 1)
    # encode processed image
    _, img_encoded = cv2.imencode('.jpg', processed_img)
    # convert encoded image to bytes
    result = img_encoded.tobytes()
    return result

async def process_websocket(websocket: WebSocket):
    print("Accepting Connection")
    await websocket.accept()
    print('Accepted')
    while True:
        try:
            image_bytes = await websocket.receive_bytes()
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, process_image, image_bytes)

            await websocket.send_bytes(result)

        except:
            pass
            break
            
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await process_websocket(websocket)

if __name__ == '__main__':
    uvicorn.run("fastApi:app", host='0.0.0.0', port=8000,  workers=4)
