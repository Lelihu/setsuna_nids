import numpy as np
import pickle as pkl
import os.path as path
from waitress import serve
from flask import Flask, request, render_template

# KitNET module
import zKITNET as core
from zGearbox import banner_web, runFE, runKN, plotRMSE_web

banner_web()
UPLOAD_FOLDER = './upload'

app = Flask(__name__, template_folder="./", static_folder='')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods = ['POST'])  
def process():  
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template("error.html", err = "No File Selected")
        
        f = request.files['file']
        
        if f.filename == '':
            return render_template("error.html", err = "No File Selected")
        
        if not f.filename.endswith('pcap') and not f.filename.endswith('pcapng'):
            return render_template("error.html", err = "Invalid file")
             
        f.save(path.join(app.config['UPLOAD_FOLDER'], f.filename))
        dPcap = f.filename
         
        print("\n[***] Setsuna start processing...")
        RunMode = "FLASK"
        PacketFile = path.join(app.config['UPLOAD_FOLDER'], f.filename)
        AutoencoderSize = 10
        ModelFile = "./CIC2017_Benign_merged_5000_10000.pkl"
        graphPath = PacketFile + ".png"
        rmseFig = graphPath
        FE = core.init_FE(PacketFile, np.inf)
        exfeature = runFE(FE)
        rmse = np.array(runKN(core.init_KN_1(ModelFile, np.array(exfeature).shape[1], AutoencoderSize), exfeature))
        
        with open(ModelFile, "rb") as f:
            _ = pkl.load(f)
            _ = pkl.load(f)
            _ = pkl.load(f)
            adth = pkl.load(f)
       
        rangeRmse = np.arange(0, len(rmse), 1)
        plotRMSE_web(RunMode, rmse, rangeRmse, adth, PacketFile, rmseFig)
        graphPath = graphPath.replace("\\", "/")
        return render_template("success.html", name = dPcap, graph = graphPath, adth = adth, rmse = rmse, trmse = len(rmse))
        print("[***] Setsuna end processing...\n")

if __name__ == '__main__':
    #app.debug = True
    app.secret_key = "8e802bc1044a451f1a1fbe62f1b6d884cd3643515b0443ef6a60729419684086"
    serve(app, host="0.0.0.0", port=80)
    #app.run(port=80)