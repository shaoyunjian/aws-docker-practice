from flask import *
import boto3
from botocore.exceptions import NoCredentialsError
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()
from mysql.connector.pooling import MySQLConnectionPool

MYSQL_HOSTNAME = os.getenv("MYSQL_HOSTNAME")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USERNAME = os.getenv("MYSQL_USERNAME")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
CLOUDFRONT_URL = os.getenv("CLOUDFRONT_URL")

pool = MySQLConnectionPool(
  pool_name = "mypool",
  pool_size = 10,
  host = MYSQL_HOSTNAME,
  port = MYSQL_PORT, 
  user = MYSQL_USERNAME, 
  password = MYSQL_PASSWORD, 
  database= MYSQL_DATABASE
)

app = Flask(__name__)

# ---------------------------------------------

@app.route("/")
def index():
  return render_template("index.html")

# ---------------------------------------------

@app.route("/api/file", methods=["POST"])
def upload_file():
  file = request.files["file"]
  message = request.form["message"]
  now = datetime.now()
  edited_filename = datetime.strftime(now, "%Y%m%d%H%M%S")
 
  # Set up an S3 client
  s3 = boto3.client(
    "s3", 
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key = os.getenv("AWS_SECRET_KEY")
  )

  try:
    if file and message:
      # Upload the file to S3
      s3.upload_fileobj(
        file, 
        "sparkles-bucket", 
        edited_filename,
        ExtraArgs = {
          "ACL": "public-read",
          "ContentType": file.content_type
        }
      )      
      try:
        connection = pool.get_connection()
        cursor = connection.cursor()
        sql = """
          INSERT INTO `my_page`(`image_url`, `message`) VALUES (%s, %s)
        """
        value = (CLOUDFRONT_URL+edited_filename, message)
        cursor.execute(sql, value)
        connection.commit()
        print("Upload Successful")
        return {
          "data": [CLOUDFRONT_URL+edited_filename, message]
        }, 200   
      except:
        return "error"
      finally:
        cursor.close()
        connection.close()
  except FileNotFoundError:
    print("The file was not found")
    return False
  except NoCredentialsError:
    print("Credentials not available")
    return False

# ---------------------------------------------

@app.route("/api/file", methods=["GET"])
def get_message_image():
  try:
    connection = pool.get_connection()
    cursor = connection.cursor()
    sql = """
      SELECT `image_url`, `message` FROM `my_page`
    """
    cursor.execute(sql, )
    dbData = cursor.fetchall()
    dataArray = []
    for data in dbData:
      dataArray.append(data)
    return {
      "data": dataArray
    }, 200
  except:
    return "error"
  finally:
    cursor.close()
    connection.close()
    print("Got File Successfully")



if __name__ == "__main__":
  app.run(port="8080", host="0.0.0.0")