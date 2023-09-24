import pandas
import easyocr

reader = easyocr.Reader(['en'])


def to_text_tesseract(img) -> pandas.DataFrame:
    import pytesseract

    text = pytesseract.image_to_data(img, output_type=pytesseract.Output.DATAFRAME)
    # Remove NaN
    text = text.dropna()
    # Remove white spaces
    text = text[text.text.map(lambda asd: asd.strip()) != ""]
    return text


def to_text_easyocr(img) -> pandas.DataFrame:
    result = reader.readtext(img)
    return pandas.DataFrame(result, columns=["rect", "text", "conf"])


def to_text(img) -> pandas.DataFrame:
    return to_text_easyocr(img)
