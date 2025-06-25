import json
import os
import time

import numpy as np
import redis
import settings
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import decode_predictions, preprocess_input
from tensorflow.keras.preprocessing import image

# TODO
# Connect to Redis and assign to variable `db``
# Make use of settings.py module to get Redis settings like host, port, etc.
db = redis.Redis(
    host=settings.REDIS_IP,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB_ID,
    decode_responses=False
)

# TODO
# Load your ML model and assign to variable `model`
# See https://drive.google.com/file/d/1ADuBSE4z2ZVIdn66YDSwxKv-58U7WEOn/view?usp=sharing
# for more information about how to use this model.
model = ResNet50(include_top=True, weights="imagenet")


def predict(image_name):
    """
    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.

    Parameters
    ----------
    image_name : str
        Image filename.

    Returns
    -------
    class_name, pred_probability : tuple(str, float)
        Model predicted class as a string and the corresponding confidence
        score as a number.
    """
    class_name = None
    pred_probability = None
    # TODO: Implement the code to predict the class of the image_name
    try: 
        # Load image
        img_path = os.path.join(settings.IMAGES_FOLDER, image_name)
        # Preprocess the image for ResNet50
        img_array = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img_array)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)  
        # Apply preprocessing (convert to numpy array, match model input dimensions (including batch) and use the resnet50 preprocessing)
        predictions = model.predict(img_array)

        decoded_preds = decode_predictions(predictions, top=1)[0][0]
        # Get predictions using model methods and decode predictions using resnet50 decode_predictions
        _, class_name, pred_probability = decoded_preds
        pred_probability = float(pred_probability)  # Convert to float
        pred_probability = round(pred_probability, 2)  # Round to 2 decimal places

    except Exception as e:
        print(f"Error processing image {image_name}: {e}")
        class_name = "unknown"
        pred_probability = 0.0
    # Convert probabilities to float and round it

    return class_name, pred_probability


def classify_process():
    """
    Loop indefinitely asking Redis for new jobs.
    When a new job arrives, takes it from the Redis queue, uses the loaded ML
    model to get predictions and stores the results back in Redis using
    the original job ID so other services can see it was processed and access
    the results.

    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.
    """
    while True:
        # Inside this loop you should add the code to:
        #   1. Take a new job from Redis
        #   2. Run your ML model on the given data
        #   3. Store model prediction in a dict with the following shape:
        #      {
        #         "prediction": str,
        #         "score": float,
        #      }
        #   4. Store the results on Redis using the original job ID as the key
        #      so the API can match the results it gets to the original job
        #      sent
        # Hint: You should be able to successfully implement the communication
        #       code with Redis making use of functions `brpop()` and `set()`.
        # TODO
        # Take a new job from Redis
        while True:
            try:
                job = db.brpop(settings.REDIS_QUEUE, timeout=0)
                if job is None:
                    continue

                job_data = job[1]  # Get the job data from the tuple returned by brpop
                # Decode the JSON data for the given job
                job_info = json.loads(job_data.decode('utf-8'))

                # Important! Get and keep the original job ID
                job_id = job_info.get("job_id")
                image_name = job_info.get("image_name")


                # Run the loaded ml model (use the predict() function)
                class_name, pred_probability = predict(image_name)
                # Prepare a new JSON with the results
                output = {"prediction": class_name, "score": pred_probability}
                
                # Store the job results on Redis using the original
                db.set(job_id, json.dumps(output))

                print(f"Processed job {job_id}: {output}")
                # job ID as the key
            except Exception as e:
                print(f"Error processing job: {e}")
                if "job_id" in locals():
                    # If job_id exists, store an error message
                    output = {"prediction": "error", "score": 0.0}
                    db.set(job_id, json.dumps(output))
                    print(f"Stored error for job {job_id}: {output}")

        # Sleep for a bit
        time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main__":
    # Now launch process
    print("Launching ML service...")
    classify_process()
