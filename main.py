from mangum import Mangum
from fastapi import FastAPI

from src.controllers.main_controller import router as home_router
from src.config import Config

app = FastAPI(root_path="/api/v1")
app.include_router(home_router, prefix="/poc")

# Health check or root endpoint
@app.get("/")
async def read_root():
    return {"message": "AI Avatar service is running"}


handler = Mangum(app)

# Method to extract reion from lamdba ARN
def _extract_aws_region(arn: str) -> str:
    # Extract AWS region from Lambda function ARN.
    return arn.split(":")[3]

def lambda_handler(event, context):
    print (f"Event = {event}")
    print (f"Context = {context}")

    aws_region = _extract_aws_region(context.invoked_function_arn)

    Config.set_aws_region(aws_region)

    response = handler(event, context)
    return response
