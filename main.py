import json
import os
import quart
from quart_cors import cors
from quart import request
from quart import Quart
from youtube_search import YoutubeSearch
from pytube import YouTube
import subprocess
from sympy import sympify
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import pathlib
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random

app = Quart(__name__, static_folder='assets')
app = cors(app, allow_origin="https://chat.openai.com")

@app.get("/command/<path:command>")
async def run_command(command):
    print("command was called")
    try:
        # get the output of the command that was run using username var
        output = subprocess.check_output(command, shell=True, text=True)
        print(output,command)
        #debug check if output exists
        if(output.replace(" ","")==""):
            output="command completed with no output but ran fine"
        output=output.replace("\\","/")
        return quart.Response(response=output, status=200)
    except subprocess.CalledProcessError as e:
        return quart.Response(response=str(e), status=500)

@app.get("/listdir/<path:directory>")
async def get_files(directory):
    print("file was called")
    if not os.path.isdir(directory):
        return quart.Response(response="Directory not found", status=404)
    filesandfolders=[]
    for filename in os.listdir(directory):
        filesandfolders.append(filename)
    return quart.Response(response=json.dumps(filesandfolders), status=200)

@app.get("/filecreate/<path:directory>/<string:filename>/<path:filecontent>")
async def append_file(directory, filename, filecontent):
    print(r"file was called")
    with open(directory+"/"+filename, "a") as f:
        f.write(filecontent)
    f.close()
    return quart.Response(response="file created", status=200)
    
@app.get("/fileread/<path:filepath>")
async def read_file(filepath):
    print(r"read file was called")
    try:
        with open(filepath, "r") as f:
            filecon=f.read()
        f.close()
        if not filecon:
            return quart.Response(response="File is empty", status=400)
        return quart.Response(response=filecon, status=200)
    except FileNotFoundError:
        return quart.Response(response="File not found", status=404)
    except Exception as e:
        return quart.Response(response=str(e), status=500)

@app.get("/calculate_equation/<path:input>")
async def calculate(input):
    print(r"calculate was called")
    try:
        a=sympify(input)
        return quart.Response(response=str(a), status=200)
    except Exception as e:
        return quart.Response(response=str(e), status=500)

@app.get("/plot/<string:equation>")
async def plot_equation(equation: str):
    try:
        plt.figure()
        # create the range of x values
        x = np.linspace(-10, 10, 400)

        # safely evaluate the equation
        y = eval(equation)

        # generate the plot
        plt.plot(x, y)
        plt.title(f"Plot of {equation}")

        # check if assets directory exists, if not create it
        if not os.path.exists('assets'):
            os.makedirs('assets')

        # create a unique filename for the image
        file_name = f"plot_{hash(equation)}.png"
        file_path = os.path.join('assets', file_name)

        # save the image
        plt.savefig(file_path)

        # close the plot to free up memory
        plt.close()

        return quart.Response(response=json.dumps({"file": f"http://localhost:5003/assets/{file_name}"}), status=200)
    except Exception as e:
        return quart.Response(response=str(e), status=500)

@app.get("/3dplot/<int:num_points>/<path:equation>/<string:x_range>/<string:y_range>")
async def create_plot(num_points, equation, x_range, y_range):
    try:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        x_range = [float(x) for x in x_range.replace("[","").replace("]","").split(',')]
        y_range = [float(y) for y in y_range.replace("[","").replace("]","").split(',')]
        
        x = np.linspace(x_range[0], x_range[1], num_points)
        y = np.linspace(y_range[0], y_range[1], num_points)
        X, Y = np.meshgrid(x, y)
        Z = eval(equation)  # Evaluate the equation for each (x, y) pair

        ax.plot_surface(X, Y, Z, cmap='viridis')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        save_dir = "./assets/3Dplots"
        os.makedirs(save_dir, exist_ok=True)
        random_value = random.randint(0, 1000)
        save_path = os.path.join(save_dir, f"plot-{random_value}.png")
        plt.savefig(save_path)
        return quart.Response(response=json.dumps({"file": f"http://localhost:5003/assets/3Dplots/plot-{random_value}.png"}), status=200)
    except Exception as e:
        return quart.Response(response=str(e), status=500)

@app.get("/download_youtube/<path:name_or_list>")
async def youtubedownload(name_or_list):

    querys = name_or_list.split(",")
    for query in querys:
        download_path = "./assets"
        # Set the download path
        # Search for the video
        results = YoutubeSearch(query, max_results=1).to_dict()
        video_info = results[0]
        video_url = f"https://www.youtube.com{video_info['url_suffix']}"
        # Download the video
        print(f"Downloading video: '{video_info['title']}'")
        yt = YouTube(video_url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        if stream is not None:
            stream.download(download_path)
            print(f"Video downloaded at: '{download_path}'")
        else:
            print("No suitable stream found.")
    print(r"youtubedownload was called")
    return quart.Response(response="done playlist location: " + str(pathlib.Path().resolve()) + "\\assets\\", status=200)

@app.get("/playvideos/<path:termspec>")
async def playvideo(termspec):
    print(r"playvideo was called")
    os.system("start " + "vlc " + "\\assets")
    return quart.Response(response="done", status=200)

@app.get("/clearplaylist/<path:amount>")
async def clear_playlist(amount):
    print(r"clearplaylist was called")
    if amount=="all":
        files_to_remove = [f for f in os.listdir("./assets") if os.path.join("./assets", f) != "./assets/3Dplots" and os.path.isfile(os.path.join("./assets", f))]
        amount = len(files_to_remove)
        for i in range(amount):
            os.remove(os.path.join("./assets", files_to_remove[0]))
    else:
        amount=int(amount)
        files_to_remove = [f for f in os.listdir("./assets") if os.path.join("./assets", f) != "./assets/3Dplots" and os.path.isfile(os.path.join("./assets", f))]
        for i in range(min(amount, len(files_to_remove))):
            os.remove(os.path.join("./assets", files_to_remove[i]))
    return quart.Response(response="done", status=200)

@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")




def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()