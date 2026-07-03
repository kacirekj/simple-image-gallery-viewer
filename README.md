# Sigvie - The Simple Image Gallery Viewer

Sigvie is a simple Python script that one thing well - it displays your images and videos from a local folder in a gallery layout in chronological order, similar to how Google Photos presents your media. With Sigvie, you can quickly browse media files directly from your filesystem in a web browser. Sigvie is ultra simple and small. 

## Demo

![Sigvie demo](demo.jpg) 

![Sigvie demo](demo2.jpg)

## Usage

Start the server:

```bash
python sigvie.py
```

Then handwrite a directory containing images and videos in your browser.

Example:

```text
http://localhost:30000/home/jiri/Pictures
```

On macOS, the path may look like this:

```text
http://localhost:30000/Users/jiri/Pictures
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

For better performance, organize your media into smaller folders and open only the folder you want to browse.


## Notes

Sigvie is intended for local use. It serves files from your local filesystem through a local web server. It contains dependency only to Python Bottle library.
