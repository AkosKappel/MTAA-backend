from fastapi import APIRouter, File
from fastapi.responses import FileResponse

router = APIRouter(
    tags=['Files'],
)


@router.get('/downloadfile', response_class=FileResponse)
def download_file():
    # with open('images/' + 'test1.jpg', 'wb') as f:
    #     image = f.read()
    # return {'file_size': len(image)}
    return FileResponse('images/' + 'test1.jpg')


@router.post('/uploadfile/')
def create_upload_file(image: bytes = File(...)):
    with open('images/' + 'test1.jpg', 'wb') as f:
        f.write(image)
    return {'file_size': len(image)}
