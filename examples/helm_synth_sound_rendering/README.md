# DawDreamer - Multiprocessing Plugins (with free VST Synth: Helm)

This script demonstrates how to use [multiprocessing](https://docs.python.org/3/library/multiprocessing.html) to efficiently generate one-shots of a synthesizer. In this specific script and notebook, we happen to use [Helm](https://tytel.org/helm/) VST synthesizer, a free open-source VST synthesizer that has a vast array of JSON-formatted presets. With the `helm_utils` module, we can load the key-parameter paris in a `.helm` preset file along with the `set_parameter()` method in DawDreamer to apply the settings from the JSON to the synthesizer.

The number of workers is by default `multiprocessing.cpu_count()`. Each worker has a persistent RenderEngine which loads a plugin instrument of our choice. Each worker consumes paths of presets from a multiprocessing [Queue](https://docs.python.org/3/library/multiprocessing.html#pipes-and-queues). For each preset, the worker renders out audio for a configurable MIDI pitch range. The output audio path includes the pitch and preset name.

To run a CLI example that produces many sounds in parallel with the TAL-U-NO-LX VST plugin using multiprocessing, you may adjust and run the following: 

```bash
python main.py --plugin "path/to/helm_plugin" --preset-dir "path/to/helm_presets"
```

After you download Helm, you can find the plugin/preset locations for your OS listed [here](https://tytel.org/helm/faq/) on the Helm FAQ page.

To see all available parameters:
```bash
python main.py --help
```


Alternatively, you can also run `main.py` directly in VS Code by pasting the `launch.json` file in this folder in your `.vscode` folder which should be located in the root of the repository. Then you can simply click the `Run and Debug` icon in the left sidebar, and select `DawDreamer Helm Test`, and run!
