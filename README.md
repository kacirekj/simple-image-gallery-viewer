# Sigvie - The Simple Image Gallery Viewer

Sigvie is a small Python script that displays images and videos from a local folder, recursively and in a chronological gallery layout, giving you a simple Google Photos-like view of your local media directly in the browser. Sigvie follows the Unix philosophy: do one thing well - for editing tags and other things, use a different complementary software.

## Demo

![Sigvie demo](doc/demo.jpg) 

![Sigvie demo](doc/demo1.jpg)

![Sigvie demo](doc/demo2.jpg)

## Installation

Install with `pipx` (recommended):

```bash
pipx install sigvie
```

Or install with `pip3`:

```bash
pip3 install sigvie
```

## Usage

Start the server on default port 30255:

```bash
sigvie
```

You can also choose a custom port:

```bash
sigvie --port 30255
```

Then open Sigvie in your browser:

```text
http://localhost:30255
```

Enter the path to a directory containing images and videos into the input box at the top of the page.

Example on Linux:

```text
/home/jiri/Pictures
```

Example on macOS:

```text
/Users/jiri/Pictures
```

## Controls

Use your browser zoom controls to change how many items are visible on the page:

```text
Ctrl+    zoom in
Ctrl-    zoom out
```

On a touchpad, use pinch-to-zoom to zoom individual images or adjust the page view, depending on your browser and system settings.

## Performance Notes

If a directory contains too many media files, especially thousands of images or videos, the page may become slow or laggy. 
This is limitation of the browser and hardware you use.

For better performance, organize your media into smaller folders (e.g. Family, Web, Memes) and open only the folder you want to browse.

## How it works

When you enter the directory path, the Sigvie will recursively display all the images in the dicrectory and all subdirectoris. (Exactly as Google Photos does it).
Sigvie will display the images and videos in chronological order based on the "Created" and "Modified" file attributes (Tha smaller value of these 2 wins). 
To keep things simple, Sigvie intentionally doesn't consider image or video tags but uses only file attributes.

## Notes

Sigvie is intended for local use. It serves files from your local filesystem through a local web server. It contains dependency only to Python Bottle library.
