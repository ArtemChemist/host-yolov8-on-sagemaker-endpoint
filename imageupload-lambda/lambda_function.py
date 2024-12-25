import boto3, random, base64, json, io
from PIL import Image, ImageDraw, ImageFont

def str_to_im(encoded_str):
    aux_path = '/tmp/tmp.png'
    with open(aux_path, 'wb') as f:
        f.write(base64.b64decode(encoded_str))
        f.close
    return Image.open(aux_path)

def im_to_str(PIL_im):
    # Convert the image with boxes a byte stream 
    byte_arr = io.BytesIO()
    PIL_im.save(responce_byte_arr, format='jpeg')
    return base64.b64encode(byte_arr.getvalue()).decode('utf-8')
    
    with open(aux_path, 'rb') as f:
        encoded_im = base64.b64encode(f.read())
        f.close
    return encoded_im.decode('utf-8')

def lambda_handler(event, context):
    ENDPOINT_NAME = 'YOLOv8-CFU-SageMaker-endpoint'
    
    # Read the image into a numpy array
    # orig_image = Image.open('cfu_positive.jpg')
    orig_image = str_to_im(event['body'])
    
    # Calculate the parameters for image resizing
    image_height, image_width = orig_image.size
    model_height, model_width = 640, 640
    x_ratio = image_width/model_width
    y_ratio = image_height/model_height
    resizedImage = orig_image.resize((model_height, model_width), Image.Resampling.LANCZOS)
    
    # Convert the image to the jpeg and save the jpeg as a byte stream 
    img_byte_arr = io.BytesIO()
    resizedImage.save(img_byte_arr, format='jpeg')

    # Convert tyhe bytes intoe base64
    payload = base64.b64encode(img_byte_arr.getvalue())
    
    runtime= boto3.client('runtime.sagemaker')
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME,
                                            ContentType='text/csv',
                                            Body=payload)
    response_body = response['Body'].read()
    result = json.loads(response_body.decode('ascii'))

    # Draw the boxes on the original image
    if 'boxes' in result:
        draw = ImageDraw.Draw(orig_image)
        for idx,(x1,y1,x2,y2,conf,lbl) in enumerate(result['boxes']):
            # Draw Bounding Boxes
            x1, x2 = int(x_ratio*x1), int(x_ratio*x2)
            y1, y2 = int(y_ratio*y1), int(y_ratio*y2)
            color = (random.randint(10,255), random.randint(10,255), random.randint(10,255))
            draw.rectangle(((x1,y1), (x2,y2)), outline = color)
            draw.text((x1,y1-40), f"Class: {int(lbl)}")
            draw.text((x1,y1-10), f"Conf: {int(conf*100)}")
    
    im_to_return = array_to_str(orig_image)
            
    return {
        'statusCode': 200,
        'body': im_to_return,
        'isBase64Encoded': True,
        'headers': {'content-type':'image/png'}
    }