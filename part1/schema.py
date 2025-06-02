### Desired Output Format:


# English JSON Format output

eng_form_template = {
      "lastName": "",
      "firstName": "",
      "idNumber": "",
      "gender": "",
      "dateOfBirth": {
        "day": "",
        "month": "",
        "year": ""
      },
      "address": {
        "street": "",
        "houseNumber": "",
        "entrance": "",
        "apartment": "",
        "city": "",
        "postalCode": "",
        "poBox": ""
      },
      "landlinePhone": "",
      "mobilePhone": "",
      "jobType": "",
      "dateOfInjury": {
        "day": "",
        "month": "",
        "year": ""
      },
      "timeOfInjury": "",
      "accidentLocation": "",
      "accidentAddress": "",
      "accidentDescription": "",
      "injuredBodyPart": "",
      "signature": "",
      "formFillingDate": {
        "day": "",
        "month": "",
        "year": ""
      },
      "formReceiptDateAtClinic": {
        "day": "",
        "month": "",
        "year": ""
      },
      "medicalInstitutionFields": {
        "healthFundMember": "",
        "natureOfAccident": "",
        "medicalDiagnoses": ""
      }
    }


structured_data_prompt_template = """
You are a helpful assistant that extracts structured data from OCR output of Israeli National Insurance Institute forms.

Given this OCR text:
\"\"\"
{raw_text}
\"\"\"

Extract the following fields in JSON format:
{eng_form_template}

Leave missing fields as empty strings. Respond ONLY with JSON format.
"""


# Hebrew JSON Format output

he_form_template = {
      "שם משפחה": "",
      "שם פרטי": "",
      "מספר זהות": "",
      "מין": "",
      "תאריך לידה": {
        "יום": "",
        "חודש": "",
        "שנה": ""
      },
      "כתובת": {
        "רחוב": "",
        "מספר בית": "",
        "כניסה": "",
        "דירה": "",
        "ישוב": "",
        "מיקוד": "",
        "תא דואר": ""
      },
      "טלפון קווי": "",
      "טלפון נייד": "",
      "סוג העבודה": "",
      "תאריך הפגיעה": {
        "יום": "",
        "חודש": "",
        "שנה": ""
      },
      "שעת הפגיעה": "",
      "מקום התאונה": "",
      "כתובת מקום התאונה": "",
      "תיאור התאונה": "",
      "האיבר שנפגע": "",
      "חתימה": "",
      "תאריך מילוי הטופס": {
        "יום": "",
        "חודש": "",
        "שנה": ""
      },
      "תאריך קבלת הטופס בקופה": {
        "יום": "",
        "חודש": "",
        "שנה": ""
      },
      "למילוי ע\"י המוסד הרפואי": {
        "חבר בקופת חולים": "",
        "מהות התאונה": "",
        "אבחנות רפואיות": ""
      }
    }