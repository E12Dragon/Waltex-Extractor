# Waltex-Extractor
Python script to convert waltex files to png files from the Where's My Water? series of games.

Waltex-Extractor is now archived as it has been made redundant by [WMW-Extractor](https://github.com/E12Dragon/WMW-Extractor). 

# Requirments
Waltex-Extractor needs Pillow and Numpy installed. If you do not already have these libraries installed, you can use the below command.
```
pip install -r requirements.txt
```

# How to use
- Run main.py and select .waltex file to convert.
- Extracted waltex is dumped in a folder called "out" which is created in the same directory as the script.

# Credits
- A big thanks to [campbellsonic](https://github.com/campbellsonic) and [ego-lay-atman-bay](https://github.com/ego-lay-atman-bay) for doing the hard working and creating a script that processes waltex files. 
- Thanks to [LolHacksRule](https://github.com/LolHacksRule) for their noesis script that reads important bytes of waltex files and the "width hack".
