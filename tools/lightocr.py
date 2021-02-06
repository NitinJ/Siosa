from liteocr import OCREngine, load_img, draw_rect, draw_text, disp

image_file = 'Untitled.png'
img = load_img(image_file)

# you can either use context manager or call engine.close() manually at the end.
with OCREngine() as engine:
    # engine.recognize() can accept a file name, a numpy image, or a PIL image.
    for text, box, conf in engine.recognize(image_file):
        print(box, '\tconfidence =', conf, '\ttext =', text)
        draw_rect(img, box)
        draw_text(img, text, box, color='bw')

# display the image with recognized text boxes overlaid
disp(img, pause=False)