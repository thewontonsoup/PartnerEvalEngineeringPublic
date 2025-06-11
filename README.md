
# pva-uci-data-extraction

Report for UCI-Partner Valuation collaboration on data extraction project

## OpenAI API Key Setup

Create a `.env` file in the root directory with the following line:
`API_KEY = 'openai api key'`

## Instructions (Docker)

Ensure docker-compose is installed on the machine and if not, follow the instructions [here](https://docs.docker.com/compose/install/linux/#install-using-the-repository).
Run the command `docker-compose up -d` the `-d` command puts it in detached mode and this command pulls and runs the containers. This process may take upto 10 minutes if setting up for the first time but anything after that should be less than a minute.  

If you are certain that you have the most up to date images, you can also run `docker-compose start` after ensuring you have the images pulled. This can also be used after the container has been stopped.

To stop the containers, run `docker-compose stop`.

### Build your own

If you would like to modify the code then build your own images, the docker-compose.yml file in the root directory can be modified to use your own built image.

Simply modify the section that says `images` and change it to `build` and add anything required for a successful build. You can now run the same commands with the newest changest available!

If you then want that image to be accessible to others, simply push the docker images to Dockerhub and anyone else running this project can also run your code. REMEMBER to change the `image` section to your own DOckerhub url as `image: yoururl:latest`.

### Speed
Currently, the parameters in `server/src/text_extraction/unstructured_extract.py` has `strategy: 'auto', infer_table_structure: True` which automatically determines whether the PDF contains table like structures that needs longer time to process accurate results. If you are certain the PDF contains only texts, then call the `extract_text` function on line 204 within the `process_pdf_to_draft` function in `/server/src/server.py` with the parameter `strategy: 'fast'`. 
Note that this is HIGHLY NOT RECOMMENDED as valuable informatoin could be lost.

## Instructions (Backend)

### External Libraries Required

1. Tesseract (https://github.com/tesseract-ocr/tesseract)
   - installation: https://tesseract-ocr.github.io/tessdoc/Installation.html
   - tesseract version 5.5.0
   - ensure it is available in the system's path
2. poppler (https://poppler.freedesktop.org/)
   - installation: https://pdf2image.readthedocs.io/en/latest/installation.html (under `installing poppler`)
   - pdftoppm version 25.03.0
   - ensure it is available in the system's path

### Python Requirements

- python 3.12
- pip install -r requirements.txt

If the Error 13 Permission Denied error appears:
1. Verify that the virtual environment activated and set to the local interpreter and not the global one. 
2. Verify that a corrupted cached wheel isn't the causing issue. If this is the case, run `pip install purge` then rerun the commands to reinstall

### Running the Backend

Once the above dependencies are properly installed, **while in the root directory** (the directory containing the server and client folders, this README, etc.), simply use python to run `./server/src/server.py`

When server.py is started (it make take a while to start up), it will display the address which the server is running, typically `http://127.0.0.1:[port]`. To use the server's API endpoints, send requests to the appropritate endpoint on the server, for example `http://127.0.0.1:[port]/upload`. See server.py for more details on the endpoints and what to know for sending and receiving data from said endpoints. If cors errors are encountered, simply open another tab to `http:localhost/5000`to ensure that the backend is running correctly. If the backend endpoints are reachable, the app will run with no errors.

## Instructions (Frontend)

## Prerequisites

Make sure you have **Node.js** and **npm** installed.

```bash
node -v
npm -v
```

Ideally node.js is version 10.9.2 and npm is version v22.14.0

## Built with:

- [React](https://reactjs.org/) – JavaScript library for building UIs
- [React Router DOM](https://reactrouter.com/) – Client-side routing
- [Material UI (MUI)](https://mui.com/) – UI components and icons
- [Emotion](https://emotion.sh/docs/introduction) – CSS-in-JS styling
- [Jest & React Testing Library](https://testing-library.com/) – For testing components

![React](https://img.shields.io/badge/React-19.0.0-blue?logo=react)
![MUI](https://img.shields.io/badge/MUI-v6.4.6-blue?logo=mui)
![React-Router](https://img.shields.io/badge/React--Router-v6.22.1-orange)

## To install dependencies

```bash
cd client
npm install
```

## To run both the frontend and the backend

```bash
cd client
npm start
```

Since the package-lock.json file is located within the client directory, it is important to first cd into the client directory. Then npm start will activate both the frontend server and the backend server, which both need to be activated in order to properly run. The address for the frontend is `http://localhost:3000/`. Please read the comments of the various client/src files on more detail on each files' functionality
