# SetsunaIDS
SetsunaIDS (Setsuna) is an unsupervised network intrusion detection system based on [Kitsune/KitNET (NDSS '18)](https://github.com/ymirsky/Kitsune-py). The plug-and-play, unsupervised and scalable features allow it to be deployed in a single-board computer like the Raspberry Pi and detect abnormal traffic.

## Implementation Notes

1. Copy the repo.
2. Install dependencies using `pip install -r requirements.txt`.
The necessary dependencies are as follows:
```
Cython==0.29.25
matplotlib==3.5.0
numpy==1.21.2
pandas==1.3.5
paramiko==2.8.1
scipy==1.7.3
```
3. Compile the AfterImage using `python setup.py build_ext --inplace`.
4. You are good to go.

### Tshark issue
For windows, install [Wireshark](https://www.wireshark.org/). Copy `tshark.exe` to `tsk` folder.
For Linux, install 'tshark' from using package management like `apt` and `yum`.

## Usage
You need to prepare a normal data (i.e., benign traffic) and an abnormal data (i.e., abnormal traffic). To see where you can get dataset, click [here](#Dataset). For additional information of each program, you can use `-h` to get the usage.

### Feature extration
To get the faetures of a captured network packet only, you can use `expm_runFE.py`. It outputs the features in NPY format.
`python .\setsuna_fe.py -i benign.pcapng`

### Train
Run `python .\setsuna_cli.py -r train -f .\train.npy -m .\model.pkl -ae 10 -fg 10000 -ag 50000`
The `.pkl` file is the trained data plug-into the Setsuna for abnormal network traffic detection. Normally, autoencoder size and relevant parameters should remain unchanged. Details may recall the [Kitsune/KitNET (NDSS '18)](https://github.com/ymirsky/Kitsune-py).

### Execute
Execute the Setsuna with benign model and abnormal features.
`python .\setsuna_cli.py -r exec -f .\abnormal.npy -m .\model.pkl -ae 10`

### Hybrid
Hybrid mode execute the Setsuna with benign model and captured network packet.
The captured network packet can be either a normal data or abnormal data.
`python .\setsuna_cli.py -r hybrid -p .\network_captures.pcap -m .\model.pkl -ae 10`

### Web Interface
The web interface allows you to upload the network packet file (PCAP/PCAPNG) for Setsuna to perform abnormal traffic detection using Hybird mode. You can run the Setsuna GUI via `run_setsuna_web` or `python .\setsuna_webgui.py`. The webgui can be accessed via 127.0.0.1:80 (if you are running it locally).

## Dataset
You may use this [dataset](https://goo.gl/iShM7E) provided by [ymirsky/Kitsune-py (NDSS '18)](https://github.com/ymirsky/Kitsune-py).
You can also use other dataset that is suitable for Setsuna, such as [UNB](https://unb.ca/cic/datasets/).

## References
*Yisroel Mirsky, Tomer Doitshman, Yuval Elovici, and Asaf Shabtai, "Kitsune: An Ensemble of Autoencoders for Online Network Intrusion Detection", Network and Distributed System Security Symposium 2018 (NDSS'18), GitHub [ymirsky/Kitsune-py](https://github.com/ymirsky/Kitsune-py.)*

*D. Han et al., "Evaluating and Improving Adversarial Robustness of Machine Learning-Based Network Intrusion Detectors," in IEEE Journal on Selected Areas in Communications, doi: 10.1109/JSAC.2021.3087242, GitHub [dongtsi/TrafficManipulator](https://github.com/dongtsi/TrafficManipulator)*

## Point of notes
*The information above may be updated accordingly.*
